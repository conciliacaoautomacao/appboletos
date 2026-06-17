import streamlit as st

st.set_page_config(
    page_title="Robô Boletos",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebarNav"] ul {
    padding-top: 20px;
}

[data-testid="stSidebarNav"] li {
    margin: 8px 0;
    border-radius: 12px;
}

[data-testid="stSidebarNav"] a {
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 600;
}

[data-testid="stSidebarNav"] a:hover {
    background-color: rgba(255,255,255,0.12);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #2563eb;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Robô de Baixa de Boletos")
st.info("Use o menu lateral para importar bases, acompanhar a fila e visualizar os status.")
