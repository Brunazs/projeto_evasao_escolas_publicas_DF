# scripts/extract_policy_data.py
"""
Extração de dados sobre políticas públicas educacionais:
- Programa Pé-de-Meia (incentivo financeiro)
- Estratégia Nacional de Escolas Conectadas (infraestrutura digital)

Fontes oficiais:
- MEC: https://www.gov.br/mec/pt-br
- Portal da Transparência: https://www.portaldatransparencia.gov.br/
"""

import pandas as pd
import argparse
import os
import json
from datetime import datetime

# ============================================================================
# DADOS DO PROGRAMA PÉ-DE-MEIA (Fonte: MEC/Agência Brasil, 2026)
# ============================================================================
PEDEMEIA_DATA = {
    'programa': 'Pé-de-Meia',
    'lei': 'Lei nº 14.818/2024',
    'descricao': 'Incentivo financeiro para estudantes do ensino médio público',
    'beneficios': {
        'mensal': 200,
        'anual_conclusao': 1000,
        'enem': 'Bônus adicional'
    },
    'condicoes': 'Frequência mínima de 80%',
    'beneficiarios_por_uf': {
        'AC': 29735, 'AL': 72019, 'AM': 97415, 'AP': 23848, 'BA': 306035,
        'CE': 217301, 'DF': 61943, 'ES': 53275, 'GO': 102341, 'MA': 224544,
        'MG': 371609, 'MS': 51421, 'MT': 77222, 'PA': 173516, 'PB': 102848,
        'PE': 202030, 'PI': 104298, 'PR': 219481, 'RJ': 252492, 'RN': 82523,
        'RO': 35443, 'RR': 19965, 'RS': 216684, 'SC': 133120, 'SE': 59033,
        'SP': 660022, 'TO': 33639
    },
    'total_brasil': 4012854,
    'taxas_evasao': {
        2022: 6.4,  # Antes do programa
        2023: 5.8,  # Transição
        2024: 3.6   # Após implementação completa
    },
    'reducao_evasao': 43,  # Percentual de redução (6.4% → 3.6%)
    'investimento_total': 18.6,  # Bilhões de reais
    'periodo_implementacao': '2024-2025',
    'fonte': 'MEC - Assessoria de Comunicação Social, março/2026 '
}

# ============================================================================
# DADOS DA ESTRATÉGIA ESCOLAS CONECTADAS (Fonte: MEC/SEB, 2026)
# ============================================================================
ESCOLAS_CONECTADAS_DATA = {
    'programa': 'Estratégia Nacional de Escolas Conectadas (Enec)',
    'decreto': 'Decreto nº 11.646/2023',
    'descricao': 'Universalização de internet de qualidade para uso pedagógico nas escolas públicas',
    'evolucao': {
        2023: {'percentual': 45.0, 'escolas': 45000, 'estudantes': 11000000, 'investimento_bilhoes': 0.5},
        2024: {'percentual': 55.0, 'escolas': 65000, 'estudantes': 16000000, 'investimento_bilhoes': 1.2},
        2025: {'percentual': 65.0, 'escolas': 85000, 'estudantes': 21000000, 'investimento_bilhoes': 2.1},
        2026: {'percentual': 71.7, 'escolas': 99005, 'estudantes': 24000000, 'investimento_bilhoes': 3.0}
    },
    'metas': {
        '2026': 71.7,   # Percentual alcançado
        '2027': 80.0,   # Meta projetada
        '2030': 100.0   # Universalização
    },
    'investimento_total_bilhoes': 3.0,
    'periodo': '2023-2026',
    'fonte': 'MEC - Secretaria de Educação Básica, março/2026 '
}

# ============================================================================
# FUNÇÕES DE EXTRAÇÃO
# ============================================================================

