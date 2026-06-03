# scripts/extract_huggingface.py
"""
Extração de dados do Censo Escolar via Hugging Face Datasets
Dataset: Horusprg/censo-2015-2024

Este script é OPCIONAL - os dados principais já são obtidos via SEEDF.
Use apenas se precisar de dados complementares do Censo Escolar.
"""

import pandas as pd
import argparse
import os
import sys
from datetime import datetime

def extract_censo_escolar_simple(state='DF', max_records=100000):
    """
    Extrai dados do Censo Escolar do Hugging Face usando download direto
    
    Args:
        state: UF a ser filtrada (ex: 'DF', 'SP', 'RJ')
        max_records: Número máximo de registros (None = todos)
    """
    
    print("=" * 60)
    print("📥 Extrator de Dados - Censo Escolar (Hugging Face)")
    print("=" * 60)
    print(f"   Dataset: Horusprg/censo-2015-2024")
    print(f"   Filtro: UF = {state}")
    print(f"   Max records: {max_records if max_records else 'Todos'}")
    
    # Tentar diferentes URLs do dataset
    urls = [
        "https://huggingface.co/datasets/Horusprg/censo-2015-2024/resolve/main/BR_School_Census_2015-2024_tratado.csv",
        "https://huggingface.co/datasets/Horusprg/censo-2015-2024/resolve/main/BR_School_Census_2015-2024.csv",
        "https://huggingface.co/datasets/Horusprg/censo-2015-2024/resolve/main/INSE_2021_escolas.csv"
    ]
    
    df = None
    
    for url in urls:
        try:
            print(f"\n🔄 Tentando: {url.split('/')[-1]}")
            
            # Tentar diferentes encodings
            for encoding in ['utf-8-sig', 'utf-8', 'latin1', 'iso-8859-1']:
                try:
                    # Tentar ler apenas as primeiras linhas
                    df_sample = pd.read_csv(url, encoding=encoding, nrows=5, on_bad_lines='skip')
                    print(f"   ✓ Leitura bem sucedida com encoding {encoding}")
                    
                    # Se funcionou, carregar dados (limitado)
                    if max_records:
                        df = pd.read_csv(url, encoding=encoding, nrows=max_records, low_memory=False, on_bad_lines='skip')
                    else:
                        df = pd.read_csv(url, encoding=encoding, low_memory=False, on_bad_lines='skip')
                    
                    print(f"   ✓ Dados carregados: {len(df):,} registros")
                    print(f"   ✓ Colunas: {len(df.columns)}")
                    break
                    
                except Exception as e:
                    continue
            
            if df is not None:
                break
                
        except Exception as e:
            print(f"   ✗ Falha na URL: {str(e)[:50]}")
            continue
    
    if df is None:
        print("\n❌ Não foi possível baixar o dataset via URL direta")
        print("\n💡 Alternativas:")
        print("   1. Use apenas os dados da SEEDF (recomendado)")
        print("   2. Instale datasets: pip install datasets")
        print("   3. Configure HF_TOKEN: $env:HF_TOKEN='seu_token'")
        return None
    
    # Identificar colunas
    ano_col = None
    uf_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'ano' in col_lower and not ano_col:
            ano_col = col
        if 'uf' in col_lower or 'sg_uf' in col_lower or 'estado' in col_lower:
            uf_col = col
    
    if not uf_col:
        print("\n⚠️ Coluna de UF não encontrada")
        print(f"   Colunas disponíveis: {list(df.columns)[:20]}")
        print(f"\n💡 Usando dados sem filtro de UF (todos os estados)")
        df_filtered = df
    else:
        # Filtrar por UF
        try:
            mask = df[uf_col].astype(str).str.upper() == state.upper()
            df_filtered = df[mask].copy()
            print(f"\n📊 Dados filtrados para {state}:")
            print(f"   Registros: {len(df_filtered):,}")
        except Exception as e:
            print(f"   Erro ao filtrar: {e}")
            df_filtered = df.head(max_records) if max_records else df
    
    if len(df_filtered) == 0:
        print("   ⚠️ Nenhum registro encontrado para a UF especificada")
        print("   Usando amostra dos dados sem filtro")
        df_filtered = df.head(10000)
    
    # Salvar dados
    os.makedirs('data/raw', exist_ok=True)
    file_path = 'data/raw/censo_df.csv'
    df_filtered.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    # Salvar metadados
    info = {
        'fonte': 'Hugging Face - Horusprg/censo-2015-2024',
        'uf_filtrada': state,
        'total_registros': len(df_filtered),
        'colunas': list(df_filtered.columns),
        'anos_disponiveis': sorted(df_filtered[ano_col].unique().tolist()) if ano_col else [],
        'data_extracao': datetime.now().isoformat()
    }
    
    import json
    with open('data/raw/censo_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados salvos em: {file_path}")
    print(f"   Metadados: data/raw/censo_metadata.json")
    
    return file_path

def extract_with_datasets_library(state='DF', max_records=50000):
    """
    Extrai usando a biblioteca 'datasets' (requer instalação)
    """
    
    print("\n🔄 Tentando extração com biblioteca 'datasets'...")
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("   ❌ Biblioteca 'datasets' não instalada")
        print("   Instale com: pip install datasets")
        return None
    
    try:
        print("   Carregando dataset (pode levar alguns minutos)...")
        
        if max_records:
            dataset = load_dataset("Horusprg/censo-2015-2024", split=f"train[:{max_records}]", trust_remote_code=True)
        else:
            dataset = load_dataset("Horusprg/censo-2015-2024", split="train", trust_remote_code=True)
        
        # Converter para pandas
        df = dataset.to_pandas()
        
        print(f"   Registros totais: {len(df):,}")
        
        # Filtrar por UF
        uf_col = None
        for col in df.columns:
            if col.lower() in ['uf', 'sg_uf', 'estado']:
                uf_col = col
                break
        
        if uf_col:
            df_filtered = df[df[uf_col] == state].copy()
            print(f"   Registros para {state}: {len(df_filtered):,}")
        else:
            df_filtered = df
        
        # Salvar
        os.makedirs('data/raw', exist_ok=True)
        file_path = 'data/raw/censo_df.csv'
        df_filtered.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ Dados salvos em: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Extrai dados do Censo Escolar (OPCIONAL)')
    parser.add_argument('--state', type=str, default='DF', help='UF a ser filtrada (ex: DF, SP, RJ)')
    parser.add_argument('--max-records', type=int, default=100000, help='Número máximo de registros')
    parser.add_argument('--method', type=str, choices=['direct', 'datasets', 'auto'], 
                       default='auto', help='Método de extração')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🚀 Extrator de Dados - Censo Escolar (OPCIONAL)")
    print("=" * 60)
    print(f"⚠️  Este script é OPCIONAL")
    print(f"   Os dados principais já são obtidos via SEEDF")
    print(f"   Use apenas se precisar de dados complementares")
    print(f"   Para o dashboard funcionar, execute apenas o transform.py\n")
    
    resposta = input("Deseja continuar com a extração? (s/N): ")
    if resposta.lower() != 's':
        print("\n✅ Extração cancelada. O dashboard funcionará com os dados do transform.py")
        print("   Execute: python scripts/transform.py")
        return
    
    file_path = None
    
    if args.method == 'direct' or args.method == 'auto':
        file_path = extract_censo_escolar_simple(state=args.state, max_records=args.max_records)
    
    if file_path is None and (args.method == 'datasets' or args.method == 'auto'):
        file_path = extract_with_datasets_library(state=args.state, max_records=args.max_records)
    
    if file_path:
        print("\n" + "=" * 60)
        print("✅ EXTRAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print(f"\n📁 Arquivo: {file_path}")
        print("\n💡 Agora execute: python scripts/transform.py")
        print("   (O transform.py combinará os dados da SEEDF com o Censo)")
    else:
        print("\n" + "=" * 60)
        print("⚠️ EXTRAÇÃO NÃO REALIZADA")
        print("=" * 60)
        print("\n💡 Recomendação:")
        print("   Use apenas os dados da SEEDF, que são suficientes para o dashboard:")
        print("   1. python scripts/extract_data_se_df.py")
        print("   2. python scripts/transform.py")
        print("   3. streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()