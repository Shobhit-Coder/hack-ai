import os
import sys
from datetime import datetime

sys.path.append("/app/code")

from parser import parse_resume_file
from save_to_backend import save_results

from airflow import DAG
from airflow.operators.python import PythonOperator

RESUME_DIR = "/app/resumes"


def task_extract(**context):
    print("[EXTRACT] Starting extract task")
    print(f"[EXTRACT] Looking inside directory: {RESUME_DIR}")

    files = [
        f
        for f in os.listdir(RESUME_DIR)
        if os.path.isfile(os.path.join(RESUME_DIR, f))
        and f.lower().endswith((".pdf", ".docx", ".txt"))
    ]

    print("[EXTRACT] Found files:", files)
    context["ti"].xcom_push(key="resume_files", value=files)
    print("[EXTRACT] XCom pushed successfully.")


def task_parse(**context):
    print("--------------------------------------------------")
    print("[PARSE] Starting parse task")

    filenames = context["ti"].xcom_pull(task_ids="extract", key="resume_files") or []
    print("[PARSE] Received filenames from XCom:", filenames)

    parsed_outputs = {}

    if not filenames:
        print("[PARSE] No files to parse.")
    else:
        for fname in filenames:
            fpath = os.path.join(RESUME_DIR, fname)
            print("--------------------------------------------------")
            print(f"[PARSE] Starting processing for file: {fname}")
            print(f"[PARSE] Full file path: {fpath}")

            try:
                print(f"[PARSE] Calling parse_resume_file() for: {fname}")
                result = parse_resume_file(fpath)

                print(f"[PARSE] parse_resume_file() returned for {fname}:")
                print(result)

                parsed_outputs[fname] = result
                print(f"[PARSE] Successfully parsed: {fname}")

            except Exception as e:
                print("--------------------------------------------------")
                print(f"[PARSE][ERROR] FAILED to parse file: {fname}")
                print(f"[PARSE][ERROR] File path: {fpath}")
                print(f"[PARSE][ERROR] Exception: {e}")
                print("--------------------------------------------------")

    print("--------------------------------------------------")
    print("[PARSE] Finished parsing all files.")
    print("[PARSE] Parsed dict keys:", list(parsed_outputs.keys()))

    context["ti"].xcom_push(key="parsed", value=parsed_outputs)
    print("[PARSE] XCom push completed.")


def task_save(**context):
    print("--------------------------------------------------")
    print("[SAVE] Starting save task")

    parsed = context["ti"].xcom_pull(task_ids="parse", key="parsed") or {}
    print("[SAVE] Received parsed items:", list(parsed.keys()))

    if not parsed:
        print("[SAVE] No parsed data to save.")
    else:
        print("[SAVE] Sending parsed data to save_results()")
        save_results(parsed)

    print("[SAVE] Save task completed.")


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

    save = PythonOperator(
        task_id="save",
        python_callable=task_save,
    )

    extract >> parse >> save
