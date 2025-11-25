# Resume Parsing and Enrichment Pipeline

This folder contains a robust, production-ready pipeline designed for automated resume parsing and enrichment using LLMs (Large Language Models) with orchestration powered by Apache Airflow.

---

## What This Pipeline Does

- **Automated Resume Parsing**: Ingests resumes, processes using custom and LLM-driven logic, and extracts structured information about candidates for applied roles.
- **Scheduled Processing**: Avoids the delays of manual ad-hoc parsing by running as a nightly batch job (cron), updating all resume data and making it instantly available the next day.
- **Database Integration**: Outputs are seamlessly updated to the backend/database, ensuring recruiters always have fresh, role-relevant insights by morning.
- **Scaling for Real-World Use**: Designed with business volume in mind, easily handling large numbers of resumes and rapid application flows.

---

## Folder Structure

- `airflow`: Contains DAGs (Directed Acyclic Graphs) and configs for task scheduling and orchestration.
- `code/`: Core scripts for extraction, parsing, backend interfacing, and LLM integration.
- `Dockerfile` & `docker-compose.yaml`: Containerization for standardized deployments and reproducibility.
- `requirements.txt`: Python dependencies for app and orchestration.

---

## How It Works

1. **Resume Extraction**: Downloads resumes from cloud blob storage (Azure).
2. **Parsing and Enrichment**: Uses LLMs to analyze files and extract candidate details; job descriptions are fetched via API and matched.
3. **Workflow Orchestration**: Airflow manages dependencies, scheduling, retries, and timeouts, running scheduled jobs via DAGs.
4. **Database Updates**: Parsed and enriched data is posted to backend endpoints for downstream usage.

---

## Benefits of Airflow

- **Reliability & Traceability**: Manage, track, and monitor jobs and dependencies with ease.
- **UI-Driven Monitoring**: Easily view workflow status via the [Airflow dashboard](http://98.70.42.182:8080/login).
- **Automation Out-of-the-Box**: Stay ahead of hiring demand with scheduled data updates, improving candidate/recruiter experience.

---

## Real World Value

- **Zero Wait Time for Recruiters**: No manual resume parsing—automated overnight bulk updates deliver results by morning.
- **Integration Ready**: Flexible design to interface with databases, blob storage, and backend APIs.
- **Scale and Reliability**: Suitable for both startups and enterprise-scale hiring pipelines.

---

## Installation & Local Setup

**Prerequisites**:
- Docker & Docker Compose installed ([Docker docs](https://docs.docker.com/get-docker/))
- Python 3.10+ (if running outside containers)
- Configure `.env` file with your Azure, Gemini, and Backend secrets (see example in repo root)

### 1. Clone the Repository

```bash
git clone https://github.com/Shobhit-Coder/hack-ai.git
cd hack-ai/pipeline
```

### 2. Prepare Your `.env` File

Create and edit a `.env` file in the `pipeline/` folder with keys for:
- Azure Blob Storage (connection string, container, etc)
- Gemini API key
- Backend service URLs

(See the repo README or example for details.)

### 3. Build and Start with Docker Compose

```bash
docker-compose up --build
```

This command will:
- Build the pipeline image with all dependencies
- Start Airflow Scheduler and Webserver (accessible at [http://localhost:8080](http://localhost:8080) or your deployed host)
- Mount necessary folders for DAGs, code, and resume files

### 4. Interact with Airflow

Visit the Airflow dashboard at [http://localhost:8080](http://localhost:8080)  
Default credentials: `admin` / `admin` (set in compose file)

- Trigger the DAG manually or set up external scheduling (e.g. cron) as desired

### 5. Check Output

- Candidate data, logs, and generated interview questions will be written to the mounted `output/` folder and posted to your backend API.
- See DAG logs, view parsed results, monitor job statuses—all via Airflow UI and output files.

---

**For further deployment/configuration help, see the Dockerfile, requirements.txt, and DAG scripts provided. For advanced Airflow usage, consult the [official Airflow documentation](https://airflow.apache.org/docs/).**
