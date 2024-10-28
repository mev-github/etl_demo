import logging
import os

import pandas as pd
import pymongo
import uuid_utils as uuid
from airflow.models import Variable
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from config import POSTGRES_CONFIG, MYSQL_CONFIG, MONGO_CONFIG, LOCAL_FILE_PATH


def extract_postgres(**kwargs):
    try:
        source_table = Variable.get('postgres_source_table', default_var='source_table')

        # Create SQLAlchemy engine for PostgreSQL
        postgres_url = URL.create(
            drivername='postgresql+psycopg2',
            username=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            database=POSTGRES_CONFIG['database']
        )
        engine = create_engine(postgres_url)

        query = f"SELECT * FROM {source_table};"
        df = pd.read_sql_query(query, engine)
        logging.info("Data extracted from PostgreSQL.")

        # Generate a unique file path
        execution_date = kwargs['execution_date'].strftime('%Y%m%dT%H%M%S')
        file_path = f'/tmp/postgres_data_{execution_date}.csv'
        df.to_csv(file_path, index=False)
        return file_path
    except Exception as e:
        logging.error(f"Error extracting data from PostgreSQL: {e}")
        return None


def extract_mongodb(**kwargs):
    try:
        collection_name = Variable.get('mongodb_source_collection', default_var='source_collection')
        mongo_uri = f"mongodb://{MONGO_CONFIG['user']}:{MONGO_CONFIG['password']}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}"
        client = pymongo.MongoClient(mongo_uri)
        db = client[MONGO_CONFIG['database']]
        collection = db[collection_name]
        data = list(collection.find({}, {'_id': 0}))
        df = pd.DataFrame(data)
        client.close()
        logging.info("Data extracted from MongoDB.")

        # Save DataFrame to a CSV file
        execution_date = kwargs['execution_date'].strftime('%Y%m%dT%H%M%S')
        file_path = f'/tmp/mongodb_data_{execution_date}.csv'
        df.to_csv(file_path, index=False)
        return file_path
    except Exception as e:
        logging.error(f"Error extracting data from MongoDB: {e}")
        return None


def extract_local_file(**kwargs):
    try:
        if LOCAL_FILE_PATH.endswith('.csv'):
            df = pd.read_csv(LOCAL_FILE_PATH)
        elif LOCAL_FILE_PATH.endswith('.json'):
            df = pd.read_json(LOCAL_FILE_PATH, lines=True)
        else:
            logging.error("Unsupported file format: " + LOCAL_FILE_PATH)
            return None
        logging.info("Data extracted from local file.")

        # Save DataFrame to a CSV file
        execution_date = kwargs['execution_date'].strftime('%Y%m%dT%H%M%S')
        file_path = f'/tmp/local_file_data_{execution_date}.csv'
        df.to_csv(file_path, index=False)
        return file_path
    except Exception as e:
        logging.error(f"Error reading local file: {e}")
        return None


def transform_data(extract_task_ids, **kwargs):
    ti = kwargs['ti']
    file_paths = []
    for task_id in extract_task_ids:
        file_path = ti.xcom_pull(task_ids=task_id)
        if file_path:
            file_paths.append(file_path)
    if not file_paths:
        logging.warning("No data files to transform.")
        return None

    data_frames = []
    try:
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            logging.info(f"Current DataFrame 6 rows:\n{df.head(6)}")
            data_frames.append(df)

        df_combined = pd.concat(data_frames, ignore_index=True)
        logging.info(f"Combined DataFrame 6 rows:\n{df_combined.head(6)}")

        # Data transformation logic
        df_combined.drop_duplicates(inplace=True)

        # Remove 'id' column if it exists
        if 'id' in df_combined.columns:
            df_combined.drop(columns=['id'], inplace=True)

        # Generate UUID version 7 strings for each row and assign to 'id' column
        df_combined['meta_id'] = [str(uuid.uuid7()) for _ in range(len(df_combined))]
        logging.info(f"Combined DataFrame 6 rows with meta_id:\n{df_combined.head(6)}")

        logging.info("Data transformed.")

        # Save the transformed data to a file
        execution_date = kwargs['execution_date'].strftime('%Y%m%dT%H%M%S')
        transformed_file_path = f'/tmp/transformed_data_{execution_date}.csv'
        df_combined.to_csv(transformed_file_path, index=False)
        return transformed_file_path
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise e
    finally:
        # Clean up the temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)


def load_to_mysql(**kwargs):
    ti = kwargs['ti']
    transformed_file_path = ti.xcom_pull(task_ids='transform_data')
    if not transformed_file_path:
        logging.warning("No transformed data file to load into MySQL.")
        return
    try:
        df = pd.read_csv(transformed_file_path)

        # Create a SQLAlchemy engine to manage the connection
        mysql_url = URL.create(
            drivername='mysql+mysqlconnector',
            username=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            database=MYSQL_CONFIG['database']
        )
        engine = create_engine(mysql_url)

        # Insert data into the MySQL table using SQLAlchemy
        target_table = Variable.get('target_table', default_var='final_table')
        df.to_sql(name=target_table, con=engine, if_exists='append', index=False)
        logging.info("Data loaded into MySQL using SQLAlchemy.")
    except Exception as e:
        logging.error(f"Error loading data into MySQL: {e}")
        raise e
    finally:
        # Clean up the temporary file
        if os.path.exists(transformed_file_path):
            os.remove(transformed_file_path)
