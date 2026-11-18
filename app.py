import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Dashboard Gerencial MR10 | Dicere Telecom",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Gerencial & Performance - Coordenação MR10")
st.markdown("**Dicere Telecom** | Acompanhamento de Lojas, Gerentes, Vendedores e Última Venda no Balcão")
st.markdown("---")

# Dados das Lojas e Metas
data_stores = [
    {"Loja": "10_ESTEIO", "Gerente": "Emily", "Meta_Fat": 41000, "Real_Fat": 17015, "Proj_Fat": 29776, "Meta_TV": 12, "Real_TV": 2, "Meta_Virtua": 22, "Real_Virtua": 12},
    {"Loja": "10_IGREJINHA", "Gerente": "Carolina", "Meta_Fat": 24000, "Real_Fat": 13093, "Proj_Fat": 22913, "Meta_TV": 8, "Real_TV": 4, "Meta_Virtua": 18, "Real_Virtua": 5},
    {"Loja": "10_MOINHOS", "Gerente": "Cleonice", "Meta_Fat": 61000, "Real_Fat": 22364, "Proj_Fat": 39566, "Meta_TV": 20, "Real_TV": 5, "Meta_Virtua": 34, "Real_Virtua": 6},
    {"Loja": "10_PAROBE", "Gerente": "Nagai", "Meta_Fat": 36000, "Real_Fat": 14306, "Proj_Fat": 25035, "Meta_TV": 12, "Real_TV": 3, "Meta_Virtua": 22, "Real_Virtua": 6},
    {"Loja": "10_SAPUCAIA_CALCADAO", "Gerente": "Barbara", "Meta_Fat": 46000, "Real_Fat": 28397, "Proj_Fat": 49694, "Meta_TV": 10, "Real_TV": 4, "Meta_Virtua": 22, "Real_Virtua": 18},
    {"Loja": "10_SAPUCAIA_MATRIZ", "Gerente": "Cassia", "Meta_Fat": 59000, "Real_Fat": 42181, "Proj_Fat": 73817, "Meta_TV": 16, "Real_TV": 16, "Meta_Virtua": 32, "Real_Virtua": 19},
    {"Loja": "10_TAQUARA", "Gerente": "Eduarda", "Meta_Fat": 36000, "Real_Fat": 26030, "Proj_Fat": 45553, "Meta_TV": 12, "Real_TV": 12, "Meta_Virtua": 22, "Real_Virtua": 16}
]
df_stores = pd.DataFrame(data_stores)

# Dados de Vendedores (Processados dos relatórios vp1711 e vr_1711)
@st.cache_data
def load_seller_data():
    try:
        vp = pd.read_excel('vp1711.xlsx', sheet_name='Planilha')
        vr = pd.read_excel('vr_1711.xlsx', sheet_name='Planilha')
        vp['Data'] = pd.to_datetime(vp['Data'])
        vr['Data'] = pd.to_datetime(vr['Data'])

        s_vp = vp.groupby(['Local', 'Vendedor']).agg(
            Total_Itens=('Descrição', 'count'),
            Faturamento=('Sub-Total', 'sum'),
            Ultima_Venda_Prod=('Data', 'max')
        ).reset_index().rename(columns={'Local': 'Loja'})

        s_vr = vr.groupby(['Loja (Venda)', 'Vendedor']).agg(
            Total_Ativacoes=('Plano/Serviço', 'count'),
            Ultima_Venda_Ativ=('Data', 'max')
        ).reset_index().rename(columns={'Loja (Venda)': 'Loja'})

        df_sellers = pd.merge(s_vp, s_vr, on=['Loja', 'Vendedor'], how='outer').fillna({
            'Total_Itens': 0, 'Faturamento': 0, 'Total_Ativacoes': 0
        })
        df_sellers['Ultima_Venda'] = np.maximum(
            df_sellers['Ultima_Venda_Prod'].fillna(pd.NaT),
            df_sellers['Ultima_Venda_Ativ'].fillna(pd.NaT)
        )
        return df_sellers
    except Exception as e:
        return pd.DataFrame(columns=['Loja', 'Vendedor', 'Total_Itens', 'Faturamento', 'Total_Ativacoes', 'Ultima_Venda'])

