import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Dashboard MR10 - Gestão de Lojas", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Desempenho - MR10")
st.markdown("Acompanhamento diário e gerencial das 7 lojas da coordenação MR10 (Dicere Telecom).")

# Sidebar for store selection
stores = [
    "Consolidado MR10",
    "10_ESTEIO",
    "10_IGREJINHA",
    "10_MOINHOS",
    "10_PAROBE",
    "10_SAPUCAIA CALCADAO",
    "10_SAPUCAIA MATRIZ",
    "10_TAQUARA"
]

selected_store = st.sidebar.selectbox("Selecione a Loja ou Consolidado", stores)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica:** Utilize os filtros para analisar o acumulado do mês, metas, projeções e indicadores de MoM e M3.")

# Sample summary data structure based on uploaded prints
data_summary = {
    "Loja": ["Est. Esteio", "Est. Igrejinha", "Est. Moinhos", "Est. Parobé", "Est. Sapucaia Calçadão", "Est. Sapucaia Matriz", "Est. Taquara"],
    "Faturamento Meta": [41000, 24000, 61000, 36000, 46000, 59000, 36000],
    "Faturamento Real": [17015, 13093, 22364, 14306, 28397, 42181, 26030],
    "Faturamento Proj": [29776, 22913, 39566, 25035, 49694, 73817, 45553],
    "Venda TV Real": [2, 4, 5, 3, 4, 16, 12],
    "Venda Virtua Real": [12, 5, 6, 6, 18, 19, 16],
    "Aparelhos Qtde Real": [12, 3, 28, 11, 14, 17, 8]
}

df_stores = pd.DataFrame(data_summary)

if selected_store == "Consolidado MR10":
    st.header("Visão Consolidada - MR10 (7 Lojas)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_meta = df_stores["Faturamento Meta"].sum()
        total_real = df_stores["Faturamento Real"].sum()
        st.metric("Faturamento Realizado", f"R$ {total_real:,.2f}", f"Meta: R$ {total_meta:,.2f}")
    with col2:
        total_tv = df_stores["Venda TV Real"].sum()
        st.metric("Vendas de TV (Total)", f"{total_tv} un.")
    with col3:
        total_virtua = df_stores["Venda Virtua Real"].sum()
        st.metric("Vendas de Vírtua (Total)", f"{total_virtua} un.")
    with col4:
        total_ap = df_stores["Aparelhos Qtde Real"].sum()
        st.metric("Aparelhos Vendidos", f"{total_ap} un.")
        
    st.markdown("---")
    st.subheader("Desempenho de Faturamento por Loja")
    st.bar_chart(df_stores.set_index("Loja")[["Faturamento Real", "Faturamento Meta"]])

else:
    st.header(f"Painel Detalhado: {selected_store}")
    # Filter for specific store
    store_idx = stores.index(selected_store) - 1
    store_row = df_stores.iloc[store_idx]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Realizado", f"R$ {store_row['Faturamento Real']:,.2f}", f"Meta: R$ {store_row['Faturamento Meta']:,.2f}")
    c2.metric("Projeção de Fechamento", f"R$ {store_row['Faturamento Proj']:,.2f}")
    c3.metric("Atingimento", f"{(store_row['Faturamento Real']/store_row['Faturamento Meta'])*100:.1f}%")
    
    st.markdown("---")
    st.subheader("Indicadores Principais (Realizados)")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Venda de TV", f"{store_row['Venda TV Real']} un.")
    col_b.metric("Venda de Vírtua", f"{store_row['Venda Virtua Real']} un.")
    col_c.metric("Aparelhos (Qtde)", f"{store_row['Aparelhos Qtde Real']} un.")

st.markdown("---")
st.caption("Desenvolvido para Gestão de Vendas MR10 — Dicere Telecom | Atualizado com base nos prints diários.")
