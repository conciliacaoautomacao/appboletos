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

[data-testid="stSidebarNav"] a {
    border-radius: 14px;
    padding: 12px 16px;
    margin: 6px 10px;
    font-weight: 700;
    background-color: rgba(255,255,255,0.04);
}

[data-testid="stSidebarNav"] a:hover {
    background-color: rgba(255,255,255,0.14);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    box-shadow: 0 6px 16px rgba(37,99,235,0.35);
}
</style>
""", unsafe_allow_html=True)

inicio = st.Page(
    "pages/dashboard.py",
    title="🏠 Início",
    icon="🏠"
)

dashboard = st.Page(
    "pages/dashboard.py",
    title="📊 Dashboard",
    icon="📊"
)

upload = st.Page(
    "pages/upload_base.py",
    title="📤 Upload Base",
    icon="📤"
)

fila = st.Page(
    "pages/fila_processamento.py",
    title="📋 Fila de Processamento",
    icon="📋"
)

config = st.Page(
    "pages/4_Config_Campos.py",
    title="⚙️ Configurações",
    icon="⚙️"
)

pg = st.navigation([
    inicio,
    dashboard,
    upload,
    fila,
    config
])

pg.run()
