"""
Centralised configuration for the ETL pipeline.

All connection strings read from environment variables so the same code
works both inside Docker and (optionally) on a bare host.
"""

import os

# ---------- source: CSV / JSON paths ----------
DATA_DIR = os.getenv("ETL_DATA_DIR", "/opt/etl/data")
CSV_PATH = os.path.join(DATA_DIR, "supply_orders.csv")
JSON_PATH = os.path.join(DATA_DIR, "housekeeping_log.json")

# ---------- source: MySQL (dimension tables) ----------
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "etl_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "etl_pass")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "hotel_dims")

# ---------- source: MongoDB (enrichment) ----------
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_USER", "etl_user")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "etl_pass")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "hotel_enrichment")

# ---------- target: PostgreSQL ----------
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_USER = os.getenv("PG_USER", "etl_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "etl_pass")
PG_DATABASE = os.getenv("PG_DATABASE", "hotel_dwh")
PG_SCHEMA = os.getenv("PG_SCHEMA", "dwh")
PG_TARGET_TABLE = os.getenv("PG_TARGET_TABLE", "fact_hotel_operations")
