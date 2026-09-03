"""
Dagster job: Hotel Supply-Chain ETL
====================================
An op-based job that mirrors the Extract -> Transform -> Load stages
defined in the ``common`` package.

Each @op wraps one function from the shared library.  Data flows between
ops as serialised JSON strings (same approach as XCom in the Airflow DAG).

Compare with the Airflow DAG (task-based, explicit XCom passing) to see
how the same logical pipeline looks under two different paradigms.
"""

import logging
from io import StringIO

import dagster as dg
import pandas as pd

from common.logging_utils import (
    LOG_ORIGIN_DAGSTER,
    STAGE_EXTRACT,
    STAGE_LOAD,
    STAGE_PIPELINE,
    STAGE_TRANSFORM,
    configure_logging,
    log_exception,
    log_info,
    log_origin,
)

configure_logging()
logger = logging.getLogger(__name__)


# =====================================================================
# Helpers: consistent serialisation / deserialisation
# =====================================================================

def _df_to_json(df: pd.DataFrame) -> str:
    """Serialise a DataFrame to a JSON string for inter-op transfer.

    Uses ISO date format so datetime columns survive the round-trip.
    """
    return df.to_json(orient="records", date_format="iso")


def _df_from_json(json_str: str) -> pd.DataFrame:
    """Deserialise a JSON string back to a DataFrame.

    Wraps the string in StringIO (required since pandas >= 2.0).
    """
    return pd.read_json(StringIO(json_str), orient="records")


# =====================================================================
# Extract ops
# =====================================================================

@dg.op
def extract_csv(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_csv
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_csv started")
            df = extract_csv()
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_csv produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_csv failed")
            raise


@dg.op
def extract_json(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_json
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_json started")
            df = extract_json()
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_json produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_json failed")
            raise


@dg.op
def extract_mysql_hotels(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_hotels started")
            df = extract_mysql("dim_hotel")
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_hotels produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_mysql_hotels failed")
            raise


@dg.op
def extract_mysql_suppliers(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_suppliers started")
            df = extract_mysql("dim_supplier")
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_suppliers produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_mysql_suppliers failed")
            raise


@dg.op
def extract_mysql_rooms(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_rooms started")
            df = extract_mysql("dim_room")
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mysql_rooms produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_mysql_rooms failed")
            raise


@dg.op
def extract_mongo(context: dg.OpExecutionContext) -> str:
    from common.extract import extract_mongo
    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mongo started")
            df = extract_mongo("supplier_contracts")
            log_info(logger, STAGE_EXTRACT, "Dagster op extract_mongo produced %d rows", len(df))
            return _df_to_json(df)
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Dagster op extract_mongo failed")
            raise


# =====================================================================
# Transform op
# =====================================================================

@dg.op
def transform(
        context: dg.OpExecutionContext,
        supply_orders_json: str,
        housekeeping_json: str,
        dim_hotel_json: str,
        dim_supplier_json: str,
        dim_room_json: str,
        contracts_json: str,
) -> str:
    from common.transform import build_fact_table

    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_TRANSFORM, "Dagster op transform started")
            supply_orders = _df_from_json(supply_orders_json)
            housekeeping = _df_from_json(housekeeping_json)
            dim_hotel = _df_from_json(dim_hotel_json)
            dim_supplier = _df_from_json(dim_supplier_json)
            dim_room = _df_from_json(dim_room_json)
            contracts = _df_from_json(contracts_json)

            result = build_fact_table(
                supply_orders, housekeeping, dim_hotel, dim_supplier, dim_room, contracts,
            )
            log_info(logger, STAGE_TRANSFORM, "Dagster op transform produced %d fact rows", len(result))
            return _df_to_json(result)
        except Exception:
            log_exception(logger, STAGE_TRANSFORM, "Dagster op transform failed")
            raise


# =====================================================================
# Load op
# =====================================================================

@dg.op
def load(context: dg.OpExecutionContext, fact_table_json: str) -> int:
    from common.load import load_to_postgres

    with log_origin(LOG_ORIGIN_DAGSTER):
        try:
            log_info(logger, STAGE_LOAD, "Dagster op load started")
            df = _df_from_json(fact_table_json)
            rows = load_to_postgres(df)
            log_info(logger, STAGE_LOAD, "Dagster op load wrote %d rows to PostgreSQL", rows)
            return rows
        except Exception:
            log_exception(logger, STAGE_LOAD, "Dagster op load failed")
            raise


# =====================================================================
# Job definition
# =====================================================================

@dg.job(
    description="Extract from CSV/JSON/MySQL/MongoDB, transform, load to PostgreSQL",
    executor_def=dg.in_process_executor,
    tags={"etl-demo": "hotel"},
)
def hotel_supply_etl():
    csv_data       = extract_csv()
    json_data      = extract_json()
    hotels         = extract_mysql_hotels()
    suppliers      = extract_mysql_suppliers()
    rooms          = extract_mysql_rooms()
    mongo_data     = extract_mongo()

    fact_table = transform(
        supply_orders_json=csv_data,
        housekeeping_json=json_data,
        dim_hotel_json=hotels,
        dim_supplier_json=suppliers,
        dim_room_json=rooms,
        contracts_json=mongo_data,
    )
    load(fact_table)


# =====================================================================
# Definitions entry point (Dagster discovers this via workspace.yaml)
# =====================================================================

defs = dg.Definitions(jobs=[hotel_supply_etl])

with log_origin(LOG_ORIGIN_DAGSTER):
    log_info(logger, STAGE_PIPELINE, "Dagster job hotel_supply_etl loaded")
