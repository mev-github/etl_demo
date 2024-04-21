import logging

from common.db_manager import DatabaseManager


class DataWriter:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataWriter initialized")

    def write_data(self, df, destination_type, destination_format, destination_name) -> None:
        self.logger.info(f"Writing data to {destination_type}: {destination_name}")
        if destination_type == 'file':
            self._write_file(df, destination_format, destination_name)
        elif destination_type == 'table':
            self._write_db(df, destination_format, destination_name)
        else:
            raise ValueError(f"Unsupported destination type: {destination_type}")

    def _write_file(self, df, file_extension, file_path) -> None:
        file_extension = file_extension.lower()
        write_functions = {
            'csv': lambda df, path: df.to_csv(path, index=False),
            'json': lambda df, path: df.to_json(path),
            'parquet': lambda df, path: df.to_parquet(path)
        }
        if file_extension not in write_functions:
            raise ValueError(f"Unsupported file format: {file_extension}")
        try:
            write_functions[file_extension](df, file_path)
        except Exception as e:
            self.logger.error(f"Failed to write to file {file_path}: {e}")
            raise

    def _write_db(self, df, db_type, table_name) -> None:
        engine = self.db_manager.create_engine(db_type)
        try:
            df.to_sql(table_name, engine, if_exists='replace', index=False)
        except Exception as e:
            self.logger.error(f"Failed to write to database {db_type}: {e}")
            raise
