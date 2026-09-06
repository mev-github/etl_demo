"""
Transform stage: join sources, apply business logic, add metadata.

The main entry point is ``build_fact_table()``.  It calls helper functions
for each logical sub-step.  Students modify ``apply_business_logic()``
and ``classify_event_type()`` to match their own domain.  Everything
else should be left as-is.
"""

import logging
import uuid
from datetime import datetime, timezone

import pandas as pd

from common.logging_utils import STAGE_TRANSFORM, configure_logging, log_info

configure_logging()
logger = logging.getLogger(__name__)


# =====================================================================
# Public entry point
# =====================================================================

def build_fact_table(
    supply_orders: pd.DataFrame,
    housekeeping: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_supplier: pd.DataFrame,
    dim_room: pd.DataFrame,
    contracts: pd.DataFrame,
) -> pd.DataFrame:
    """Assemble the final fact table from all extracted sources.

    Parameters
    ----------
    supply_orders : DataFrame from CSV (fact)
    housekeeping  : DataFrame from JSON (fact / events)
    dim_hotel     : DataFrame from MySQL
    dim_supplier  : DataFrame from MySQL
    dim_room      : DataFrame from MySQL
    contracts     : DataFrame from MongoDB

    Returns
    -------
    DataFrame ready for loading into PostgreSQL.
    """
    batch_id = str(uuid.uuid4())
    batch_ts = datetime.now(timezone.utc)
    log_info(
        logger,
        STAGE_TRANSFORM,
        "Transform started with batch_id=%s batch_ts=%s",
        batch_id,
        batch_ts,
    )
    log_info(
        logger,
        STAGE_TRANSFORM,
        "Input sizes supply_orders=%d housekeeping=%d dim_hotel=%d dim_supplier=%d dim_room=%d contracts=%d",
        len(supply_orders),
        len(housekeeping),
        len(dim_hotel),
        len(dim_supplier),
        len(dim_room),
        len(contracts),
    )

    # Step 1 -- join supply orders with dimensions and contracts
    orders_enriched = _join_supply_orders(supply_orders, dim_hotel, dim_supplier, contracts)

    # Step 2 -- join housekeeping with dimensions
    hk_enriched = _join_housekeeping(housekeeping, dim_hotel, dim_room)

    # Step 3 -- apply student business logic
    orders_enriched = apply_business_logic(orders_enriched)
    hk_enriched = apply_business_logic(hk_enriched)

    # Step 4 -- classify event types
    orders_enriched["event_type"] = orders_enriched.apply(
        lambda row: classify_event_type(row, source="supply"), axis=1
    )
    hk_enriched["event_type"] = hk_enriched.apply(
        lambda row: classify_event_type(row, source="housekeeping"), axis=1
    )

    # Step 5 -- unify into a single frame with the target schema
    result = _unify_schema(orders_enriched, hk_enriched)

    # Step 6 -- stamp metadata
    result["batch_id"] = batch_id
    result["batch_ts"] = batch_ts

    log_info(
        logger,
        STAGE_TRANSFORM,
        "Transform completed with %d output rows and columns %s",
        len(result),
        list(result.columns),
    )
    return result


# =====================================================================
# TODO: Student-editable functions
# =====================================================================

def apply_business_logic(df: pd.DataFrame) -> pd.DataFrame:
    """Apply domain-specific transformations.

    TODO (student): modify this function for your own dataset.
    -------------------------------------------------------
    Example ideas for the hotel supply demo:
      - Calculate ``final_price`` using the discount from the contract.
      - Flag orders that exceed the contracted delivery SLA.
      - Normalise duration_minutes into a categorical column
        (e.g. "quick" / "normal" / "long").

    The default implementation below computes ``final_price`` for supply
    orders using the discount_pct column (populated by the join step).
    For housekeeping rows the column is absent, so nothing happens.
    """
    if "unit_price" in df.columns and "discount_pct" in df.columns:
        log_info(logger, STAGE_TRANSFORM, "Applying default pricing logic to %d rows", len(df))
        df["discount_pct"] = df["discount_pct"].fillna(0)
        df["final_price"] = (
            df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
        ).round(2)
    else:
        log_info(logger, STAGE_TRANSFORM, "Skipping default pricing logic for %d rows", len(df))
    return df


