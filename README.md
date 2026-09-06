# etl-demo-2026-py

A template repository for a hands-on ETL lab.  It ships a working pipeline that reads from four heterogeneous sources (CSV, JSON, MySQL, MongoDB), transforms and enriches the data with pandas, and loads the result into a PostgreSQL data warehouse.  The same logical pipeline is implemented twice, once as an **Apache Airflow** DAG (task-based orchestration) and once as a set of **Dagster** assets (asset-based orchestration), so you can run both and compare the experience.

The bundled sample dataset models the **supply-side operations of a small hotel chain**: procurement orders, housekeeping logs, hotel/supplier/room dimensions, and supplier contract terms.  You will replace this dataset with your own domain assignment and adapt the transformation logic accordingly.

---

## 1. Prerequisites

You need a container runtime (Podman or Docker) and Git.  Everything else runs inside containers.

### 1.1 Install a container runtime

**Podman (recommended, free):** download Podman Desktop from https://podman-desktop.io.  During installation on Windows, it will offer to install WSL2 and set up a Podman machine automatically. Accept the defaults.  After installation, open Podman Desktop and make sure the machine is running (green indicator in the bottom-left corner).

**Docker (alternative):** Docker Desktop requires a paid license for organisations above 250 employees.  If you use it, install Docker Desktop 4.20+ and enable the WSL2 backend in Settings.

### 1.2 Verify your environment

Open a **PowerShell** terminal (on Windows) or a regular terminal (macOS/Linux) and run each command.  All three must succeed.

```
git --version
```
Expected: any version string.  If missing, install Git from https://git-scm.com.

```
podman --version
```
Expected: `podman version 4.x` or higher.  If you use Docker instead, substitute `docker` for `podman` in every command throughout this document.

```
podman compose version
```
Expected: a version string.  If you get "unknown command", install `podman-compose` (`pip install podman-compose`) or, for Docker users, make sure the Compose V2 plugin is present (`docker compose version`, not the legacy `docker-compose`).

**Windows users only:** confirm WSL2 is active:
```
wsl --status
```
Expected: output mentioning "Default Version: 2".  If WSL2 is missing, run `wsl --install` from an elevated PowerShell and reboot.

### 1.3 Minimum resources

| Platform       | RAM (free) | CPU cores | Disk   |
|----------------|-----------|-----------|--------|
| Windows 10/11  | 8 GB      | 4         | 10 GB  |
| macOS          | 8 GB      | 4         | 10 GB  |
| Linux          | 6 GB      | 4         | 10 GB  |

On Windows and macOS the container runtime runs inside a VM, which adds memory overhead compared to native Linux.

### 1.4 Platform notes

**Windows 10/11 (build 19041+):** WSL2 is required for both Podman and Docker.  Use Compose V2 (`podman compose` or `docker compose`), not the legacy standalone `docker-compose` v1 binary.

**macOS (12 Monterey+, Apple Silicon and Intel):** Podman Desktop, Docker Desktop 4.20+, or OrbStack all work.

**Linux (Ubuntu 22.04+, Fedora 38+):** Podman 4.4+ with podman-compose, or Docker Engine 24+.

**Windows without WSL2:** if you cannot or do not want to install WSL2 manually, open this repository in VS Code with the Dev Containers extension.  The included `.devcontainer/devcontainer.json` provides a Linux environment with Docker-in-Docker.

---

## 2. Quick start

All commands below use `podman compose`.  If you use Docker, replace `podman` with `docker`.

### 2.1 Clone and configure

One by one:

```
git clone https://github.com/mev-github/etl_demo.git
cd etl_demo
copy .env.example .env
```

On macOS/Linux use `cp` instead of `copy`.

Generate a Fernet key and paste it into `.env` as the value of `AIRFLOW__CORE__FERNET_KEY`. Run this in your terminal:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

If `cryptography` is not installed locally, use:

