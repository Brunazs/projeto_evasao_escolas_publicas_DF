# scripts/extract_data_se_df.py
"""
Extração de dados da SEEDF - Situação do Aluno
Este script baixa e processa o CSV oficial da SEEDF
"""

import pandas as pd
import requests
import os
import csv

URL = "https://data.se.df.gov.br/dataset/situacao-do-aluno-serie-historica/resource/c196e905-11d2-4333-9a5a-e64d6a89d2bb/download/situacao_aluno.csv"

def extract_situacao_aluno():
    """Baixa e processa o CSV oficial da SEEDF"""
    
    print("📥 Iniciando download dos dados da SEEDF...")
    print(f"   Fonte: {URL}")
    
    os.makedirs('data/raw', exist_ok=True)
    file_path = 'data/raw/situacao_aluno.csv'
    
    try:
        # Download do arquivo
        response = requests.get(URL, timeout=60)
        response.raise_for_status()
        
        # Salvar arquivo bruto
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Download concluído: {file_path}")
        print(f"   Tamanho: {os.path.getsize(file_path) / 1024:.1f} KB")
        
        return file_path
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None

if __name__ == "__main__":
    extract_situacao_aluno()