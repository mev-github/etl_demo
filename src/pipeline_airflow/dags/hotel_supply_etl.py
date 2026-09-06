"""
Airflow DAG: Hotel Supply-Chain ETL
====================================
A classic task-based DAG that mirrors the Extract -> Transform -> Load
stages defined in the ``common`` package.

Each PythonOperator wraps one function from the shared library.
Intermediate data is passed between tasks via XCom (serialised as JSON).
This is acceptable for the small seed dataset; production pipelines would
use a staging area instead.
"""

import logging
from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from common.logging_utils import (
    LOG_ORIGIN_AIRFLOW,
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


# ---------------------------------------------------------------------------
# Task callables
# ---------------------------------------------------------------------------

def _extract_csv(**ctx):
    from common.extract import extract_csv
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_csv started")
            df = extract_csv()
            ctx["ti"].xcom_push(key="supply_orders", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_csv pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_csv failed")
            raise


def _extract_json(**ctx):
    from common.extract import extract_json
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_json started")
            df = extract_json()
            ctx["ti"].xcom_push(key="housekeeping", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_json pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_json failed")
            raise


def _extract_mysql_hotels(**ctx):
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_hotels started")
            df = extract_mysql("dim_hotel")
            ctx["ti"].xcom_push(key="dim_hotel", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_hotels pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_mysql_hotels failed")
            raise


def _extract_mysql_suppliers(**ctx):
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_suppliers started")
            df = extract_mysql("dim_supplier")
            ctx["ti"].xcom_push(key="dim_supplier", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_suppliers pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_mysql_suppliers failed")
            raise


def _extract_mysql_rooms(**ctx):
    from common.extract import extract_mysql
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_rooms started")
            df = extract_mysql("dim_room")
            ctx["ti"].xcom_push(key="dim_room", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mysql_rooms pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_mysql_rooms failed")
            raise


def _extract_mongo(**ctx):
    from common.extract import extract_mongo
    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mongo started")
            df = extract_mongo("supplier_contracts")
            ctx["ti"].xcom_push(key="contracts", value=df.to_json(orient="records"))
            log_info(logger, STAGE_EXTRACT, "Airflow task extract_mongo pushed %d rows to XCom", len(df))
        except Exception:
            log_exception(logger, STAGE_EXTRACT, "Airflow task extract_mongo failed")
            raise


def _transform(**ctx):
    import pandas as pd
    from common.transform import build_fact_table

    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_TRANSFORM, "Airflow task transform started")
            ti = ctx["ti"]
            supply_orders = pd.read_json(ti.xcom_pull(task_ids="extract_csv", key="supply_orders"), orient="records")
            housekeeping = pd.read_json(ti.xcom_pull(task_ids="extract_json", key="housekeeping"), orient="records")
            dim_hotel = pd.read_json(ti.xcom_pull(task_ids="extract_mysql_hotels", key="dim_hotel"), orient="records")
            dim_supplier = pd.read_json(ti.xcom_pull(task_ids="extract_mysql_suppliers", key="dim_supplier"),
                                        orient="records")
            dim_room = pd.read_json(ti.xcom_pull(task_ids="extract_mysql_rooms", key="dim_room"), orient="records")
            contracts = pd.read_json(ti.xcom_pull(task_ids="extract_mongo", key="contracts"), orient="records")

            result = build_fact_table(
                supply_orders, housekeeping, dim_hotel, dim_supplier, dim_room, contracts,
            )
            ti.xcom_push(key="fact_table", value=result.to_json(orient="records", date_format="iso"))
            log_info(logger, STAGE_TRANSFORM, "Airflow task transform pushed %d rows to XCom", len(result))
        except Exception:
            log_exception(logger, STAGE_TRANSFORM, "Airflow task transform failed")
            raise


def _load(**ctx):
    import pandas as pd
    from common.load import load_to_postgres

    with log_origin(LOG_ORIGIN_AIRFLOW):
        try:
            log_info(logger, STAGE_LOAD, "Airflow task load started")
            ti = ctx["ti"]
            df = pd.read_json(ti.xcom_pull(task_ids="transform", key="fact_table"), orient="records")
            rows = load_to_postgres(df)
            ti.xcom_push(key="rows_loaded", value=rows)
            log_info(logger, STAGE_LOAD, "Airflow task load pushed rows_loaded=%d to XCom", rows)
        except Exception:
            log_exception(logger, STAGE_LOAD, "Airflow task load failed")
            raise


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------

default_args = {
    "owner": "etl-demo",
    "retries": 0,  # fail fast for teaching purposes
    "retry_delay": timedelta(minutes=1),
}

with DAG(
        dag_id="hotel_supply_etl",
        default_args=default_args,
        description="Extract from CSV/JSON/MySQL/MongoDB, transform, load to PostgreSQL",
        schedule=None,  # manual trigger only
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["etl-demo", "hotel"],
) as dag:
    with log_origin(LOG_ORIGIN_AIRFLOW):
        log_info(logger, STAGE_PIPELINE, "Airflow DAG hotel_supply_etl loaded")

    extract_csv_task = PythonOperator(task_id="extract_csv", python_callable=_extract_csv)
    extract_json_task = PythonOperator(task_id="extract_json", python_callable=_extract_json)
    extract_hotels_task = PythonOperator(task_id="extract_mysql_hotels", python_callable=_extract_mysql_hotels)
    extract_suppliers_task = PythonOperator(task_id="extract_mysql_suppliers", python_callable=_extract_mysql_suppliers)
    extract_rooms_task = PythonOperator(task_id="extract_mysql_rooms", python_callable=_extract_mysql_rooms)
    extract_mongo_task = PythonOperator(task_id="extract_mongo", python_callable=_extract_mongo)

    transform_task = PythonOperator(task_id="transform", python_callable=_transform)
    load_task = PythonOperator(task_id="load", python_callable=_load)

    # All extracts must finish before transform begins.
    [
        extract_csv_task,
        extract_json_task,
        extract_hotels_task,
        extract_suppliers_task,
        extract_rooms_task,
        extract_mongo_task,
    ] >> transform_task >> load_task
