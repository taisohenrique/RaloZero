import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração de alto nível
st.set_page_config(page_title="Gestão Financeira BlackBelt", layout="wide", page_icon="📊")

# Custom CSS para melhorar a estética
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.header("🔧 Configurações")
uploaded_file = st.sidebar.file_uploader("Suba sua planilha (CSV)", type="csv")

st.title("📊 Painel de Saúde Financeira")

if uploaded_file:
    # --- 1. CARREGAMENTO COM TRATAMENTO DE ERROS (UTF-8 e LATIN-1) ---
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python')
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='latin-1', sep=None, engine='python')
    
    # Converter Data garantindo o formato brasileiro
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
    
    # --- BARRA LATERAL COM FILTROS ---
    st.sidebar.subheader("Filtros")
    
    # Filtro de Data
    data_min = df['Data'].min().to_pydatetime()
    data_max = df['Data'].max().to_pydatetime()
    intervalo = st.sidebar.date_input("Selecione o período", [data_min, data_max])

    # --- CORREÇÃO DO ERRO DE CATEGORIA ---
    categorias_unicas = df['Categoria'].dropna().astype(str).unique()
    categorias = ["Todas"] + sorted(list(categorias_unicas))
    cat_selecionada = st.sidebar.selectbox("Filtrar por Categoria", categorias)

    # Aplicação dos Filtros de Data
    if isinstance(intervalo, (list, tuple)) and len(intervalo) == 2:
        df = df[(df['Data'] >= pd.to_datetime(intervalo[0])) & (df['Data'] <= pd.to_datetime(intervalo[1]))]
    
    # Aplicação do Filtro de Categoria
    if cat_selecionada != "Todas":
        df = df[df['Categoria'] == cat_selecionada]

    # --- MÉTRICAS ---
    total_
