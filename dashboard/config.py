
Agora, crie também o arquivo de configuração para complementar:

```python
# dashboard/config.py
import streamlit as st

# Cores do tema
COLORS = {
    "primary": "#1e3c72",
    "secondary": "#2a5298",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "success": "#10b981",
    "info": "#3b82f6",
    "dark": "#1f2937",
    "light": "#f3f4f6"
}

# Configurações de gráficos
CHART_CONFIG = {
    "height": 400,
    "template": "plotly_white",
    "margin": dict(l=50, r=50, t=50, b=50)
}

# Labels e textos
TEXTS = {
    "app_title": "Evasão Escolar no Distrito Federal",
    "app_subtitle": "Análise completa baseada nos dados do Censo Escolar INEP/SEEDF",
    "period_analyzed": "Período analisado: 2015-2024",
    "footer_text": "Dashboard desenvolvido para o Projeto Integrador - Ciência de Dados",
    "data_sources": "Fonte: Censo Escolar INEP/SEEDF + Hugging Face Dataset"
}

def get_custom_theme():
    """Retorna tema customizado para o Plotly"""
    return {
        "layout": {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "Arial, sans-serif", "size": 12},
            "title": {"font": {"size": 16, "weight": "bold"}},
            "xaxis": {"gridcolor": "#e5e7eb", "showgrid": True},
            "yaxis": {"gridcolor": "#e5e7eb", "showgrid": True}
        }
    }