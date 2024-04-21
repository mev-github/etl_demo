import logging

import pandas as pd

from common.db_manager import DatabaseManager


class DataReader:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataReader initialized")

    def read_data(self, source_type, source_format, source_name) -> pd.DataFrame:
        self.logger.info(f"Reading data from {source_type}: {source_name}")
        if source_type == 'file':
            return self._read_file(source_format, source_name)
        elif source_type == 'table':
            return self._read_db(source_format, source_name)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def _read_file(self, file_extension, file_path) -> pd.DataFrame:
        file_extension = file_extension.lower()
        read_functions = {
            'csv': pd.read_csv,
            'json': pd.read_json,
            'parquet': pd.read_parquet
        }
        if file_extension not in read_functions:
            raise ValueError(f"Unsupported file format: {file_extension}")
        return read_functions[file_extension](file_path)

    def _read_db(self, db_type, table_name) -> pd.DataFrame:
        engine = self.db_manager.create_engine(db_type)
        try:
            return pd.read_sql_table(table_name, engine)
        except Exception as e:
            self.logger.error(f"Failed to read from database {db_type}: {e}")
            raise
