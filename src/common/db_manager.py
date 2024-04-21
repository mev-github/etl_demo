import logging

import yaml
from sqlalchemy import create_engine, Engine


class DatabaseManager:
    def __init__(self, config_path='config/data_connection_config.yaml'):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        self.logger.info("DatabaseManager initialized")

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def create_engine(self, db_type=None) -> Engine:
        self.logger.info(f"Creating database engine for {db_type}")
        db_string = self._create_db_string(db_type)
        return create_engine(db_string)

    def _create_db_string(self, db_type) -> str:
        if db_type is None:
            db_type = 'mysql'

        if db_type not in self.config:
            raise ValueError(f"Unsupported or undefined database type: {db_type}")

        db_config = self.config[db_type]

        if db_type == 'mssql':
            return f"mssql+pyodbc://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?driver={db_config['driver']}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        elif db_type == 'postgresql':
            return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
