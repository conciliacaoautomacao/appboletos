import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📊 Dashboard do Robô")

res = (
    supabase
    .table("robo_boletos")
    .select("*")
    .execute()
)

df = pd.DataFrame(res.data)

if df.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

df["status_robo"] = df["status_robo"].fillna("PENDENTE")

total = len(df)
pendentes = len(df[df["status_robo"] == "PENDENTE"])
processando = len(df[df["status_robo"] == "PROCESSANDO"])
sucesso = len(df[df["status_robo"] == "SUCESSO"])
erro = len(df[df["status_robo"] == "ERRO"])
nao_processado = len(df[df["status_robo"] == "NAO_PROCESSADO"])

df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce").fillna(0)

valor_total = df["valor_pago"].sum()
valor_sucesso = df[df["status_robo"] == "SUCESSO"]["valor_pago"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total de Boletos", total)
col2.metric("Pendentes", pendentes)
col3.metric("Sucesso", sucesso)

col4, col5, col6 = st.columns(3)

col4.metric("Erro", erro)
col5.metric("Não Processado", nao_processado)
col6.metric(
    "Valor com Sucesso",
    f"R$ {valor_sucesso:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.markdown("---")

st.subheader("Resumo por Status")

resumo = (
    df.groupby("status_robo")
    .agg(
        quantidade=("nosso_numero", "count"),
        valor_total=("valor_pago", "sum")
    )
    .reset_index()
)

resumo["valor_total"] = resumo["valor_total"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.dataframe(
    resumo.rename(columns={
        "status_robo": "Status",
        "quantidade": "Quantidade",
        "valor_total": "Valor Total"
    }),
    use_container_width=True,
    hide_index=True
)
