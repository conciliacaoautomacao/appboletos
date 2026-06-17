# Criar pasta:
# mkdir C:\conciliacaoautomacao
# cd C:\conciliacaoautomacao

# Clonar Git:
# git clone https://github.com/conciliacaoautomacao/appboletos.git appboletos_git
# cd appboletos_git

# Instalar dependências:
# pip install -r requirements.txt
# pip install python-dotenv playwright supabase openpyxl
# playwright install

# Criar .env na pasta:
# C:\conciliacaoautomacao\appboletos_git
# Com os dados:
# SUPABASE_URL=SUA_URL_SUPABASE
# SUPABASE_KEY=SUA_CHAVE_SUPABASE

# PORTAL_EMAIL=email.da.pessoa@gooroocredito.com.br
# PORTAL_SENHA=senha_da_pessoa

# Criar executável.bat:
# @echo off
# cd /d C:\conciliacaoautomacao\appboletos_git
# streamlit run app.py
# pause