```
python -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Open `.env` in any text editor and paste the generated string after the `=` sign on the `AIRFLOW__CORE__FERNET_KEY` line.

### 2.2 Option A: run with Airflow

```
podman compose --profile airflow up -d --build
```

Wait for all containers to become healthy.  Check status with:

```
podman compose ps
```

When all services show "healthy" or "running", open **http://localhost:8080** in your browser.  Authentication is disabled, so you go straight to the dashboard.  Find the `hotel_supply_etl` DAG in the list, unpause it (toggle on the left), and trigger a manual run via the "play" button.

### 2.3 Option B: run with Dagster

```
podman compose --profile dagster up -d --build
```

Check status with `podman compose ps`, then open **http://localhost:3000**.  Navigate to the asset graph, select all assets, and click **Materialize all**.

### 2.4 Shutting down

```
podman compose --profile airflow down -v
```

Replace `airflow` with `dagster` if you ran that profile.  The `-v` flag removes named volumes so the next run starts from a clean state.

---

## 3. Port reference

| Service        | URL / Port              | Notes |
|----------------|-------------------------|-------|
| Airflow UI     | http://localhost:8080   | Profile `airflow`. No login required |
| Dagster UI     | http://localhost:3000   | Profile `dagster` |
| Adminer        | http://localhost:8081   | Web UI for MySQL and PostgreSQL |
| Mongo Express  | http://localhost:8082   | Web UI for MongoDB |
| MySQL          | localhost:3306          | User: etl_user / etl_pass |
| PostgreSQL     | localhost:5432          | User: etl_user / etl_pass, DB: hotel_dwh |
| MongoDB        | localhost:27017         | User: etl_user / etl_pass |

**Connecting from Adminer:** Adminer runs inside Docker, so you must use container service names, not `localhost`.  In the "Server" field enter `mysql` for MySQL or `postgres` for PostgreSQL.  Username `etl_user`, password `etl_pass`.

---

## 4. IDE setup

The ETL source code lives in `src/`.  Your IDE does not know this automatically, so you must mark it as a source root manually.  Without this step, imports like `from common.extract import ...` will show as unresolved errors.

**PyCharm / IntelliJ IDEA with Python plugin:**
Right-click the `src` folder in the Project tool window, then select **Mark Directory as > Sources Root**.  The folder icon turns blue.

**VS Code:**
Add this to your workspace `.vscode/settings.json`:
```json
{
  "python.analysis.extraPaths": ["src"],
  "python.autoComplete.extraPaths": ["src"]
}
```

After marking the source root, install the project dependencies into your local interpreter if you want full autocompletion and type checking:

```
pip install -e .
```

This uses `pyproject.toml` to install the `common` package in editable mode.  This step is optional since all code runs inside containers, not on your host, but it makes the IDE experience much better.

---

## 5. Repository structure

```
etl-demo-2026-py/
├── docker-compose.yml           # profiles: airflow, dagster
├── Dockerfile.airflow           # Airflow image with ETL deps
├── Dockerfile.dagster           # Dagster image with ETL deps
├── Dockerfile.etl               # (optional) standalone ETL base
├── pyproject.toml               # editable install for local dev
├── .devcontainer/               # VS Code Dev Container for Windows
├── .env.example
├── .gitignore
├── requirements.txt             # Python deps for the ETL code
├── README.md
├── pregen/
│   ├── data/
│   │   ├── supply_orders.csv    # Fact: procurement orders
│   │   └── housekeeping_log.json# Fact: housekeeping events
│   └── db/
│       ├── mysql_init.sql       # Dimension tables + seed data
│       ├── postgres_init.sql    # Target warehouse DDL
│       └── mongo_seed.js        # Supplier contract documents
└── src/
    ├── common/                  # Shared ETL logic (both orchestrators use this)
    │   ├── __init__.py
    │   ├── config.py            # Connection settings from env vars
    │   ├── extract.py           # Read from CSV, JSON, MySQL, MongoDB
    │   ├── transform.py         # Join, enrich, classify, add metadata
    │   └── load.py              # Write to PostgreSQL
    ├── pipeline_airflow/        # named to avoid shadowing the airflow package
    │   └── dags/
    │       └── hotel_supply_etl.py   # Airflow DAG definition
    └── pipeline_dagster/        # named to avoid shadowing the dagster package
        ├── assets.py            # Dagster asset definitions
        ├── workspace.yaml       # Dagster code location config
        └── dagster.yaml         # Dagster instance config
