import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

st.title("📋 Fila de Processamento")

res = (
    supabase
    .table("robo_boletos")
    .select("*")
    .order("id", desc=True)
    .execute()
)

df = pd.DataFrame(res.data)

if df.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Pendentes",
        len(df[df["status_robo"] == "PENDENTE"])
    )

with col2:
    st.metric(
        "Sucesso",
        len(df[df["status_robo"] == "SUCESSO"])
    )

with col3:
    st.metric(
        "Erro",
        len(df[df["status_robo"] == "ERRO"])
    )

with col4:
    st.metric(
        "Total",
        len(df)
    )

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
