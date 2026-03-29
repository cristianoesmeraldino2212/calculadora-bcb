import streamlit as st
import pandas as pd
import os

# --- NOVA FUNÇÃO DE CARREGAMENTO ---
@st.cache_data
def carregar_dados():
    # Descobre o caminho real da pasta onde o script app.py está salvo
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(diretorio_atual, "dados_tbca.parquet")
    
    # Verifica se o arquivo realmente existe antes de tentar ler
    if not os.path.exists(caminho_completo):
        st.error(f"❌ Arquivo não encontrado no caminho: {caminho_completo}")
        # Lista os arquivos da pasta para te ajudar a depurar
        st.write("Arquivos na pasta atual:", os.listdir(diretorio_atual))
        return pd.DataFrame() # Retorna um DataFrame vazio para não travar tudo
    
    return pd.read_parquet(caminho_completo)

df = carregar_dados()

# Verificação de segurança
if df.empty:
    st.stop() # Para a execução se o arquivo não foi lido
