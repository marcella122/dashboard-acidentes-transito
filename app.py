
import pandas as pd
import streamlit as st
import plotly.express as px



# Configuração da página
st.set_page_config(
    page_title="Dashboard de Acidentes de Trânsito",
    page_icon="🚦",
    layout="wide"
)

# Carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "si-bol-2021.csv",
        encoding="latin1",
        sep=";"
    )

    # Corrigir espaços nos nomes das colunas
    df.columns = df.columns.str.strip()

    return df

try:
    df = carregar_dados()

except Exception as erro:
    st.error("Não foi possível carregar o arquivo CSV.")
    st.write("Confira se si-bol-2021.csv está na mesma pasta que app.py.")
    st.code(str(erro))
    st.stop()

print(df.head().to_string())

# Título
st.title("🚦 Dashboard de Acidentes de Trânsito")
st.write(
    "Análise dos registros de acidentes de trânsito."
)
st.caption(
    "Por: Brunna Amparo Alves, Marcella Moura de Lima, "
    "Maria Fernanda Quintana e Gustavo Nigro Novi Rebelo"
)

# Conferir colunas necessárias
colunas_necessarias = [
    "DESC_REGIONAL",
    "DESC_TIPO_ACIDENTE",
    "INDICADOR_FATALIDADE"
]

faltando = [
    coluna for coluna in colunas_necessarias
    if coluna not in df.columns
]

if faltando:
    st.error("Não encontrei algumas colunas esperadas no arquivo.")
    st.write("Colunas encontradas:", df.columns.tolist())
    st.stop()

# Filtros na lateral
st.sidebar.header("Filtros")

regionais = sorted(
    df["DESC_REGIONAL"].dropna().astype(str).unique().tolist()
)

tipos = sorted(
    df["DESC_TIPO_ACIDENTE"].dropna().astype(str).unique().tolist()
)

regionais_escolhidas = st.sidebar.multiselect(
    "Escolha as regionais",
    options=regionais,
    default=regionais
)

tipos_escolhidos = st.sidebar.multiselect(
    "Escolha os tipos de acidente",
    options=tipos,
    default=tipos
)

# Aplicar os filtros
dados = df[
    df["DESC_REGIONAL"].astype(str).isin(regionais_escolhidas)
    & df["DESC_TIPO_ACIDENTE"].astype(str).isin(tipos_escolhidos)
].copy()

# Indicadores
st.subheader("📊 Visão geral")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total de registros",
    f"{len(dados):,}".replace(",", ".")
)

col2.metric(
    "Regionais",
    dados["DESC_REGIONAL"].nunique()
)

fatalidade = (
    dados["INDICADOR_FATALIDADE"]
    .astype(str)
    .str.strip()
    .str.upper()
    .isin(["SIM", "S", "1", "TRUE", "FATAL", "SIM - FATAL"])
    .sum()
)

col3.metric(
    "Registros marcados como fatais",
    int(fatalidade)
)

st.divider()

# Gráfico 1: acidentes por tipo
st.subheader("🚗 Acidentes por tipo")

contagem_tipos = (
    dados["DESC_TIPO_ACIDENTE"]
    .value_counts()
    .rename_axis("Tipo de acidente")
    .reset_index(name="Quantidade")
)

if not contagem_tipos.empty:
    fig_tipos = px.bar(
        contagem_tipos,
        x="Tipo de acidente",
        y="Quantidade",
        text="Quantidade",
        title="Quantidade de registros por tipo de acidente"
    )

    fig_tipos.update_layout(
        xaxis_title="Tipo de acidente",
        yaxis_title="Quantidade",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_tipos,
        use_container_width=True
    )
else:
    st.warning("Não há dados para os filtros selecionados.")

st.divider()

# Gráfico 2: acidentes por regional
st.subheader("📍 Acidentes por regional")

contagem_regionais = (
    dados["DESC_REGIONAL"]
    .value_counts()
    .rename_axis("Regional")
    .reset_index(name="Quantidade")
)

if not contagem_regionais.empty:
    fig_regionais = px.bar(
        contagem_regionais,
        x="Regional",
        y="Quantidade",
        text="Quantidade",
        title="Quantidade de registros por regional"
    )

    fig_regionais.update_layout(
        xaxis_title="Regional",
        yaxis_title="Quantidade",
        xaxis_tickangle=-45,
        template="plotly_white"
    )

    st.plotly_chart(
        fig_regionais,
        use_container_width=True
    )
else:
    st.warning("Não há dados por regional para exibir.")

st.divider()

# Gráfico 3: condições do tempo
st.subheader("🌦️ Acidentes por condição do tempo")

if "DESC_TEMPO" in dados.columns:
    contagem_tempo = (
        dados["DESC_TEMPO"]
        .value_counts()
        .rename_axis("Condição do tempo")
        .reset_index(name="Quantidade")
    )

    fig_tempo = px.pie(
        contagem_tempo,
        names="Condição do tempo",
        values="Quantidade",
        title="Distribuição dos registros por condição do tempo"
    )

    st.plotly_chart(
        fig_tempo,
        use_container_width=True
    )

st.divider()

# Tabela dos registros
st.subheader("📋 Dados dos acidentes")
st.write("Use a tabela para consultar os registros filtrados.")

st.dataframe(
    dados,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Os gráficos representam os registros presentes no arquivo "
    "e não necessariamente todos os acidentes ocorridos."
)
