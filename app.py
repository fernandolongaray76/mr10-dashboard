import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Gerencial MR10 | Dicere Telecom",
    page_icon="📊",
    layout="wide"
)

# Link público CSV da planilha no Google Drive / Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQLixDs-AZos2eDJLeCdxIGkSmhzNqbSYINKUrhy0EZcDYgLH1q5SpFihHKvzpbMw/pub?output=csv"

# ==============================================================================
# FUNÇÕES AUXILIARES DE TRATAMENTO DE DADOS
# ==============================================================================
def parse_br_number(val):
    """Converte números em formato brasileiro (ex: 'R$ 9.187,90' ou '9187,90') ou padrão para float seguro."""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float, np.number)):
        return float(val)
    s = str(val).strip()
    if not s or s.lower() in ["nan", "none", "nat", "-"]:
        return 0.0
    s = s.replace("R$", "").replace(" ", "").strip()
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def format_brl(val):
    """Formata qualquer valor numérico ou texto numérico no padrão monetário brasileiro R$ 1.234,56."""
    num = parse_br_number(val)
    formatted = f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def find_column(df, candidates):
    """Localiza o nome real da coluna no DataFrame a partir de uma lista de possíveis nomes (case-insensitive)."""
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    for cand in candidates:
        for col_l, orig_col in cols_lower.items():
            if cand.lower() in col_l:
                return orig_col
    return None


@st.cache_data(ttl=300)
def load_google_sheet_data(url):
    """Lê os dados diretamente do Google Sheets (CSV público) com detecção automática de cabeçalho."""
    df = pd.read_csv(url)
    df = df.dropna(how="all")

    # Se a primeira linha for um título mesclado (gerando colunas 'Unnamed'), procura o cabeçalho real nas primeiras linhas
    unnamed_ratio = sum(1 for c in df.columns if str(c).startswith("Unnamed")) / max(len(df.columns), 1)
    if unnamed_ratio > 0.4 and len(df) > 1:
        for idx in range(min(5, len(df))):
            row_vals = [str(v).strip().lower() for v in df.iloc[idx].values if pd.notna(v)]
            if any(k in row_vals for k in ["loja", "vendedor", "indicador", "loja (venda)", "local"]):
                new_headers = [str(v).strip() if pd.notna(v) else f"Col_{i}" for i, v in enumerate(df.iloc[idx].values)]
                df = df.iloc[idx + 1:].copy()
                df.columns = new_headers
                break

    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
    df = df.dropna(how="all").reset_index(drop=True)
    return df


# ==============================================================================
# DADOS ESTRUTURAIS DAS LOJAS E GERENTES MR10
# ==============================================================================
DATA_STORES = [
    {"Loja": "10_ESTEIO", "Gerente": "Emily", "Meta_Fat": 41000.0, "Real_Fat": 17015.0, "Proj_Fat": 29776.0, "Meta_TV": 12, "Real_TV": 2, "Meta_Virtua": 22, "Real_Virtua": 12},
    {"Loja": "10_IGREJINHA", "Gerente": "Carolina", "Meta_Fat": 24000.0, "Real_Fat": 13093.0, "Proj_Fat": 22913.0, "Meta_TV": 8, "Real_TV": 4, "Meta_Virtua": 18, "Real_Virtua": 5},
    {"Loja": "10_MOINHOS", "Gerente": "Cleonice", "Meta_Fat": 61000.0, "Real_Fat": 22364.0, "Proj_Fat": 39566.0, "Meta_TV": 20, "Real_TV": 5, "Meta_Virtua": 34, "Real_Virtua": 6},
    {"Loja": "10_PAROBE", "Gerente": "Nagai", "Meta_Fat": 36000.0, "Real_Fat": 14306.0, "Proj_Fat": 25035.0, "Meta_TV": 12, "Real_TV": 3, "Meta_Virtua": 22, "Real_Virtua": 6},
    {"Loja": "10_SAPUCAIA_CALCADAO", "Gerente": "Barbara", "Meta_Fat": 46000.0, "Real_Fat": 28397.0, "Proj_Fat": 49694.0, "Meta_TV": 10, "Real_TV": 4, "Meta_Virtua": 22, "Real_Virtua": 18},
    {"Loja": "10_SAPUCAIA_MATRIZ", "Gerente": "Cassia", "Meta_Fat": 59000.0, "Real_Fat": 42181.0, "Proj_Fat": 73817.0, "Meta_TV": 16, "Real_TV": 16, "Meta_Virtua": 32, "Real_Virtua": 19},
    {"Loja": "10_TAQUARA", "Gerente": "Eduarda", "Meta_Fat": 36000.0, "Real_Fat": 26030.0, "Proj_Fat": 45553.0, "Meta_TV": 12, "Real_TV": 12, "Meta_Virtua": 22, "Real_Virtua": 16},
]
df_stores = pd.DataFrame(DATA_STORES)

