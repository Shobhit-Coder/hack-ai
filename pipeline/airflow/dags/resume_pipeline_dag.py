# resume_pipeline_dag.py
import os
import sys
from datetime import datetime, timedelta

# 1. Add your code directory to system path so Airflow can find your modules
sys.path.append("/app/code")

# 2. Import your specific functions
from extractor import extract_all_resumes
from parser import parse_resume_file  # Sync wrapper in parser.py

from airflow import DAG
from airflow.operators.python import PythonOperator

# Env var matches what you used in extractor.py
RESUME_DIR = os.getenv("LOCAL_RESUME_DIR", "/app/resumes")


# ------------------------------------------------------------
# TASK 1: EXTRACT
# Downloads files and passes the LIST OF FILENAMES to XCom
# ------------------------------------------------------------
def task_extract(**context):
    print("====================================================")
    print("[EXTRACT] Starting extraction task...")

    files = extract_all_resumes()

    print(f"[EXTRACT] Extracted {len(files)} files.")
    print(f"[EXTRACT] File list: {files}")

    context["ti"].xcom_push(key="resume_filenames", value=files)

    print("[EXTRACT] Pushed filenames to XCom.")
    print("====================================================")


# ------------------------------------------------------------
# TASK 2: PARSE
# Pulls filenames, creates full paths, and runs the full LLM + backend flow
# ------------------------------------------------------------
def task_parse(**context):
    print("====================================================")
    print("[PARSE] Starting parse task...")

    filenames = context["ti"].xcom_pull(task_ids="extract", key="resume_filenames")

    if not filenames:
        print("[PARSE] ⚠️ No files found in XCom. Nothing to process.")
        return

    success_count = 0
    fail_count = 0

    for fname in filenames:
        fpath = os.path.join(RESUME_DIR, fname)

        if not os.path.exists(fpath):
            print(f"[PARSE] ❌ File missing locally (Check path logic): {fpath}")
            fail_count += 1
            continue

        print("--------------------------------------------------")
        print(f"[PARSE] Processing: {fname}")

        try:
            result = parse_resume_file(fpath)

            if result and result.get("candidate_id"):
                cid = result.get("candidate_id")
                q_count = result.get("questions_count", 0)
                score = result.get("resume_job_score")
                print(
                    f"[PARSE] ✅ Success! Candidate ID: {cid} | "
                    f"resume_job_score: {score} | Questions: {q_count}"
                )
                success_count += 1
            else:
                print(f"[PARSE] ⚠️ Parsed, but returned incomplete data or no candidate_id.")
                fail_count += 1

        except Exception as e:
            print(f"[PARSE] ❌ CRITICAL ERROR parsing {fname}: {e}")
            fail_count += 1

    print("====================================================")
    print(f"[PARSE] Batch Complete. Success: {success_count} | Failed: {fail_count}")
    print("====================================================")


# ------------------------------------------------------------
# DAG DEFINITION
# ------------------------------------------------------------
default_args = {
    "owner": "airflow",
    "retries": 0,  # Disable retries for now to avoid duplicate API calls while testing
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="resume_parsing_pipeline_v3",  # keep same ID unless you want a new DAG
    default_args=default_args,
    start_date=days_ago(1),      # <-- Automatically today's date
    schedule_interval="30 15 * * *",  # 9:00 PM daily
    catchup=False,
    tags=["hiring", "genai", "azure"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    parse_task = PythonOperator(
        task_id="parse",
        python_callable=task_parse,
        execution_timeout=timedelta(minutes=60),  # Safety limit
    )

    # Set Dependency: Extract runs first, then Parse
    extract_task >> parse_task