def classify_event_type(row: pd.Series, source: str) -> str:
    """Return an event_type string for a single row.

    TODO (student): adjust classification rules for your domain.
    -----------------------------------------------------------
    Default rules for the hotel supply demo:
      - supply + is_urgent == True  -> "supply_order_urgent"
      - supply + is_urgent == False -> "supply_order_standard"
      - housekeeping + status "incident" -> "housekeeping_incident"
      - housekeeping + status "deferred" -> "housekeeping_deferred"
      - housekeeping + otherwise         -> "housekeeping_completed"
    """
    if source == "supply":
        if row.get("is_urgent") in (True, "true", "True"):
            return "supply_order_urgent"
        return "supply_order_standard"

    if source == "housekeeping":
        status = str(row.get("status", "")).lower()
        if status == "incident":
            return "housekeeping_incident"
        if status == "deferred":
            return "housekeeping_deferred"
        return "housekeeping_completed"

    return "unknown"


# =====================================================================
# Internal helpers (students do NOT need to change these)
# =====================================================================

def _join_supply_orders(
    orders: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_supplier: pd.DataFrame,
    contracts: pd.DataFrame,
) -> pd.DataFrame:
    """Enrich supply orders with hotel, supplier, and contract data."""
    log_info(logger, STAGE_TRANSFORM, "Joining supply orders with hotel, supplier, and contract data")
    df = orders.merge(
        dim_hotel[["hotel_id", "name", "city"]],
        on="hotel_id",
        how="left",
    ).rename(columns={"name": "hotel_name"})

    df = df.merge(
        dim_supplier[["supplier_id", "name"]],
        on="supplier_id",
        how="left",
    ).rename(columns={"name": "supplier_name"})

    # Flatten volume discounts: pick the highest applicable tier
    discount_map = _build_discount_map(contracts)
    df["discount_pct"] = df.apply(
        lambda r: _lookup_discount(discount_map, r["supplier_id"], r["quantity"]),
        axis=1,
    )

    # Carry source event id
    df = df.rename(columns={"order_id": "source_event_id"})
    log_info(logger, STAGE_TRANSFORM, "Supply order join completed with %d rows", len(df))
    return df


def _join_housekeeping(
    hk: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_room: pd.DataFrame,
) -> pd.DataFrame:
    """Enrich housekeeping events with hotel and room data."""
    log_info(logger, STAGE_TRANSFORM, "Joining housekeeping events with hotel and room data")
    df = hk.merge(
        dim_hotel[["hotel_id", "name", "city"]],
        on="hotel_id",
        how="left",
    ).rename(columns={"name": "hotel_name"})

    df = df.merge(
        dim_room[["room_id", "room_type"]],
        on="room_id",
        how="left",
    )

    df = df.rename(columns={
        "event_id": "source_event_id",
        "status": "hk_status",
        "notes": "hk_notes",
    })
    log_info(logger, STAGE_TRANSFORM, "Housekeeping join completed with %d rows", len(df))
    return df


def _build_discount_map(contracts: pd.DataFrame) -> dict:
    """Parse contracts into {supplier_id: [(min_qty, discount_pct), ...]}."""
    log_info(logger, STAGE_TRANSFORM, "Building discount map from %d contract rows", len(contracts))
    result = {}
    for _, row in contracts.iterrows():
        sid = row["supplier_id"]
        terms = row.get("terms", {})
        if isinstance(terms, dict):
            tiers = terms.get("volume_discounts", [])
        else:
            tiers = []
        # Sort descending by min_quantity so first match wins
        sorted_tiers = sorted(tiers, key=lambda t: t["min_quantity"], reverse=True)
        result[sid] = [(t["min_quantity"], t["discount_pct"]) for t in sorted_tiers]
    log_info(logger, STAGE_TRANSFORM, "Discount map built for %d suppliers", len(result))
    return result


def _lookup_discount(discount_map: dict, supplier_id: str, quantity) -> float:
    """Find the best discount tier for a given supplier and quantity."""
    tiers = discount_map.get(supplier_id, [])
    for min_qty, pct in tiers:
        if quantity >= min_qty:
            return pct
    return 0.0


def _unify_schema(orders: pd.DataFrame, hk: pd.DataFrame) -> pd.DataFrame:
    """Combine the two enriched frames into the target table schema.

    Missing columns in either frame are filled with None.
    """
    target_cols = [
        "event_type",
        "source_event_id",
        "hotel_id",
        "hotel_name",
        "city",
        "supplier_id",
        "supplier_name",
        "item_category",
        "item_description",
        "quantity",
        "unit_price",
        "discount_pct",
        "final_price",
        "room_id",
        "room_type",
        "hk_status",
        "duration_minutes",
        "hk_notes",
    ]

    for col in target_cols:
        if col not in orders.columns:
            orders[col] = None
        if col not in hk.columns:
            hk[col] = None

    combined = pd.concat([orders[target_cols], hk[target_cols]], ignore_index=True)
    log_info(logger, STAGE_TRANSFORM, "Unified schema prepared with %d combined rows", len(combined))
    return combined