# ==============================================================================
# BARRA LATERAL (CONTROLES & STATUS DA CONEXÃO)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Controle MR10")
    st.markdown("**Coordenação:** Fernando Longaray")
    st.markdown("**Unidades:** 7 Lojas (Dicere Telecom)")
    st.markdown("---")
    if st.button("🔄 Atualizar Dados Agora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Os dados são sincronizados automaticamente com a planilha do Google Drive a cada 5 minutos ou ao clicar no botão acima.")

# ==============================================================================
# CABEÇALHO PRINCIPAL E CARREGAMENTO DOS DADOS
# ==============================================================================
st.title("📊 Dashboard Gerencial & Performance — Coordenação MR10")
st.markdown("**Dicere Telecom** | Acompanhamento de Lojas, Gerentes, Vendedores e Data da Última Venda")

try:
    df_sheet = load_google_sheet_data(SHEET_CSV_URL)
    load_error = None
except Exception as e:
    df_sheet = pd.DataFrame()
    load_error = str(e)

if load_error:
    st.error(f"❌ Erro ao conectar com a planilha do Google Drive: {load_error}")
    st.info("Verifique se a planilha continua publicada na web como CSV e se há conexão com a internet.")
elif df_sheet.empty:
    st.warning("⚠️ A planilha conectada está vazia no momento.")
else:
    st.success(f"✅ Conectado ao Google Sheets — {len(df_sheet)} registros carregados em tempo real.")

st.markdown("---")

# Identificação dinâmica das colunas da planilha
col_loja = find_column(df_sheet, ["Loja", "Loja (Venda)", "Local", "Unidade"])
col_vendedor = find_column(df_sheet, ["Vendedor", "Colaborador", "Consultor", "Nome"])
col_fat = find_column(df_sheet, ["Faturamento", "Valor Venda", "Sub-Total", "Valor", "Realizado"])
col_itens = find_column(df_sheet, ["Qtd_Itens", "Total_Itens", "Itens", "Qtd", "Quantidade"])
col_ativ = find_column(df_sheet, ["Qtd_Ativacoes", "Total_Ativacoes", "Ativacoes", "Ativações"])
col_ultima = find_column(df_sheet, ["Ultima_Venda", "Última Venda", "Ultima Venda", "Data_Ultima_Venda", "Data"])

# Pré-processamento numérico seguro
if not df_sheet.empty:
    if col_fat:
        df_sheet["_fat_num"] = df_sheet[col_fat].apply(parse_br_number)
    if col_itens:
        df_sheet["_itens_num"] = df_sheet[col_itens].apply(parse_br_number)
    if col_ativ:
        df_sheet["_ativ_num"] = df_sheet[col_ativ].apply(parse_br_number)

# ==============================================================================
# NAVEGAÇÃO POR ABAS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "👥 Performance por Vendedor & Última Venda",
    "📈 Visão Consolidada & Lojas (MR10)",
    "🏪 Detalhamento por Unidade & Gerente"
])

