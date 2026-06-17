import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
from io import BytesIO

st.set_page_config(
    page_title="Relatórios",
    page_icon="📑",
    layout="wide"
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📑 Relatórios")

res = (
    supabase
    .table("robo_boletos")
    .select("*")
    .order("processed_at", desc=True)
    .execute()
)

df = pd.DataFrame(res.data)

if df.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce").fillna(0)
df["data_do_pagamento"] = pd.to_datetime(df["data_do_pagamento"], errors="coerce")
df["processed_at"] = pd.to_datetime(df["processed_at"], errors="coerce")

st.markdown("### Filtros")

col1, col2, col3 = st.columns(3)

with col1:
    status_robo = st.selectbox(
        "Status Robô",
        ["Todos"] + sorted(df["status_robo"].dropna().unique().tolist())
    )

with col2:
    status_portal = st.selectbox(
        "Status Portal",
        ["Todos"] + sorted(df["status_boleto_portal"].dropna().unique().tolist())
    )

with col3:
    data_ref = st.date_input(
        "Data do pagamento",
        value=None,
        format="DD/MM/YYYY"
    )

df_filtrado = df.copy()

if status_robo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_robo"] == status_robo]

if status_portal != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_boleto_portal"] == status_portal]

if data_ref:
    df_filtrado = df_filtrado[
        df_filtrado["data_do_pagamento"].dt.date == data_ref
    ]

st.markdown("---")

col1, col2, col3 = st.columns(3)

col1.metric("Quantidade", len(df_filtrado))
col2.metric(
    "Valor Total",
    f"R$ {df_filtrado['valor_pago'].sum():,.2f}"
    .replace(",", "X")
    .replace(".", ",")
    .replace("X", ".")
)
col3.metric(
    "Sucessos",
    len(df_filtrado[df_filtrado["status_robo"] == "SUCESSO"])
)

df_view = df_filtrado.copy()

df_view["valor_pago"] = df_view["valor_pago"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

df_view["data_do_pagamento"] = df_view["data_do_pagamento"].dt.strftime("%d/%m/%Y")
df_view["processed_at"] = df_view["processed_at"].dt.strftime("%d/%m/%Y %H:%M")

colunas = [
    "nosso_numero",
    "cpf",
    "contrato",
    "valor_pago",
    "data_do_pagamento",
    "status_robo",
    "status_boleto_portal",
    "mensagem_retorno",
    "etapa",
    "tentativas",
    "processed_at"
]

df_view = df_view[colunas].rename(columns={
    "nosso_numero": "Nosso Número",
    "cpf": "CPF",
    "contrato": "Contrato",
    "valor_pago": "Valor Pago",
    "data_do_pagamento": "Data Pagamento",
    "status_robo": "Status Robô",
    "status_boleto_portal": "Status Portal",
    "mensagem_retorno": "Mensagem Retorno",
    "etapa": "Etapa",
    "tentativas": "Tentativas",
    "processed_at": "Processado em"
})

st.dataframe(
    df_view,
    use_container_width=True,
    hide_index=True
)

def gerar_excel(df_export):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Relatorio")

    return output.getvalue()

excel = gerar_excel(df_view)

st.download_button(
    label="📥 Baixar relatório Excel",
    data=excel,
    file_name="relatorio_robo_boletos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
