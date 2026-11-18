import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Dashboard Gerencial MR10 | Dicere Telecom",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS customizada para visual executivo
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.title("📊 Dashboard Gerencial - Coordenação MR10")
st.markdown("**Dicere Telecom** | Acompanhamento de Desempenho e Indicadores Comerciais das 7 Lojas")
st.markdown("---")

# Dados estruturados das 7 lojas da MR10
data_stores = [
    {
        "Loja": "10_ESTEIO", "Gerente": "Emily",
        "Meta_Fat": 41000, "Real_Fat": 17015, "Proj_Fat": 29776,
        "Meta_TV": 12, "Real_TV": 2, "Meta_Virtua": 22, "Real_Virtua": 12,
        "Meta_Aparelho": 34, "Real_Aparelho": 12, "Controle": 31, "Seguros": 3, "Up_Plano": 30
    },
    {
        "Loja": "10_IGREJINHA", "Gerente": "Carolina",
        "Meta_Fat": 24000, "Real_Fat": 13093, "Proj_Fat": 22913,
        "Meta_TV": 8, "Real_TV": 4, "Meta_Virtua": 18, "Real_Virtua": 5,
        "Meta_Aparelho": 24, "Real_Aparelho": 3, "Controle": 26, "Seguros": 1, "Up_Plano": 10
    },
    {
        "Loja": "10_MOINHOS", "Gerente": "Cleonice",
        "Meta_Fat": 61000, "Real_Fat": 22364, "Proj_Fat": 39566,
        "Meta_TV": 20, "Real_TV": 5, "Meta_Virtua": 34, "Real_Virtua": 6,
        "Meta_Aparelho": 44, "Real_Aparelho": 28, "Controle": 9, "Seguros": 9, "Up_Plano": 32
    },
    {
        "Loja": "10_PAROBE", "Gerente": "Nagai",
        "Meta_Fat": 36000, "Real_Fat": 14306, "Proj_Fat": 25035,
        "Meta_TV": 12, "Real_TV": 3, "Meta_Virtua": 22, "Real_Virtua": 6,
        "Meta_Aparelho": 34, "Real_Aparelho": 11, "Controle": 36, "Seguros": 3, "Up_Plano": 10
    },
    {
        "Loja": "10_SAPUCAIA_CALCADAO", "Gerente": "Barbara",
        "Meta_Fat": 46000, "Real_Fat": 28397, "Proj_Fat": 49694,
        "Meta_TV": 10, "Real_TV": 4, "Meta_Virtua": 22, "Real_Virtua": 18,
        "Meta_Aparelho": 34, "Real_Aparelho": 14, "Controle": 41, "Seguros": 6, "Up_Plano": 45
    },
    {
        "Loja": "10_SAPUCAIA_MATRIZ", "Gerente": "Cassia",
        "Meta_Fat": 59000, "Real_Fat": 42181, "Proj_Fat": 73817,
        "Meta_TV": 16, "Real_TV": 16, "Meta_Virtua": 32, "Real_Virtua": 19,
        "Meta_Aparelho": 50, "Real_Aparelho": 17, "Controle": 44, "Seguros": 14, "Up_Plano": 29
    },
    {
        "Loja": "10_TAQUARA", "Gerente": "Eduarda",
        "Meta_Fat": 36000, "Real_Fat": 26030, "Proj_Fat": 45553,
        "Meta_TV": 12, "Real_TV": 12, "Meta_Virtua": 22, "Real_Virtua": 16,
        "Meta_Aparelho": 34, "Real_Aparelho": 8, "Controle": 25, "Seguros": 16, "Up_Plano": 25
    }
]

df = pd.DataFrame(data_stores)

# Sidebar - Filtros e Seleção
st.sidebar.header("🔍 Filtros de Navegação")
selected_view = st.sidebar.radio("Visualizar por:", ["Visão Consolidada MR10", "Análise Individual por Loja"])

if selected_view == "Visão Consolidada MR10":
    st.header("📈 Visão Consolidada - MR10 (7 Lojas)")
    
    # Métricas Globais
    col1, col2, col3, col4 = st.columns(4)
    tot_meta = df["Meta_Fat"].sum()
    tot_real = df["Real_Fat"].sum()
    tot_proj = df["Proj_Fat"].sum()
    ating_geral = (tot_real / tot_meta) * 100
    
    col1.metric("Faturamento Realizado", f"R$ {tot_real:,.2f}", f"Meta: R$ {tot_meta:,.2f}")
    col2.metric("Projeção de Fechamento", f"R$ {tot_proj:,.2f}", f"Ating.: {(tot_proj/tot_meta)*100:.1f}%")
    col3.metric("Vendas de TV (Total)", f"{df['Real_TV'].sum()} un.", f"Meta: {df['Meta_TV'].sum()} un.")
    col4.metric("Vendas de Vírtua (Total)", f"{df['Real_Virtua'].sum()} un.", f"Meta: {df['Meta_Virtua'].sum()} un.")
    
    st.markdown("---")
    
    # Tabela Resumo Consolidada
    st.subheader("📋 Resumo de Desempenho por Unidade")
    df_display = df[["Loja", "Gerente", "Meta_Fat", "Real_Fat", "Proj_Fat"]].copy()
    df_display["% Atingimento"] = (df_display["Real_Fat"] / df_display["Meta_Fat"]) * 100
    df_display["% Atingimento"] = df_display["% Atingimento"].apply(lambda x: f"{x:.1f}%")
    df_display["Meta_Fat"] = df_display["Meta_Fat"].apply(lambda x: f"R$ {x:,.2f}")
    df_display["Real_Fat"] = df_display["Real_Fat"].apply(lambda x: f"R$ {x:,.2f}")
    df_display["Proj_Fat"] = df_display["Proj_Fat"].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Comparativo de Faturamento: Realizado vs Meta")
    st.bar_chart(df.set_index("Loja")[["Real_Fat", "Meta_Fat"]])

else:
    st.header("🏪 Análise Detalhada por Unidade")
    store_selected = st.sidebar.selectbox("Selecione a Loja:", df["Loja"].tolist())
    
    row = df[df["Loja"] == store_selected].iloc[0]
    
    st.subheader(f"Loja: {row['Loja']} | Gerente: {row['Gerente']}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Realizado", f"R$ {row['Real_Fat']:,.2f}", f"Meta: R$ {row['Meta_Fat']:,.2f}")
    c2.metric("Projeção de Fechamento", f"R$ {row['Proj_Fat']:,.2f}")
    c3.metric("Atingimento da Meta", f"{(row['Real_Fat']/row['Meta_Fat'])*100:.1f}%")
    
    st.markdown("---")
    st.subheader("🎯 Indicadores de Pilares e KPIs")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Vendas de TV", f"{row['Real_TV']} un.", f"Meta: {row['Meta_TV']}")
    col_b.metric("Vendas de Vírtua", f"{row['Real_Virtua']} un.", f"Meta: {row['Meta_Virtua']}")
    col_c.metric("Ativações Controle", f"{row['Controle']} un.")
    col_d.metric("Seguros Vendidos", f"{row['Seguros']} un.")
    
    col_e, col_f = st.columns(2)
    col_e.metric("Aparelhos (Qtd)", f"{row['Real_Aparelho']} un.", f"Meta: {row['Meta_Aparelho']}")
    col_f.metric("Upgrades de Plano", f"{row['Up_Plano']} un.")

st.markdown("---")
st.caption("🚀 Painel Gerencial MR10 — Desenvolvido para Gestão de Vendas Dicere Telecom.")
