import pandas as pd
import urllib.parse  # Needed for URL encoding the connection string for MS SQL Server
from sqlalchemy import create_engine


class DatabaseHelper:
    def __init__(self):
        self.engines = {}

    def connect_mysql(self, host, port, user, password, db):
        db_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        try:
            self.engines['mysql'] = create_engine(db_uri)
        except Exception as e:
            print(f"Failed to connect to MySQL database: {e}")

    def connect_mssql(self, host, user, password, db):
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={host};DATABASE={db};UID={user};PWD={password};"
        )
        try:
            self.engines['mssql'] = create_engine(f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(conn_str)}')
        except Exception as e:
            print(f"Failed to connect to MS SQL database: {e}")

    def read_from_db(self, db_type, query):
        engine = self.engines.get(db_type)
        if engine:
            try:
                return pd.read_sql_query(query, engine)
            except Exception as e:
                print(f"Failed to read from {db_type} database: {e}")
        else:
            print(f"No connection to {db_type} database")
            return None

    def write_to_db(self, db_type, df, table_name, if_exists='replace'):
        engine = self.engines.get(db_type)
        if engine:
            try:
                df.to_sql(table_name, engine, if_exists=if_exists, index=False)
            except Exception as e:
                print(f"Failed to write to {db_type} database: {e}")
        else:
            print(f"No connection to {db_type} database")
