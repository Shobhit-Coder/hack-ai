import os
import sys
from datetime import datetime

# Ensure Python can import /app/code
sys.path.append("/app/code")

from extractor import extract_all_resumes
from parser import parse_resume_file

from airflow import DAG
from airflow.operators.python import PythonOperator

RESUME_DIR = "/app/resumes"


# ------------------------------------------------------------
# 1️⃣ EXTRACT TASK — downloads files from Azure Blob
# ------------------------------------------------------------
def task_extract(**context):
    print("====================================================")
    print("[EXTRACT] Starting extract task")

    # This calls blob_utils → downloads → returns file list
    files = extract_all_resumes()

    print("[EXTRACT] Files ready for parsing:", files)

    context["ti"].xcom_push(key="resume_files", value=files)
    print("[EXTRACT] XCom push completed.")
    print("====================================================")


# ------------------------------------------------------------
# 2️⃣ PARSE TASK — calls Gemini & sends JSON to NGROK
# ------------------------------------------------------------
def task_parse(**context):
    print("====================================================")
    print("[PARSE] Starting parse task")

    filenames = context["ti"].xcom_pull(task_ids="extract", key="resume_files") or []
    print("[PARSE] Files received:", filenames)

    if not filenames:
        print("[PARSE] No files to parse. Exiting parse task.")
        return

    for fname in filenames:
        fpath = os.path.join(RESUME_DIR, fname)

        print("--------------------------------------------------")
        print(f"[PARSE] Processing file: {fname}")
        print(f"[PARSE] Full file path: {fpath}")

        try:
            parse_resume_file(fpath)
            print(f"[PARSE] Successfully parsed + sent to backend: {fname}")

        except Exception as e:
            print("--------------------------------------------------")
            print(f"[PARSE][ERROR] FAILED to parse {fname}")
            print(f"[PARSE][ERROR] Exception: {e}")
            print("--------------------------------------------------")

    print("====================================================")
    print("[PARSE] Finished processing all files.")
    print("====================================================")


# ------------------------------------------------------------
# DAG DEFINITION
# ------------------------------------------------------------
with DAG(
    dag_id="resume_pipeline_llm_only",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    parse = PythonOperator(
        task_id="parse",
        python_callable=task_parse,
    )

    extract >> parse