# ------------------------------------------------------------------------------
# ABA 1: PERFORMANCE POR VENDEDOR & ÚLTIMA VENDA (DADOS DO GOOGLE DRIVE)
# ------------------------------------------------------------------------------
with tab1:
    st.header("👥 Desempenho Individual & Data da Última Venda")
    st.markdown("Rastreio em tempo real da produtividade por colaborador e última movimentação registrada no balcão.")

    if not df_sheet.empty:
        col_f1, col_f2 = st.columns(2)

        df_filtered = df_sheet.copy()

        # Filtro por Loja
        if col_loja:
            lojas_disponiveis = ["Todas"] + sorted(df_filtered[col_loja].dropna().astype(str).unique().tolist())
            loja_selecionada = col_f1.selectbox("Filtrar por Loja:", lojas_disponiveis, key="filtro_loja_vendedor")
            if loja_selecionada != "Todas":
                df_filtered = df_filtered[df_filtered[col_loja].astype(str) == loja_selecionada]

        # Filtro por Vendedor
        if col_vendedor:
            vendedores_disponiveis = ["Todos"] + sorted(df_filtered[col_vendedor].dropna().astype(str).unique().tolist())
            vendedor_selecionado = col_f2.selectbox("Filtrar por Vendedor:", vendedores_disponiveis, key="filtro_nome_vendedor")
            if vendedor_selecionado != "Todos":
                df_filtered = df_filtered[df_filtered[col_vendedor].astype(str) == vendedor_selecionado]

        # Cards de KPIs dinâmicos
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_registros = df_filtered[col_vendedor].nunique() if col_vendedor else len(df_filtered)
        kpi1.metric("Colaboradores / Registros", f"{total_registros}")

        if col_fat:
            kpi2.metric("Faturamento / Valor Total", format_brl(df_filtered["_fat_num"].sum()))
        else:
            kpi2.metric("Colunas Mapeadas", f"{len(df_filtered.columns)}")

        if col_itens:
            kpi3.metric("Total de Itens", f"{int(df_filtered['_itens_num'].sum()):,}".replace(",", "."))
        else:
            kpi3.metric("Lojas Ativas", f"{df_filtered[col_loja].nunique()}" if col_loja else "-")

        if col_ativ:
            kpi4.metric("Total de Ativações", f"{int(df_filtered['_ativ_num'].sum()):,}".replace(",", "."))
        elif col_ultima:
            ultima_dt_geral = pd.to_datetime(df_filtered[col_ultima], dayfirst=True, errors="coerce").max()
            kpi4.metric("Última Venda Registrada", ultima_dt_geral.strftime("%d/%m/%Y") if pd.notna(ultima_dt_geral) else "-")
        else:
            kpi4.metric("Status Base", "Sincronizada")

        st.markdown("---")

        # Preparar tabela de exibição limpa
        cols_to_hide = ["_fat_num", "_itens_num", "_ativ_num"]
        display_cols = [c for c in df_filtered.columns if c not in cols_to_hide]
        df_display = df_filtered[display_cols].copy()

        if col_fat and col_fat in df_display.columns:
            df_display[col_fat] = df_filtered["_fat_num"].apply(format_brl)

        # Calcular status de recência se houver coluna de Última Venda
        if col_ultima and col_ultima in df_display.columns:
            datas_parsed = pd.to_datetime(df_filtered[col_ultima], dayfirst=True, errors="coerce")
            data_ref = datas_parsed.max()
            if pd.notna(data_ref):
                def calc_status(dt):
                    if pd.isna(dt):
                        return "Sem registro"
                    dias = (data_ref - dt).days
                    if dias <= 1:
                        return "🟢 Ativo (Recente)"
                    elif dias <= 3:
                        return f"🟡 Há {dias} dias"
                    else:
                        return f"🔴 Há {dias} dias"
                df_display["Status_Atividade"] = datas_parsed.apply(calc_status)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Gráfico de Ranking por Vendedor (se houver vendedor e faturamento ou itens)
        if col_vendedor and (col_fat or col_itens):
            st.markdown("---")
            st.subheader("📊 Ranking de Performance por Vendedor")
            metric_col = "_fat_num" if col_fat else "_itens_num"
            metric_label = "Faturamento (R$)" if col_fat else "Quantidade de Itens"
            chart_df = (
                df_filtered.groupby(col_vendedor)[metric_col]
                .sum()
                .sort_values(ascending=False)
                .rename(metric_label)
            )
            st.bar_chart(chart_df)

        # Botão para download do recorte filtrado
        csv_export = df_filtered[display_cols].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Baixar Tabela Filtrada (CSV)",
            data=csv_export,
            file_name="MR10_Vendedores_Filtrado.csv",
            mime="text/csv"
        )
    else:
        st.info("Aguardando dados da planilha do Google Sheets para exibição.")

