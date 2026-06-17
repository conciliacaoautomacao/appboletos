import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="Fila de Processamento",
    page_icon="📋",
    layout="wide"
    
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📋 Fila de Processamento")

res = (
    supabase
    .table("robo_boletos")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)

df = pd.DataFrame(res.data)

if df.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

df["status_robo"] = df["status_robo"].fillna("PENDENTE")
df["status_boleto_portal"] = df["status_boleto_portal"].fillna("")
df["mensagem_retorno"] = df["mensagem_retorno"].fillna("")

def status_amigavel(row):
    status = row["status_robo"]

    if status == "PENDENTE":
        return "🟡 Pendente"

    if status == "PROCESSANDO":
        return "🔵 Processando"

    if status == "SUCESSO":
        return "🟢 Sucesso"

    if status == "ERRO":
        return "🔴 Erro"

    if status == "NAO_PROCESSADO":
        portal = row["status_boleto_portal"] or "status não identificado"
        return f"⚪ Não Processado - boleto já {portal}"

    return status

df["status_exibicao"] = df.apply(status_amigavel, axis=1)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Pendentes", len(df[df["status_robo"] == "PENDENTE"]))
col2.metric("Processando", len(df[df["status_robo"] == "PROCESSANDO"]))
col3.metric("Sucesso", len(df[df["status_robo"] == "SUCESSO"]))
col4.metric("Erro", len(df[df["status_robo"] == "ERRO"]))
col5.metric("Não Processado", len(df[df["status_robo"] == "NAO_PROCESSADO"]))

st.markdown("---")

status_opcao = st.selectbox(
    "Filtrar por status",
    [
        "Todos",
        "PENDENTE",
        "PROCESSANDO",
        "SUCESSO",
        "ERRO",
        "NAO_PROCESSADO"
    ]
)

df_filtrado = df.copy()

if status_opcao != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["status_robo"] == status_opcao
    ]

df_filtrado["valor_pago"] = df_filtrado["valor_pago"].apply(
    lambda x: f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if pd.notna(x) else ""
)

df_filtrado["data_do_pagamento"] = pd.to_datetime(
    df_filtrado["data_do_pagamento"],
    errors="coerce"
).dt.strftime("%d/%m/%Y")

df_filtrado["processed_at"] = pd.to_datetime(
    df_filtrado["processed_at"],
    errors="coerce"
).dt.strftime("%d/%m/%Y %H:%M")

colunas = [
    "nosso_numero",
    "cpf",
    "contrato",
    "valor_pago",
    "data_do_pagamento",
    "status_exibicao",
    "mensagem_retorno",
    "etapa",
    "tentativas",
    "processed_at"
]

df_view = df_filtrado[colunas].rename(columns={
    "nosso_numero": "Nosso Número",
    "cpf": "CPF",
    "contrato": "Contrato",
    "valor_pago": "Valor Pago",
    "data_do_pagamento": "Data Pagamento",
    "status_exibicao": "Status",
    "mensagem_retorno": "Retorno",
    "etapa": "Etapa",
    "tentativas": "Tentativas",
    "processed_at": "Processado em"
})

st.dataframe(
    df_view,
    use_container_width=True,
    hide_index=True
)