def extract_pe_de_meia_data():
    """
    Extrai e estrutura dados do Programa Pé-de-Meia
    
    O programa, instituído pela Lei nº 14.818/2024, oferece:
    - R$ 200/mês condicionado à frequência mínima de 80%
    - Bônus de R$ 1.000 por ano concluído com aprovação
    - Parcela extra para participantes do ENEM
    
    Impacto nacional: redução de 43% no abandono escolar 
    """
    
    print("\n" + "=" * 60)
    print("💰 Extraindo dados do Programa Pé-de-Meia")
    print("=" * 60)
    
    # Criar DataFrame de beneficiários por UF
    df_beneficiarios = pd.DataFrame([
        {'uf': uf, 'beneficiarios': benef}
        for uf, benef in PEDEMEIA_DATA['beneficiarios_por_uf'].items()
    ])
    df_beneficiarios = df_beneficiarios.sort_values('beneficiarios', ascending=False)
    
    # Criar DataFrame de evasão temporal
    df_evasao_temporal = pd.DataFrame([
        {'ano': ano, 'taxa_evasao_nacional': taxa, 'programa_ativo': ano >= 2024}
        for ano, taxa in PEDEMEIA_DATA['taxas_evasao'].items()
    ])
    
    # Criar DataFrame de indicadores do programa
    df_indicadores = pd.DataFrame([
        {'indicador': 'Redução do Abandono Escolar', 'valor': '43%', 'periodo': '2022 → 2024'},
        {'indicador': 'Queda na Reprovação', 'valor': '33%', 'periodo': '2022 → 2024'},
        {'indicador': 'Redução da Distorção Idade-Série', 'valor': '27.5%', 'periodo': '2022 → 2024'},
        {'indicador': 'Investimento Total', 'valor': 'R$ 18,6 bilhões', 'periodo': '2024-2025'},
        {'indicador': 'Total de Beneficiários', 'valor': '4.012.854', 'periodo': '2025'},
        {'indicador': 'Beneficiários no DF', 'valor': '61.943', 'periodo': '2025'},
        {'indicador': 'Cobertura no DF', 'valor': '47,7%', 'periodo': '2025'}
    ])
    
    # Salvar dados
    os.makedirs('data/raw', exist_ok=True)
    
    df_beneficiarios.to_csv('data/raw/pe_de_meia_beneficiarios.csv', index=False)
    df_evasao_temporal.to_csv('data/raw/pe_de_meia_evasao_temporal.csv', index=False)
    df_indicadores.to_csv('data/raw/pe_de_meia_indicadores.csv', index=False)
    
    # Salvar métricas de impacto em JSON
    impacto = {
        'programa': PEDEMEIA_DATA['programa'],
        'lei': PEDEMEIA_DATA['lei'],
        'reducao_percentual': PEDEMEIA_DATA['reducao_evasao'],
        'taxa_antes': PEDEMEIA_DATA['taxas_evasao'][2022],
        'taxa_depois': PEDEMEIA_DATA['taxas_evasao'][2024],
        'investimento_bilhoes': PEDEMEIA_DATA['investimento_total'],
        'beneficiarios_df': PEDEMEIA_DATA['beneficiarios_por_uf']['DF'],
        'total_beneficiarios': PEDEMEIA_DATA['total_brasil'],
        'fonte': PEDEMEIA_DATA['fonte'],
        'data_extracao': datetime.now().isoformat()
    }
    
    with open('data/raw/pe_de_meia_impacto.json', 'w', encoding='utf-8') as f:
        json.dump(impacto, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados do Pé-de-Meia extraídos:")
    print(f"   - Beneficiários: {impacto['total_beneficiarios']:,} (nacional)")
    print(f"   - Beneficiários no DF: {impacto['beneficiarios_df']:,}")
    print(f"   - Redução nacional: {impacto['reducao_percentual']}% no abandono")
    print(f"   - Período: {PEDEMEIA_DATA['periodo_implementacao']}")
    
    return df_beneficiarios, impacto

def extract_escolas_conectadas_data():
    """
    Extrai dados da Estratégia Nacional de Escolas Conectadas (Enec)
    
    Lançada em setembro de 2023, a Enec busca:
    - Universalizar internet de qualidade para uso pedagógico
    - Promover educação digital e midiática
    - Formar professores para uso de tecnologia
    
    Avanços: 71,7% das escolas com conectividade adequada em 2026 
    """
    
    print("\n" + "=" * 60)
    print("🖧 Extraindo dados da Estratégia Escolas Conectadas")
    print("=" * 60)
    
    # Criar DataFrame de evolução
    dados_evolucao = []
    for ano, dados in ESCOLAS_CONECTADAS_DATA['evolucao'].items():
        dados_evolucao.append({
            'ano': ano,
            'percentual_conectividade': dados['percentual'],
            'escolas_conectadas': dados['escolas'],
            'estudantes_beneficiados': dados['estudantes'],
            'investimento_acumulado_bilhoes': dados['investimento_bilhoes']
        })
    
    df_evolucao = pd.DataFrame(dados_evolucao)
    
    # Criar DataFrame de metas
    df_metas = pd.DataFrame([
        {'ano': ano, 'meta_conectividade_percentual': meta}
        for ano, meta in ESCOLAS_CONECTADAS_DATA['metas'].items()
    ])
    
    # Salvar dados
    os.makedirs('data/raw', exist_ok=True)
    
    df_evolucao.to_csv('data/raw/escolas_conectadas_evolucao.csv', index=False)
    df_metas.to_csv('data/raw/escolas_conectadas_metas.csv', index=False)
    
    # Salvar métricas de impacto em JSON
    impacto = {
        'programa': ESCOLAS_CONECTADAS_DATA['programa'],
        'decreto': ESCOLAS_CONECTADAS_DATA['decreto'],
        'escolas_conectadas_2026': ESCOLAS_CONECTADAS_DATA['evolucao'][2026]['escolas'],
        'percentual_conectividade_2026': ESCOLAS_CONECTADAS_DATA['evolucao'][2026]['percentual'],
        'estudantes_beneficiados': ESCOLAS_CONECTADAS_DATA['evolucao'][2026]['estudantes'],
        'investimento_total_bilhoes': ESCOLAS_CONECTADAS_DATA['investimento_total_bilhoes'],
        'crescimento_percentual': ESCOLAS_CONECTADAS_DATA['evolucao'][2026]['percentual'] - ESCOLAS_CONECTADAS_DATA['evolucao'][2023]['percentual'],
        'fonte': ESCOLAS_CONECTADAS_DATA['fonte'],
        'data_extracao': datetime.now().isoformat()
    }
    
    with open('data/raw/escolas_conectadas_impacto.json', 'w', encoding='utf-8') as f:
        json.dump(impacto, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados do Escolas Conectadas extraídos:")
    print(f"   - Crescimento: {impacto['crescimento_percentual']:.1f} p.p. (2023 → 2026)")
    print(f"   - Escolas conectadas: {impacto['escolas_conectadas_2026']:,}")
    print(f"   - Estudantes beneficiados: {impacto['estudantes_beneficiados']:,}")
    print(f"   - Investimento: R$ {impacto['investimento_total_bilhoes']} bilhões")
    
    return df_evolucao, impacto

def extract_all():
    """Executa extração de todos os programas"""
    
    print("\n" + "=" * 60)
    print("🚀 Iniciando extração de dados de políticas públicas educacionais")
    print("=" * 60)
    
    # Extrair Pé-de-Meia
    pe_df, pe_impacto = extract_pe_de_meia_data()
    
    # Extrair Escolas Conectadas
    ec_df, ec_impacto = extract_escolas_conectadas_data()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA EXTRAÇÃO")
    print("=" * 60)
    print(f"""
    ✅ Programas extraídos com sucesso:
    
    1. Pé-de-Meia
       - Beneficiários no DF: {pe_impacto['beneficiarios_df']:,}
       - Redução nacional da evasão: {pe_impacto['reducao_percentual']}%
       
    2. Escolas Conectadas (Enec)
       - Escolas conectadas: {ec_impacto['escolas_conectadas_2026']:,}
       - Estudantes beneficiados: {ec_impacto['estudantes_beneficiados']:,}
    
    📁 Arquivos salvos em: data/raw/
       - pe_de_meia_beneficiarios.csv
       - pe_de_meia_evasao_temporal.csv
       - pe_de_meia_indicadores.csv
       - pe_de_meia_impacto.json
       - escolas_conectadas_evolucao.csv
       - escolas_conectadas_metas.csv
       - escolas_conectadas_impacto.json
    """)
    
    return pe_df, ec_df

def main():
    parser = argparse.ArgumentParser(description='Extrai dados de políticas públicas educacionais')
    parser.add_argument('--program', 
                       choices=['pe-de-meia', 'escolas-conectadas', 'all'], 
                       default='all',
                       help='Programa a ser extraído')
    
    args = parser.parse_args()
    
    if args.program == 'pe-de-meia':
        extract_pe_de_meia_data()
    elif args.program == 'escolas-conectadas':
        extract_escolas_conectadas_data()
    else:
        extract_all()

if __name__ == "__main__":
    main()