"""
Load stage: write the transformed DataFrame into PostgreSQL.

Uses pandas ``to_sql`` with ``if_exists='append'`` for simplicity.
No upsert, no deduplication.  Each pipeline run appends a new batch.
"""

import logging

import pandas as pd
from sqlalchemy import create_engine

from common.config import (
    PG_DATABASE,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_SCHEMA,
    PG_TARGET_TABLE,
    PG_USER,
)
from common.logging_utils import STAGE_LOAD, configure_logging, log_info

configure_logging()
logger = logging.getLogger(__name__)


def load_to_postgres(df: pd.DataFrame) -> int:
    """Append *df* to the target table and return the number of rows written."""
    url = (
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}"
        f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    )
    engine = create_engine(url)
    log_info(
        logger,
        STAGE_LOAD,
        "Loading %d rows into %s.%s on %s:%s",
        len(df),
        PG_SCHEMA,
        PG_TARGET_TABLE,
        PG_HOST,
        PG_PORT,
    )
    df.to_sql(
        name=PG_TARGET_TABLE,
        con=engine,
        schema=PG_SCHEMA,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
    log_info(logger, STAGE_LOAD, "Load completed with %d rows written", len(df))
    return len(df)
