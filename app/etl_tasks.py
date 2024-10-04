import logging
import pandas as pd
import psycopg2
import pymongo
import mysql.connector

from airflow.models import Variable
from config import POSTGRES_CONFIG, MYSQL_CONFIG, MONGO_CONFIG, LOCAL_FILE_PATH

def extract_postgres(**kwargs):
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        query = "SELECT * FROM source_table;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        logging.info("Data extracted from PostgreSQL.")
        return df.to_json(orient='records')
    except Exception as e:
        logging.error(f"Error extracting data from PostgreSQL: {e}")
        return None

def extract_mongodb(**kwargs):
    try:
        mongo_uri = f"mongodb://{MONGO_CONFIG['user']}:{MONGO_CONFIG['password']}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/{MONGO_CONFIG['database']}"
        client = pymongo.MongoClient(mongo_uri)
        db = client[MONGO_CONFIG['database']]
        collection = db['source_collection']
        data = list(collection.find({}, {'_id': 0}))
        df = pd.DataFrame(data)
        client.close()
        logging.info("Data extracted from MongoDB.")
        return df.to_json(orient='records')
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
        return df.to_json(orient='records')
    except Exception as e:
        logging.error(f"Error reading local file: {e}")
        return None

def transform_data(**kwargs):
    ti = kwargs['ti']
    data_list = []
    for task_id in ['extract_postgres', 'extract_mongodb', 'extract_local_file']:
        data = ti.xcom_pull(task_ids=task_id)
        if data:
            df = pd.read_json(data, orient='records')
            data_list.append(df)
    if not data_list:
        logging.warning("No data to transform.")
        return None
    df_combined = pd.concat(data_list, ignore_index=True)
    # Placeholder for data transformation logic
    df_combined.drop_duplicates(inplace=True)
    logging.info("Data transformed.")
    return df_combined.to_json(orient='records')

def load_to_mysql(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_data')
    if not data:
        logging.warning("No data to load into MySQL.")
        return
    try:
        df = pd.read_json(data, orient='records')
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        target_table = Variable.get('target_table', default_var='final_table')
        insert_query = f"INSERT INTO {target_table} (column1, column2) VALUES (%s, %s)"
        data_tuples = df[['column1', 'column2']].values.tolist()
        cursor.executemany(insert_query, data_tuples)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data loaded into MySQL.")
    except Exception as e:
        logging.error(f"Error loading data into MySQL: {e}")
