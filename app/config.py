import os

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': 5432,
    'database': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
}

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': 3306,
    'database': os.environ.get('MYSQL_DATABASE'),
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
}

# MongoDB Configuration
MONGO_CONFIG = {
    'host': os.environ.get('MONGO_HOST', 'localhost'),
    'port': 27017,
    'database': os.environ.get('MONGO_INITDB_DATABASE'),
    'user': os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
    'password': os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
}

# Local File Path
LOCAL_FILE_PATH = os.environ.get('LOCAL_FILE_PATH', '/opt/airflow/data/input_file.csv')
