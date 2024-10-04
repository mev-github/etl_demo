# ETL Pipeline with Apache Airflow

This project implements an ETL (Extract, Transform, Load) pipeline using Apache Airflow. The pipeline extracts data from PostgreSQL and MongoDB databases, as well as local CSV or JSON files, transforms the data, and loads it into a MySQL database. All components are containerized using Docker, ensuring portability and ease of deployment.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [ETL Pipeline Logic](#etl-pipeline-logic)
- [Instructions for Setup and Execution](#instructions-for-setup-and-execution)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
    - [Running the Application](#running-the-application)
    - [Testing](#testing)
        - [Unit Tests](#unit-tests)
        - [Manual Testing in Airflow](#manual-testing-in-airflow)
- [Potential Limitations](#potential-limitations)

## Introduction

This project demonstrates how to build a scalable and flexible ETL pipeline using Apache Airflow. The pipeline allows users to select which data sources to extract from and specify the target table in the MySQL database for data loading. The entire setup is orchestrated using Docker Compose, enabling seamless deployment on any system with Docker support.

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
├── tests/
│   └── test_etl_tasks.py
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
- **tests/**: Contains unit tests for the ETL tasks.
    - **test_etl_tasks.py**: Unit tests using `pytest`.
- **init/**: Initialization scripts for the databases.
    - **mongodb/**: MongoDB initialization script (`init.js`).
    - **mysql/**: MySQL initialization script (`init.sql`).
    - **postgres/**: PostgreSQL initialization script (`init.sql`).
- **docker-compose.yml**: Docker Compose configuration file.
- **.env**: Environment variables for configurations and credentials.
- **README.md**: Detailed project documentation (this file).

## ETL Pipeline Logic

The ETL pipeline consists of the following steps:

1. **Extraction**:
    - **PostgreSQL**: Extracts data from a specified table in the PostgreSQL database.
    - **MongoDB**: Extracts data from a specified collection in the MongoDB database.
    - **Local File**: Reads data from a local CSV or JSON file.
    - The data extraction from each source is optional and controlled via Airflow Variables.

2. **Transformation**:
    - Combines data from the selected sources into a single DataFrame.
    - Performs data cleaning, such as removing duplicates.
    - Placeholder for additional transformation logic (e.g., data normalization, aggregation).

3. **Loading**:
    - Inserts the transformed data into a specified table in the MySQL database.
    - Supports specifying the target table via an Airflow Variable.

4. **Orchestration**:
    - Apache Airflow orchestrates the entire pipeline using a DAG (`etl_dag.py`).
    - Users can control the execution flow by setting Airflow Variables.

## Instructions for Setup and Execution

### Prerequisites

- **Operating System**: The project is designed to run on Windows, but it can also run on Linux or macOS.
- **Docker Desktop**: Install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop).
    - Ensure Docker is configured to use **Linux containers**.
    - Enable **WSL 2** backend on Windows for better performance.
- **Git**: Install Git to clone the repository.

### Setup

#### Step 1: Clone the Repository

Open a terminal or PowerShell and navigate to your desired directory:

```bash
git clone <repository_url>
cd project_root
```

#### Step 2: Configure Environment Variables

- Open the `.env` file in a text editor.
- **Generate a Fernet Key**:

  In your terminal, run:

  ```bash
  docker run --rm apache/airflow:2.6.3 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

    - Copy the generated key and paste it into the `.env` file as the value for `AIRFLOW_FERNET_KEY`.

- **Verify and Update Credentials**:

  Ensure that all database credentials and configurations are set correctly in the `.env` file.

#### Step 3: Build and Start Services

- **Build the Custom Airflow Image and Initialize Airflow**:

  ```bash
  docker-compose up --build airflow_init
  ```

    - Wait until the initialization completes (look for "Initialization done" in the logs).

- **Start All Services**:

  ```bash
  docker-compose up -d
  ```

    - This starts all services in detached mode.

### Running the Application

#### Access the Airflow Web UI

- Open a web browser and navigate to `http://localhost:8080`.
- Log in with:
    - **Username**: `admin`
    - **Password**: `admin`

#### Configure Airflow Variables

- In the Airflow UI, navigate to **Admin** > **Variables**.
- Add or edit the following variables to control the pipeline:

    - **read_postgres**: `True` or `False` (default: `True`)
    - **read_mongodb**: `True` or `False` (default: `True`)
    - **read_file**: `True` or `False` (default: `False`)
    - **target_table**: Name of the MySQL table to load data into (default: `final_table`)

#### Trigger the ETL Pipeline DAG

- In the Airflow UI, go to the **DAGs** view.
- Locate the `etl_pipeline` DAG.
- Toggle the DAG **On** if it's not already.
- Click the **Trigger DAG** button to start a manual run.

#### Monitor the Workflow

- Use the **Graph View** or **Tree View** to monitor the execution of each task.
- Ensure that each task completes successfully.
- View logs for each task by clicking on it and selecting **View Log**.

### Testing

#### Unit Tests

The project includes unit tests for the ETL functions using `pytest`.

##### Running Unit Tests

1. **Install `pytest`**:

   `pytest` is already included in the `airflow/requirements.txt`. Ensure the Docker image is rebuilt to include it.

2. **Run Tests Inside the Airflow Webserver Container**:

   ```bash
   docker exec -it airflow_webserver bash
   cd /opt/airflow/tests
   pytest test_etl_tasks.py
   ```

    - This will execute all unit tests and display the results.

#### Manual Testing in Airflow

##### Verify Data in MySQL

After the DAG completes successfully, verify that data has been written to the MySQL database.

1. **Connect to the MySQL Database**:

    - Use a MySQL client (e.g., MySQL Workbench) or connect via terminal:

      ```bash
      docker exec -it mysql_container mysql -u mysql_user -p
      ```

      Enter the MySQL password (`mysql_password` from the `.env` file).

2. **Run SQL Queries**:

   ```sql
   USE mysql_db;
   SELECT * FROM final_table;
   ```

    - Verify that the data from the selected sources has been inserted into the `final_table`.

##### Troubleshooting

- **Task Failures**:

    - Check task logs in the Airflow UI for error messages.
    - Ensure that all services (databases, Airflow components) are running.

- **Connection Issues**:

    - Verify that the database credentials in the `.env` file are correct.
    - Ensure Docker has sufficient resources allocated.

### Shutting Down Services

When finished, you can stop and remove containers:

```bash
docker-compose down
```

## Potential Limitations

- **Resource Consumption**: Running multiple containers (databases, Airflow services) can consume significant system resources.

- **Windows File System Compatibility**: On Windows, Docker's file system sharing may cause issues with volume mounts and file permissions.

- **Error Handling in ETL Tasks**: While basic error handling is implemented, the ETL tasks might not handle all edge cases, such as network interruptions or corrupted data.

- **Security Considerations**:

    - Credentials are stored in the `.env` file, which may not be secure for production environments.
    - The default Airflow user credentials are weak and should be changed for production use.

- **Scalability**:

    - The current setup is suitable for small to medium workloads. For larger datasets, performance tuning and scaling would be necessary.