```

---

## 6. Where to make changes (student tasks)

Your primary editing targets are in `src/common/transform.py`:

1. **`apply_business_logic(df)`** receives a DataFrame after the join step.  Add your domain-specific calculations, derivations, and enrichment here.  The default implementation computes a discounted price for supply orders; replace it with logic that fits your assigned domain.

2. **`classify_event_type(row, source)`** returns the `event_type` string stamped on every output row.  Define meaningful categories for your data (e.g. `"booking_created"`, `"maintenance_urgent"`).

3. **`pregen/data/`** -- replace `supply_orders.csv` and `housekeeping_log.json` with your own source files.  Keep at least two files with different formats (CSV and JSON) to preserve the multi-source nature of the exercise.

4. **`pregen/db/mysql_init.sql`** -- redefine the dimension tables for your domain.

5. **`pregen/db/mongo_seed.js`** -- replace the supplier contracts with enrichment documents relevant to your domain.

6. **`pregen/db/postgres_init.sql`** -- update the target table DDL.  Keep the three mandatory metadata columns (`batch_id`, `batch_ts`, `event_type`) and add your own domain columns.

After replacing the dataset, update `src/common/extract.py` if your filenames or MySQL table names differ, and adjust the join logic in the private helper functions `_join_supply_orders` and `_join_housekeeping` inside `transform.py`.

---

## 7. Mandatory metadata columns

Every student's final table must include these three columns regardless of domain:

| Column | Type | Description |
|--------|------|-------------|
| `batch_id` | `VARCHAR(64)` | UUID generated at the start of each pipeline run |
| `batch_ts` | `TIMESTAMP WITH TIME ZONE` | Timestamp of the pipeline run |
| `event_type` | `VARCHAR(60)` | Domain-specific row classification, set in `classify_event_type()` |

These are added automatically by `build_fact_table()` in `transform.py`.  Do not remove them.

---

## 8. Airflow vs Dagster: what to compare

The same ETL logic runs under two orchestration models.  Here is what to pay attention to when you run both.

**Airflow (task-based):**
The pipeline is a DAG of tasks.  Each task is an explicit operation ("extract CSV", "transform", "load").  Data flows between tasks through XCom, a key-value sidecar store.  You define execution order with `>>` operators.  The Airflow UI shows task status, duration, and logs per task.  The mental model is "what steps run in what order."

**Dagster (asset-based):**
The pipeline is a graph of assets.  Each asset is a named data product ("supply_orders", "fact_hotel_operations").  Dependencies are declared implicitly: if an asset function takes `supply_orders` as a parameter, Dagster knows it depends on the `supply_orders` asset.  The Dagster UI shows the asset lineage graph and materialisation history.  The mental model is "what data exists and where did it come from."

Points to note in your lab report:

- How is the dependency graph expressed in each system?
- Where does intermediate data live (XCom vs in-process DataFrames)?
- What happens when a single step fails?  How do you re-run just that step?
- Which UI gives you better visibility into data lineage?
- Which approach feels more natural for this pipeline's structure?

---

## 9. Troubleshooting

**"The system cannot find the file specified" or connection refused on Windows:** the Podman machine (or Docker Desktop engine) is not running.  Open Podman Desktop (or Docker Desktop) and start the engine, then retry.

**"unable to retrieve auth token", "invalid username/password", or "unauthorized" when pulling/building images:** the container runtime is sending stale or missing credentials to Docker Hub.  This is common when Podman inherits a credential store entry left by a previous Docker Desktop installation, or when Docker Hub rate-limits anonymous pulls.

Fix for Podman:
```
podman logout docker.io
podman login docker.io
```

Fix for Docker:
```
docker logout docker.io
docker login docker.io
```

Enter your Docker Hub username and password (a free account is sufficient).  If you do not have an account, create one at https://hub.docker.com.  On Windows, Podman stores credentials in `%APPDATA%\containers\auth.json`; if the logout command does not help, open that file and delete the `docker.io` key manually, then run `podman login docker.io` again.

**Containers fail to start:** run `podman compose ps` and check which service is unhealthy.  Then `podman compose logs <service>` for details.  The most common cause is a port conflict (another process already listening on 3306, 5432, etc.).

**Airflow DAG not visible:** the scheduler needs 30-60 seconds to parse new DAGs after startup.  Check `podman compose logs airflow-scheduler` for import errors.

**MongoDB seed not applied:** the `docker-entrypoint-initdb.d` scripts only run on a fresh volume.  If you changed `mongo_seed.js` after the first run, tear down volumes with `podman compose down -v` and rebuild.

**Out of memory:** reduce memory limits in `docker-compose.yml` or close other applications.  The Airflow profile needs roughly 4 GB total across all containers; Dagster needs roughly 3 GB.

**Podman compose hangs or fails with "unknown flag":** make sure you have podman-compose installed (`pip install podman-compose`).  Some older Podman versions bundle a different compose wrapper.  `podman compose version` should print a version string without errors.
