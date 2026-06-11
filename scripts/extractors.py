# scripts/extractors.py

import pandas as pd
import requests
import os
import json
from datetime import datetime
from airflow.models.taskinstance import TaskInstance

# Resolve o caminho do projeto pelo próprio arquivo
# extractors.py está em: projeto/scripts/extractors.py
# PROJECT_DIR será:       projeto/
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")

def _ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)


# Tarefa 1 — SEEDF

SEEDF_URL = (
    "https://data.se.df.gov.br/dataset/situacao-do-aluno-serie-historica"
    "/resource/c196e905-11d2-4333-9a5a-e64d6a89d2bb/download/situacao_aluno.csv"
)


def extract_seedf(**context):
    ti: TaskInstance = context["ti"]

    _ensure_dirs()

    file_path = os.path.join(RAW_DIR, "situacao_aluno.csv")

    print("📥 Baixando dados da SEEDF...")

    response = requests.get(SEEDF_URL, timeout=120)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(response.content)

    print(f"✅ SEEDF salvo: {file_path}")

    ti.xcom_push(
        key="seedf_path",
        value=file_path
    )

    return file_path


# Tarefa 2 — HUGGING FACE

HF_URLS = [
    "https://huggingface.co/datasets/Horusprg/censo-2015-2024/resolve/main/BR_School_Census_2015-2024_tratado.csv",
    "https://huggingface.co/datasets/Horusprg/censo-2015-2024/resolve/main/BR_School_Census_2015-2024.csv",
]