df_sellers = load_seller_data()

# Navegação por Abas
tab1, tab2, tab3 = st.tabs(["📈 Visão Consolidada & Lojas", "🏪 Detalhamento por Unidade", "👥 Performance por Vendedor & Última Venda"])

with tab1:
    st.header("Visão Geral - Coordenação MR10")
    col1, col2, col3, col4 = st.columns(4)
    tot_meta = df_stores["Meta_Fat"].sum()
    tot_real = df_stores["Real_Fat"].sum()
    tot_proj = df_stores["Proj_Fat"].sum()
    
    col1.metric("Faturamento Realizado", f"R$ {tot_real:,.2f}", f"Meta: R$ {tot_meta:,.2f}")
    col2.metric("Projeção de Fechamento", f"R$ {tot_proj:,.2f}", f"Ating.: {(tot_proj/tot_meta)*100:.1f}%")
    col3.metric("Vendas de TV (Total)", f"{df_stores['Real_TV'].sum()} un.")
    col4.metric("Vendas de Vírtua (Total)", f"{df_stores['Real_Virtua'].sum()} un.")
    
    st.markdown("---")
    st.subheader("Desempenho de Faturamento por Loja")
    st.bar_chart(df_stores.set_index("Loja")[["Real_Fat", "Meta_Fat"]])

with tab2:
    st.header("Análise Detalhada por Loja e Gerente")
    selected_store = st.selectbox("Selecione a Loja:", df_stores["Loja"].tolist())
    row = df_stores[df_stores["Loja"] == selected_store].iloc[0]
    
    st.subheader(f"{row['Loja']} — Gerente: {row['Gerente']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Realizado", f"R$ {row['Real_Fat']:,.2f}", f"Meta: R$ {row['Meta_Fat']:,.2f}")
    c2.metric("Projeção de Fechamento", f"R$ {row['Proj_Fat']:,.2f}")
    c3.metric("Atingimento", f"{(row['Real_Fat']/row['Meta_Fat'])*100:.1f}%")
    
    st.markdown("---")
    st.subheader("Indicadores Principais")
    col_a, col_b = st.columns(2)
    col_a.metric("Venda de TV", f"{row['Real_TV']} un.", f"Meta: {row['Meta_TV']}")
    col_b.metric("Venda de Vírtua", f"{row['Real_Virtua']} un.", f"Meta: {row['Meta_Virtua']}")

with tab3:
    st.header("👥 Desempenho Individual & Data da Última Venda")
    st.markdown("Acompanhamento da atividade dos colaboradores por loja, volume de vendas, ativações e a data da última venda registrada.")
    
    if not df_sellers.empty:
        filter_loja = st.selectbox("Filtrar por Loja (Vendedores):", ["Todas"] + df_stores["Loja"].tolist())
        
        df_filtered = df_sellers if filter_loja == "Todas" else df_sellers[df_sellers["Loja"] == filter_loja]
        
        df_show = df_filtered.copy()
        df_show['Ultima_Venda'] = pd.to_datetime(df_show['Ultima_Venda']).dt.strftime('%d/%m/%Y')
        df_show['Faturamento'] = df_show['Faturamento'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_show[['Loja', 'Vendedor', 'Total_Itens', 'Faturamento', 'Total_Ativacoes', 'Ultima_Venda']], use_container_width=True)
    else:
        st.info("Nenhum dado de vendedor carregado. Certifique-se de que os arquivos de relatório estão no mesmo diretório.")

st.markdown("---")
st.caption("🚀 Painel Gerencial MR10 — Dicere Telecom | Desenvolvido com Python e Streamlit.")