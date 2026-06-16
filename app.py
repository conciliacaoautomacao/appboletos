import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Robô Boletos", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🤖 Robô de Baixa de Boletos")

arquivo = st.file_uploader(
    "Importe a base Excel ou CSV",
    type=["xlsx", "csv"]
)

def ler_arquivo(arquivo):
    if arquivo.name.endswith(".xlsx"):
        return pd.read_excel(arquivo, dtype=str)
    return pd.read_csv(arquivo, dtype=str, sep=None, engine="python", encoding="utf-8-sig")

if arquivo:
    df = ler_arquivo(arquivo)

    df.columns = (
        df.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
    )

    colunas_obrigatorias = [
        "cpf",
        "contrato",
        "nosso_numero",
        "valor_pago",
        "data_do_pagamento"
    ]

    faltantes = [c for c in colunas_obrigatorias if c not in df.columns]

    if faltantes:
        st.error(f"Colunas faltantes: {faltantes}")
        st.stop()

    st.success(f"Arquivo carregado com {len(df)} linhas.")
    st.dataframe(df, use_container_width=True)

    if st.button("Enviar para fila do robô"):
        registros = []
    
        for _, row in df.iterrows():
            valor_pago = str(row["valor_pago"]).strip()
            valor_pago = valor_pago.replace(".", "").replace(",", ".")
    
            data_pgto = pd.to_datetime(
                row["data_do_pagamento"],
                dayfirst=True,
                errors="coerce"
            )
    
            registros.append({
                "cpf": str(row["cpf"]).strip(),
                "contrato": str(row["contrato"]).strip(),
                "nosso_numero": str(row["nosso_numero"]).strip(),
                "valor_pago": float(valor_pago),
                "data_do_pagamento": data_pgto.strftime("%Y-%m-%d"),
                "status_robo": "PENDENTE",
                "etapa": "IMPORTADO"
            })
    
        st.write("Prévia do que será enviado:")
        st.write(registros[:3])
    
        supabase.table("robo_boletos").insert(registros).execute()
    
        st.success("Base enviada para a fila do robô com sucesso!")
