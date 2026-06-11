#!/bin/bash

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip
pip install pandas
pip install requests
pip install -r requirements.txt
pip install apache-airflow

# AIRFLOW_VERSION=2.10.5
# PYTHON_VERSION=3.11

# pip install -r requirements-airflow.txt \
# -c "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"