# ------------------------------------------------------------------------------
# ABA 2: VISÃO CONSOLIDADA & LOJAS (MR10)
# ------------------------------------------------------------------------------
with tab2:
    st.header("📈 Visão Geral — Coordenação MR10")
    col1, col2, col3, col4 = st.columns(4)
    tot_meta = df_stores["Meta_Fat"].sum()
    tot_real = df_stores["Real_Fat"].sum()
    tot_proj = df_stores["Proj_Fat"].sum()

    col1.metric("Faturamento Realizado", format_brl(tot_real), f"Meta: {format_brl(tot_meta)}")
    col2.metric("Projeção de Fechamento", format_brl(tot_proj), f"Ating.: {(tot_proj / tot_meta) * 100:.1f}%")
    col3.metric("Vendas de TV (Total)", f"{df_stores['Real_TV'].sum()} un.", f"Meta: {df_stores['Meta_TV'].sum()}")
    col4.metric("Vendas de Vírtua (Total)", f"{df_stores['Real_Virtua'].sum()} un.", f"Meta: {df_stores['Meta_Virtua'].sum()}")

    st.markdown("---")
    st.subheader("Comparativo Realizado vs. Meta por Loja")
    st.bar_chart(df_stores.set_index("Loja")[["Real_Fat", "Meta_Fat"]])

    st.markdown("---")
    st.subheader("Resumo Consolidado das 7 Unidades")
    df_stores_view = df_stores.copy()
    df_stores_view["Atingimento (%)"] = ((df_stores_view["Real_Fat"] / df_stores_view["Meta_Fat"]) * 100).round(1).astype(str) + "%"
    for c in ["Meta_Fat", "Real_Fat", "Proj_Fat"]:
        df_stores_view[c] = df_stores_view[c].apply(format_brl)
    st.dataframe(df_stores_view, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# ABA 3: DETALHAMENTO POR UNIDADE & GERENTE
# ------------------------------------------------------------------------------
with tab3:
    st.header("🏪 Análise Detalhada por Loja e Gerente")
    selected_store = st.selectbox("Selecione a Loja:", df_stores["Loja"].tolist(), key="select_loja_detalhe")
    row = df_stores[df_stores["Loja"] == selected_store].iloc[0]

    st.subheader(f"{row['Loja']} — Gerente: {row['Gerente']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Realizado", format_brl(row["Real_Fat"]), f"Meta: {format_brl(row['Meta_Fat'])}")
    c2.metric("Projeção de Fechamento", format_brl(row["Proj_Fat"]))
    c3.metric("Atingimento Atual", f"{(row['Real_Fat'] / row['Meta_Fat']) * 100:.1f}%")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    col_a.metric("Venda de TV", f"{row['Real_TV']} un.", f"Meta: {row['Meta_TV']} un.")
    col_b.metric("Venda de Vírtua", f"{row['Real_Virtua']} un.", f"Meta: {row['Meta_Virtua']} un.")

    # Cruzar equipe da unidade selecionada a partir da planilha do Google Sheets
    if not df_sheet.empty and col_loja:
        st.markdown("---")
        st.subheader(f"👥 Equipe de Vendas — {row['Loja']}")
        # Normaliza o nome da loja para casar (ex: '10_ESTEIO' com '10_ESTEIO (IRIC)')
        store_key = row["Loja"].replace("_", " ").split()[0]
        team_df = df_sheet[df_sheet[col_loja].astype(str).str.upper().str.contains(row["Loja"].split("_")[1], na=False)].copy()
        if not team_df.empty:
            cols_hide = ["_fat_num", "_itens_num", "_ativ_num"]
            disp_cols = [c for c in team_df.columns if c not in cols_hide]
            team_view = team_df[disp_cols].copy()
            if col_fat and col_fat in team_view.columns:
                team_view[col_fat] = team_df["_fat_num"].apply(format_brl)
            st.dataframe(team_view, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum vendedor encontrado para {row['Loja']} na planilha conectada.")

st.markdown("---")
st.caption("🚀 Painel Gerencial MR10 — Dicere Telecom | Sincronizado em tempo real com Google Sheets.")
