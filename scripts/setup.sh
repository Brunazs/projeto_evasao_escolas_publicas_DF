#!/bin/bash

# Detecta o diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AIRFLOW_HOME="$PROJECT_DIR/airflow"

echo "📁 Projeto: $PROJECT_DIR"
echo "✈️  Airflow em: $AIRFLOW_HOME"

# Ativa venv
source "$PROJECT_DIR/venv/bin/activate"

# Inicializa Airflow
echo "🔄 Inicializando Airflow..."
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com 2>/dev/null || true

# Sobe
echo "🚀 Iniciando Airflow..."
airflow standalone