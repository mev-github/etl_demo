# ETL Pipeline with Apache Airflow and Docker

This project implements an ETL (Extract, Transform, Load) pipeline using Apache Airflow. The pipeline is designed to extract data from various sources (PostgreSQL, MongoDB, and local files), transform the data, and load it into a MySQL database. The entire project is containerized using Docker and orchestrated with Docker Compose, ensuring a consistent and reproducible environment.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Running the ETL Pipeline](#running-the-etl-pipeline)
- [Stopping the Services](#stopping-the-services)
- [Troubleshooting](#troubleshooting)

## Introduction

This ETL pipeline demonstrates how to build a scalable and flexible data processing system using Apache Airflow. It allows users to select which data sources to extract from and specify the target table in the MySQL database. The pipeline components include:

- **Extraction**: From PostgreSQL, MongoDB, and local CSV/JSON files.
- **Transformation**: Data cleaning, deduplication, and UUID assignment.
- **Loading**: Inserting transformed data into MySQL.
- **Orchestration**: Managed by Apache Airflow DAGs.

## Project Structure

```
project_root/
├── airflow/
│   ├── dags/
│   │   └── etl_dag.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── logs/
│   └── plugins/
├── app/
│   ├── config.py
│   └── etl_tasks.py
├── data/
│   └── input_file.csv
├── init/
│   ├── mongodb/
│   │   └── init.js
│   ├── mysql/
│   │   └── init.sql
│   └── postgres/
│       └── init.sql
├── docker-compose.yml
├── .env
└── README.md
```

- **airflow/**: Contains Airflow DAGs, Dockerfile, and requirements.
    - **dags/**: The Airflow DAG definition (`etl_dag.py`).
    - **Dockerfile**: Custom Dockerfile to include necessary Python packages.
    - **requirements.txt**: Python dependencies for the Airflow environment.
- **app/**: Contains the ETL task functions and configurations.
    - **config.py**: Configuration settings and environment variables.
    - **etl_tasks.py**: ETL task functions for data extraction, transformation, and loading.
- **data/**: Directory for local data files (e.g., `input_file.csv`).
- **init/**: Initialization scripts for the databases.
    - **mongodb/**: MongoDB initialization script (`init.js`).
    - **mysql/**: MySQL initialization script (`init.sql`).
    - **postgres/**: PostgreSQL initialization script (`init.sql`).
- **docker-compose.yml**: Docker Compose configuration file.
- **.env**: Environment variables for configurations and credentials.
- **README.md**: Project documentation (this file).

## Installation and Setup

Follow these steps to set up and run the ETL pipeline:

### 1. Clone the Repository

```bash
git clone <repository_url>
cd project_root
```

### 2. Configure Environment Variables

Copy the example `.env` file and update the environment variables as needed.

#### Generate a Fernet Key

Apache Airflow requires a Fernet key for encryption. Generate one using the following command:

```bash
pip install cryptography
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the generated key and set it in the `.env` file:

```
AIRFLOW_FERNET_KEY=your_generated_fernet_key_here
```

#### Verify and Update Credentials

Ensure all database credentials and hostnames are correctly set in the `.env` file.

### 3. Build and Start the Docker Containers

#### Build the Custom Airflow Image

From the project root directory, run:

```bash
docker-compose build
```

#### Initialize Airflow

Before starting Airflow services, initialize the Airflow database and create the admin user:

```bash
docker-compose up airflow_init
```

Wait until the initialization is complete. You should see a message indicating that the Airflow database has been initialized and the admin user has been created.

#### Start All Services

Now start all the services using:

```bash
docker-compose up -d
```

This command starts all containers in detached mode.

## Configuration

### Accessing the Airflow Web UI

Open your web browser and navigate to `http://localhost:8080`.

Login credentials:

- **Username**: `admin`
- **Password**: `admin`

### Setting Airflow Variables

In the Airflow UI:

1. Navigate to **Admin** > **Variables**.
2. Add or update the following variables to control the ETL pipeline:

    - **read_postgres**: `True` or `False` (default: `True`)
    - **read_mongodb**: `True` or `False` (default: `True`)
    - **read_file**: `True` or `False` (default: `False`)
    - **postgres_source_table**: Name of the source table in PostgreSQL (default: `source_table`)
    - **mongodb_source_collection**: Name of the source collection in MongoDB (default: `source_collection`)
    - **target_table**: Name of the target table in MySQL (default: `final_table`)

### Adjusting the Data Sources

If you want to include data from a local file:

1. Place your CSV or JSON file in the `data/` directory.
2. Update the `LOCAL_FILE_PATH` in the `.env` file to point to your file, e.g.:

    ```
    LOCAL_FILE_PATH=/opt/airflow/data/your_file.csv
    ```

## Running the ETL Pipeline

### Trigger the DAG

In the Airflow UI:

1. Go to the **DAGs** page.
2. Locate the `etl_pipeline` DAG.
3. Turn on the DAG by toggling the **On/Off** switch.
4. Manually trigger the DAG by clicking the **Trigger DAG** button.

### Monitor the Pipeline

Use Airflow's built-in monitoring tools:

- **Graph View**: Visualize task dependencies.
- **Tree View**: See the status of task runs over time.
- **Task Logs**: Click on a task and select **Log** to view its output.

## Stopping the Services

To stop and remove all containers, networks, and volumes created by Docker Compose:

```bash
docker-compose down -v
```

The `-v` flag removes the named volumes declared in the `volumes` section of the `docker-compose.yml` file, freeing up space.

## Troubleshooting

### Common Issues

- **Services Not Starting**: Ensure Docker Desktop is running and you have sufficient resources allocated (CPU, Memory).
- **Port Conflicts**: Make sure the ports specified in `docker-compose.yml` are not being used by other applications.
- **Database Connection Errors**: Verify that the database credentials in `.env` and Airflow Variables are correct.
- **Airflow Variables Not Set**: Ensure you've set all the necessary Airflow Variables in the UI.

### Viewing Logs

- **Container Logs**: Use `docker-compose logs service_name` to view logs for a specific service.
- **Airflow Task Logs**: Accessible via the Airflow UI under each task instance.
