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
    total_entrada = df[df['Tipo'] == 'Entrada']['Valor'].sum()
    total_saida = df[df['Tipo'] == 'Saída']['Valor'].sum()
    lucro = total_entrada - total_saida

    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Total", f"R$ {total_entrada:,.2f}")
    c2.metric("Despesas Totais", f"R$ {total_saida:,.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Status do Lucro:** {'🟢 Saudável' if lucro > 0 else '🔴 Atenção'}")
    c3.metric(
        "Lucro Líquido", 
        f"R$ {lucro:,.2f}", 
        delta=f"R$ {lucro:,.2f}", 
        delta_color="normal" if lucro >= 0 else "inverse"
    )

    st.markdown("---")

    # --- GRÁFICOS ---
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("📈 Evolução no Tempo")
        fig_evolucao = px.line(
            df.sort_values('Data'), 
            x='Data', 
            y='Valor', 
            color='Tipo', 
            markers=True, 
            template="plotly_dark", 
            color_discrete_map={"Entrada": "#00CC96", "Saída": "#EF553B"}
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

    with col_dir:
        st.subheader("🍕 Distribuição de Despesas")
        df_saidas = df[df['Tipo'] == 'Saída']
        if not df_saidas.empty:
            fig_pizza = px.pie(df_saidas, values='Valor', names='Categoria', hole=0.5, template="plotly_dark")
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.warning("Nenhuma despesa registrada para os filtros selecionados.")

    st.markdown("---")
    
    # --- TABELA DETALHADA ---
    st.subheader("📋 Detalhamento dos Lançamentos")
    
    df_display = df.copy()
    df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y')
    
    col_tab, col_btn = st.columns([4, 1])
    
    with col_tab:
        st.dataframe(
            df_display.sort_values(by="Data", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )

    with col_btn:
        st.write("###")
        csv_ready = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados (CSV)",
            data=csv_ready,
            file_name=f"relatorio_financeiro.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    
    st.info("👋 Bem-vindo! Por favor, suba sua planilha CSV na barra lateral para gerar os insights financeiros.")
    st.markdown("---")
    
    col_texto, col_imagem = st.columns([1, 2])
    
    with col_texto:
        st.subheader("📋 Instruções da Planilha")
        st.markdown("""
            Para o sistema funcionar, seu arquivo CSV deve ter estas colunas:
            - **Data**: Ex: 15/03/2026
            - **Categoria**: Ex: Aluguel, Vendas, Salários
            - **Tipo**: Use apenas 'Entrada' ou 'Saída'
            - **Valor**: Use números (ex: 1250.50)
            
            *Dica: Evite acentos nos cabeçalhos e não mescle células.*
        """)
        
    with col_imagem:
        st.subheader("🖼️ Exemplo do Formato Correto")
        # Certifique-se de que o arquivo abaixo foi enviado via 'Upload' no GitHub
        st.image("imagem_planilha.png", caption="Modelo de estrutura aceita pelo RaloZero", use_container_width=True)
