import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard MR10", layout="wide")

st.title("📊 Dashboard Gerencial & Performance - Coordenação MR10")

# Conexão direta com o Google Sheets da MR10
@st.cache_data(ttl=600)
def load_data_from_gsheets():
    # Substitua pelo link de exportação CSV da sua planilha do Google Sheets ou use st.connection
    sheet_url = "https://docs.google.com/spreadsheets/d/1nQObLsq9WLZQn8YaKYK0nGeMRXbiwUFt/edit?gid=292568011#gid=292568011"
    df = pd.read_csv(sheet_url)
    return df

# Se preferir usar o st.connection nativo do Streamlit:
# conn = st.connection("gsheets", type=GsheetsConnection)
# df_sellers = conn.read(worksheet="Performance")