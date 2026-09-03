"""
Extract stage: read data from all four sources into pandas DataFrames.

Each function returns a plain DataFrame.  No transformation logic belongs here.
"""

import json
import logging

import pandas as pd
import pymysql
from pymongo import MongoClient

from common.config import (
    CSV_PATH,
    JSON_PATH,
    MONGO_DATABASE,
    MONGO_HOST,
    MONGO_PASSWORD,
    MONGO_PORT,
    MONGO_USER,
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)
from common.logging_utils import STAGE_EXTRACT, configure_logging, log_info

configure_logging()
logger = logging.getLogger(__name__)


def extract_csv() -> pd.DataFrame:
    """Read the supply-orders fact table from a CSV file."""
    log_info(logger, STAGE_EXTRACT, "Reading CSV source from %s", CSV_PATH)
    df = pd.read_csv(CSV_PATH)
    log_info(
        logger,
        STAGE_EXTRACT,
        "CSV extraction completed with %d rows and columns %s",
        len(df),
        list(df.columns),
    )
    return df


def extract_json() -> pd.DataFrame:
    """Read the housekeeping log from a JSON file."""
    log_info(logger, STAGE_EXTRACT, "Reading JSON source from %s", JSON_PATH)
    with open(JSON_PATH, "r") as fh:
        records = json.load(fh)
    df = pd.DataFrame(records)
    log_info(
        logger,
        STAGE_EXTRACT,
        "JSON extraction completed with %d rows and columns %s",
        len(df),
        list(df.columns),
    )
    return df


def extract_mysql(table: str) -> pd.DataFrame:
    """Read a single dimension table from MySQL."""
    log_info(
        logger,
        STAGE_EXTRACT,
        "Reading MySQL table %s.%s from %s:%s",
        MYSQL_DATABASE,
        table,
        MYSQL_HOST,
        MYSQL_PORT,
    )
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)  # noqa: S608
        log_info(logger, STAGE_EXTRACT, "MySQL extraction completed for %s with %d rows", table, len(df))
        return df
    finally:
        conn.close()


def extract_mongo(collection_name: str) -> pd.DataFrame:
    """Read a MongoDB collection into a DataFrame.

    Nested documents are kept as dicts inside DataFrame cells.  The
    transform stage is responsible for flattening what it needs.
    """
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    log_info(
        logger,
        STAGE_EXTRACT,
        "Reading MongoDB collection %s.%s from %s:%s",
        MONGO_DATABASE,
        collection_name,
        MONGO_HOST,
        MONGO_PORT,
    )
    client = MongoClient(uri)
    try:
        db = client[MONGO_DATABASE]
        docs = list(db[collection_name].find({}, {"_id": 0}))
        df = pd.DataFrame(docs)
        log_info(
            logger,
            STAGE_EXTRACT,
            "MongoDB extraction completed for %s with %d documents",
            collection_name,
            len(df),
        )
        return df
    finally:
        client.close()
