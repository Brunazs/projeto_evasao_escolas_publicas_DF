# airflow/dags/evasao_escolar_dag.py

import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator


import os
import sys

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from scripts.extractors import extract_seedf, extract_huggingface, extract_policy_data

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 5, 1),
}

with DAG(
    dag_id="evasao_escolar_etl",
    default_args=default_args,
    description="ETL - Evasão Escolar Escolas Públicas DF",
    schedule="@monthly",
    catchup=False,
    tags=["educacao", "etl", "df"],
) as dag:

    t_seedf = PythonOperator(
        task_id="extract_seedf",
        python_callable=extract_seedf,
    )

    t_hf = PythonOperator(
        task_id="extract_huggingface",
        python_callable=extract_huggingface,
    )

    t_policy = PythonOperator(
        task_id="extract_policy_data",
        python_callable=extract_policy_data,
    )

    t_transform = BashOperator(
        task_id="transform",
        bash_command=f"cd {PROJECT_DIR} && python scripts/transform.py",
    )

    [t_seedf, t_hf, t_policy] >> t_transform

