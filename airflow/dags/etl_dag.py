from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from app.etl_tasks import extract_postgres, extract_mongodb, extract_local_file, transform_data, load_to_mysql

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    schedule_interval=None,  # Set to None or desired schedule
    catchup=False,
)

read_postgres = Variable.get("read_postgres", default_var="True") == "True"
read_mongodb = Variable.get("read_mongodb", default_var="True") == "True"
read_file = Variable.get("read_file", default_var="False") == "True"

extract_tasks = []

if read_postgres:
    extract_postgres_task = PythonOperator(
        task_id='extract_postgres',
        python_callable=extract_postgres,
        dag=dag,
    )
    extract_tasks.append(extract_postgres_task)

if read_mongodb:
    extract_mongodb_task = PythonOperator(
        task_id='extract_mongodb',
        python_callable=extract_mongodb,
        dag=dag,
    )
    extract_tasks.append(extract_mongodb_task)

if read_file:
    extract_file_task = PythonOperator(
        task_id='extract_local_file',
        python_callable=extract_local_file,
        dag=dag,
    )
    extract_tasks.append(extract_file_task)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_mysql',
    python_callable=load_to_mysql,
    dag=dag,
)

# Define task dependencies
if extract_tasks:
    for extract_task in extract_tasks:
        extract_task >> transform_task
    transform_task >> load_task
else:
    from airflow.operators.dummy import DummyOperator
    skip_task = DummyOperator(task_id='skip_task', dag=dag)
    skip_task >> load_task
