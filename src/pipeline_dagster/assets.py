"""
Dagster assets: Hotel Supply-Chain ETL
=======================================
An asset-based pipeline.  Each ``@asset`` function produces a named data
artifact.  Dagster tracks lineage automatically: downstream assets declare
their dependencies via parameter names that match upstream asset keys.

Compare with the Airflow DAG (task-based, explicit XCom passing) to see
how the same logical pipeline looks under two different paradigms.
"""

import logging

import pandas as pd
from dagster import (
    AssetExecutionContext,
    Definitions,
    asset,
)

from common.logging_utils import (
    LOG_ORIGIN_DAGSTER,
    STAGE_EXTRACT,
    STAGE_LOAD,
    STAGE_PIPELINE,
    STAGE_TRANSFORM,
    configure_logging,
    log_origin,
    tagged_message,
)

configure_logging()
logger = logging.getLogger(__name__)


# =====================================================================
# Extract assets
# =====================================================================

@asset(group_name="extract", description="Supply orders from CSV (fact table)")
def supply_orders(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_csv
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset supply_orders started"))
        df = extract_csv()
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset supply_orders produced %d rows"), len(df))
        return df


@asset(group_name="extract", description="Housekeeping log from JSON (events)")
def housekeeping(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_json
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset housekeeping started"))
        df = extract_json()
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset housekeeping produced %d rows"), len(df))
        return df


@asset(group_name="extract", description="Hotel dimension table from MySQL")
def dim_hotel(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_hotel started"))
        df = extract_mysql("dim_hotel")
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_hotel produced %d rows"), len(df))
        return df


@asset(group_name="extract", description="Supplier dimension table from MySQL")
def dim_supplier(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_supplier started"))
        df = extract_mysql("dim_supplier")
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_supplier produced %d rows"), len(df))
        return df


@asset(group_name="extract", description="Room dimension table from MySQL")
def dim_room(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_room started"))
        df = extract_mysql("dim_room")
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset dim_room produced %d rows"), len(df))
        return df


@asset(group_name="extract", description="Supplier contracts from MongoDB (enrichment)")
def contracts(context: AssetExecutionContext) -> pd.DataFrame:
    from common.extract import extract_mongo
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset contracts started"))
        df = extract_mongo("supplier_contracts")
        context.log.info(tagged_message(STAGE_EXTRACT, "Dagster asset contracts produced %d rows"), len(df))
        return df


# =====================================================================
# Transform asset
# =====================================================================

@asset(
    group_name="transform",
    description="Joined and enriched fact table, ready for warehouse load",
)
def fact_hotel_operations(
    context: AssetExecutionContext,
    supply_orders: pd.DataFrame,
    housekeeping: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_supplier: pd.DataFrame,
    dim_room: pd.DataFrame,
    contracts: pd.DataFrame,
) -> pd.DataFrame:
    from common.transform import build_fact_table
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_TRANSFORM, "Dagster asset fact_hotel_operations started"))
        df = build_fact_table(
            supply_orders, housekeeping, dim_hotel, dim_supplier, dim_room, contracts,
        )
        context.log.info(tagged_message(STAGE_TRANSFORM, "Dagster asset fact_hotel_operations produced %d rows"), len(df))
        return df


# =====================================================================
# Load asset
# =====================================================================

@asset(
    group_name="load",
    description="Write fact table to PostgreSQL warehouse",
)
def warehouse_loaded(
    context: AssetExecutionContext,
    fact_hotel_operations: pd.DataFrame,
) -> int:
    from common.load import load_to_postgres
    with log_origin(LOG_ORIGIN_DAGSTER):
        context.log.info(tagged_message(STAGE_LOAD, "Dagster asset warehouse_loaded started"))
        rows = load_to_postgres(fact_hotel_operations)
        context.log.info(tagged_message(STAGE_LOAD, "Dagster asset warehouse_loaded loaded %d rows"), rows)
        return rows


# =====================================================================
# Definitions entry point (Dagster discovers this automatically)
# =====================================================================

defs = Definitions(
    assets=[
        supply_orders,
        housekeeping,
        dim_hotel,
        dim_supplier,
        dim_room,
        contracts,
        fact_hotel_operations,
        warehouse_loaded,
    ],
)

with log_origin(LOG_ORIGIN_DAGSTER):
    logger.info(tagged_message(STAGE_PIPELINE, "Dagster definitions loaded"))
