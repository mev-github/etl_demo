# Project: Dockerized Data Processing with Jenkins Automation

This project facilitates automated data processing using a Python script managed by Jenkins within a Docker environment.
It involves a Jenkins CI/CD pipeline to handle tasks that interact with a MySQL database.

## Prerequisites

- Python 3.11+
- Docker
- Docker Compose

## Directory Structure

```plaintext
/
├── config/
│   ├── data_connection_config.yaml    # Database connection configurations
│   ├── init_mysql.sql                 # SQL script to initialize MySQL database
│   └── settings.yaml                  # Application pre-settings
├── src/
│   ├── common/
│   │   └── db_manager.py              # Database management utilities
│   │   └── utils.py                   # General utility functions
│   ├── dpu/
│   │   └── data_processing.py         # Data processing utilities
│   │   └── data_reader.py             # Data reading utilities
│   │   └── data_writer.py             # Data writing utilities
│   └── main.py                        # Main script for data processing
├── local_data/
│   ├── input/
│   │   └── sample_data.csv            # Default sample input data
│   └── output/                        # Directory for output data
├── docker-compose.yml                 # Docker compose file for the environment
├── Dockerfile                         # Dockerfile for Python environment
├── Jenkinsfile                        # Jenkins pipeline configuration (optional)
└── README.md                          # This file
```

## Setup Instructions

### Step 1: Clone Repository

Clone the project repository (if applicable):

```bash
git clone <repository-url>
cd <project-directory>
```

### Step 2: Build Docker Images

Run the following command to build Docker images specified in the `docker-compose.yml`:

```bash
docker-compose build
```

### Step 3: Initialize Services

Start all services (Jenkins, MySQL, app placeholder):

```bash
docker-compose up -d
```

### Step 4: Configure Jenkins

1. **Access Jenkins**:
    - Open a web browser and go to `http://localhost:8080`.
    - Complete the initial setup using the secret found with:
      ```bash
      docker exec <jenkins-container-id> cat /var/jenkins_home/secrets/initialAdminPassword
      ```
    - Install recommended plugins and create an admin user.

2. **Install Necessary Plugins** (if not pre-installed):
    - Go to **Manage Jenkins** > **Manage Plugins** > **Available**
    - Search for "Docker Pipeline" and any other necessary plugins, then install them.

3. **Create a Pipeline Job**:
    - Go to **New Item**, select **Pipeline**, and name your job.
    - In the pipeline configuration, select **Pipeline script from SCM** if using Git, or **Pipeline script** and paste
      the content of `Jenkinsfile`.

### Step 5: Run Pipeline

- Manually trigger the pipeline job configured in the previous step to execute the data processing tasks.

## Updating Project

### Updating Application Code

1. Make changes to your application code (e.g., `main.py` or scripts in `src/`).
2. Rebuild the Docker image if necessary:
   ```bash
   docker-compose build app
   ```
3. Restart the affected services to apply changes:
   ```bash
   docker-compose up -d --no-deps app
   ```

### Updating Jenkins Jobs

- If modifications are needed for the Jenkins pipeline:
    1. Go to the respective job configuration in Jenkins.
    2. Adjust the pipeline script as needed.
    3. Save changes and rerun the job.

### Updating Docker Compose and Environment Configurations

- For significant changes such as adding new services or modifying existing services:
    1. Update the `docker-compose.yml`.
    2. Reload the Docker Compose configurations:
       ```bash
       docker-compose up -d
       ```

## Common Troubleshooting

- **Jenkins Cannot Find Docker**: Ensure that Jenkins has proper permissions to access Docker. Review the user group
  settings for Docker.
- **Database Connection Issues**: Check the `data_connection_config.yaml` for correctness in database configurations and
  ensure MySQL service is properly initialized.

For more detailed troubleshooting, refer to service-specific logs using:

```bash
docker-compose logs <service-name>
```