def extract_huggingface(state: str = "DF", max_records: int = 100_000, **context):
    ti:TaskInstance=context["ti"]
    _ensure_dirs()
    df = None

    for url in HF_URLS:
        print(f"🔄 Tentando: {url.split('/')[-1]}")
        for encoding in ["utf-8-sig", "utf-8", "latin1"]:
            try:
                df = pd.read_csv(url, encoding=encoding, nrows=max_records,
                                 low_memory=False, on_bad_lines="skip")
                print(f"   ✓ encoding={encoding} | {len(df):,} registros")
                break
            except Exception:
                continue
        if df is not None:
            break

    if df is None:
        print("⚠️  Hugging Face indisponível. Pipeline continua com dados da SEEDF.")
        ti.xcom_push(key="hf_path", value=None)
        return None

    uf_col = next((c for c in df.columns if c.lower() in ["uf", "sg_uf", "estado"]), None)
    if uf_col:
        df = df[df[uf_col].astype(str).str.upper() == state.upper()].copy()
        print(f"   Registros para {state}: {len(df):,}")
    else:
        print("⚠️  Coluna de UF não encontrada — salvando sem filtro")

    file_path = os.path.join(RAW_DIR, "censo_df.csv")
    df.to_csv(file_path, index=False, encoding="utf-8-sig")

    ano_col = next((c for c in df.columns if "ano" in c.lower()), None)
    meta = {
        "fonte": "Hugging Face - Horusprg/censo-2015-2024",
        "uf_filtrada": state,
        "total_registros": len(df),
        "colunas": list(df.columns),
        "anos_disponiveis": sorted(df[ano_col].dropna().unique().tolist()) if ano_col else [],
        "data_extracao": datetime.now().isoformat(),
    }
    with open(os.path.join(RAW_DIR, "censo_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ Censo salvo: {file_path}")
    ti.xcom_push(key="hf_path", value=file_path)
    return file_path


# Tarefa 3 — POLÍTICAS PÚBLICAS

PEDEMEIA_DATA = {
    "programa": "Pé-de-Meia",
    "lei": "Lei nº 14.818/2024",
    "beneficiarios_por_uf": {
        "AC": 29735, "AL": 72019, "AM": 97415, "AP": 23848, "BA": 306035,
        "CE": 217301, "DF": 61943, "ES": 53275, "GO": 102341, "MA": 224544,
        "MG": 371609, "MS": 51421, "MT": 77222, "PA": 173516, "PB": 102848,
        "PE": 202030, "PI": 104298, "PR": 219481, "RJ": 252492, "RN": 82523,
        "RO": 35443, "RR": 19965, "RS": 216684, "SC": 133120, "SE": 59033,
        "SP": 660022, "TO": 33639,
    },
    "total_brasil": 4012854,
    "taxas_evasao": {2022: 6.4, 2023: 5.8, 2024: 3.6},
    "reducao_evasao": 43,
    "investimento_total": 18.6,
    "periodo_implementacao": "2024-2025",
    "fonte": "MEC - Assessoria de Comunicação Social, março/2026",
}

ESCOLAS_CONECTADAS_DATA = {
    "programa": "Estratégia Nacional de Escolas Conectadas (Enec)",
    "decreto": "Decreto nº 11.646/2023",
    "evolucao": {
        2023: {"percentual": 45.0, "escolas": 45000, "estudantes": 11000000, "investimento_bilhoes": 0.5},
        2024: {"percentual": 55.0, "escolas": 65000, "estudantes": 16000000, "investimento_bilhoes": 1.2},
        2025: {"percentual": 65.0, "escolas": 85000, "estudantes": 21000000, "investimento_bilhoes": 2.1},
        2026: {"percentual": 71.7, "escolas": 99005, "estudantes": 24000000, "investimento_bilhoes": 3.0},
    },
    "metas": {"2026": 71.7, "2027": 80.0, "2030": 100.0},
    "investimento_total_bilhoes": 3.0,
    "fonte": "MEC - Secretaria de Educação Básica, março/2026",
}

def extract_policy_data(**context):
    ti:TaskInstance=context["ti"]
    _ensure_dirs()

    print("💰 Extraindo dados do Pé-de-Meia...")

    df_beneficiarios = pd.DataFrame([
        {"uf": uf, "beneficiarios": v}
        for uf, v in PEDEMEIA_DATA["beneficiarios_por_uf"].items()
    ]).sort_values("beneficiarios", ascending=False)

    df_evasao = pd.DataFrame([
        {"ano": ano, "taxa_evasao_nacional": taxa, "programa_ativo": ano >= 2024}
        for ano, taxa in PEDEMEIA_DATA["taxas_evasao"].items()
    ])

    df_indicadores = pd.DataFrame([
        {"indicador": "Redução do Abandono Escolar",     "valor": "43%",        "periodo": "2022 → 2024"},
        {"indicador": "Queda na Reprovação",              "valor": "33%",        "periodo": "2022 → 2024"},
        {"indicador": "Redução da Distorção Idade-Série", "valor": "27.5%",      "periodo": "2022 → 2024"},
        {"indicador": "Investimento Total",               "valor": "R$ 18,6 bi", "periodo": "2024-2025"},
        {"indicador": "Total de Beneficiários",           "valor": "4.012.854",  "periodo": "2025"},
        {"indicador": "Beneficiários no DF",              "valor": "61.943",     "periodo": "2025"},
        {"indicador": "Cobertura no DF",                  "valor": "47,7%",      "periodo": "2025"},
    ])

    df_beneficiarios.to_csv(os.path.join(RAW_DIR, "pe_de_meia_beneficiarios.csv"), index=False)
    df_evasao.to_csv(os.path.join(RAW_DIR, "pe_de_meia_evasao_temporal.csv"), index=False)
    df_indicadores.to_csv(os.path.join(RAW_DIR, "pe_de_meia_indicadores.csv"), index=False)

    pe_impacto = {
        "programa": PEDEMEIA_DATA["programa"],
        "lei": PEDEMEIA_DATA["lei"],
        "reducao_percentual": PEDEMEIA_DATA["reducao_evasao"],
        "taxa_antes": PEDEMEIA_DATA["taxas_evasao"][2022],
        "taxa_depois": PEDEMEIA_DATA["taxas_evasao"][2024],
        "investimento_bilhoes": PEDEMEIA_DATA["investimento_total"],
        "beneficiarios_df": PEDEMEIA_DATA["beneficiarios_por_uf"]["DF"],
        "total_beneficiarios": PEDEMEIA_DATA["total_brasil"],
        "fonte": PEDEMEIA_DATA["fonte"],
        "data_extracao": datetime.now().isoformat(),
    }
    with open(os.path.join(RAW_DIR, "pe_de_meia_impacto.json"), "w", encoding="utf-8") as f:
        json.dump(pe_impacto, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Pé-de-Meia: {pe_impacto['beneficiarios_df']:,} beneficiários no DF")
    print("🖧  Extraindo dados do Escolas Conectadas...")

    df_evolucao = pd.DataFrame([
        {
            "ano": ano,
            "percentual_conectividade": d["percentual"],
            "escolas_conectadas": d["escolas"],
            "estudantes_beneficiados": d["estudantes"],
            "investimento_acumulado_bilhoes": d["investimento_bilhoes"],
        }
        for ano, d in ESCOLAS_CONECTADAS_DATA["evolucao"].items()
    ])

    df_metas = pd.DataFrame([
        {"ano": ano, "meta_conectividade_percentual": meta}
        for ano, meta in ESCOLAS_CONECTADAS_DATA["metas"].items()
    ])

    df_evolucao.to_csv(os.path.join(RAW_DIR, "escolas_conectadas_evolucao.csv"), index=False)
    df_metas.to_csv(os.path.join(RAW_DIR, "escolas_conectadas_metas.csv"), index=False)

    ec_impacto = {
        "programa": ESCOLAS_CONECTADAS_DATA["programa"],
        "decreto": ESCOLAS_CONECTADAS_DATA["decreto"],
        "escolas_conectadas_2026": ESCOLAS_CONECTADAS_DATA["evolucao"][2026]["escolas"],
        "percentual_2026": ESCOLAS_CONECTADAS_DATA["evolucao"][2026]["percentual"],
        "estudantes_beneficiados": ESCOLAS_CONECTADAS_DATA["evolucao"][2026]["estudantes"],
        "investimento_total_bilhoes": ESCOLAS_CONECTADAS_DATA["investimento_total_bilhoes"],
        "crescimento_pp": (
            ESCOLAS_CONECTADAS_DATA["evolucao"][2026]["percentual"]
            - ESCOLAS_CONECTADAS_DATA["evolucao"][2023]["percentual"]
        ),
        "fonte": ESCOLAS_CONECTADAS_DATA["fonte"],
        "data_extracao": datetime.now().isoformat(),
    }
    with open(os.path.join(RAW_DIR, "escolas_conectadas_impacto.json"), "w", encoding="utf-8") as f:
        json.dump(ec_impacto, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Escolas Conectadas: {ec_impacto['percentual_2026']}% de cobertura em 2026")

    files = [
        "pe_de_meia_beneficiarios.csv", "pe_de_meia_evasao_temporal.csv",
        "pe_de_meia_indicadores.csv",   "pe_de_meia_impacto.json",
        "escolas_conectadas_evolucao.csv", "escolas_conectadas_metas.csv",
        "escolas_conectadas_impacto.json",
    ]
    ti.xcom_push(key="policy_files", value=[os.path.join(RAW_DIR, f) for f in files])
    return files
