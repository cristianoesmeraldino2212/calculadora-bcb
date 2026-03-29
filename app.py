import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuração
st.set_page_config(page_title="Cristiano Esmeraldino - Financeiro", page_icon="📈")
st.title("🏦 Calculadora de Correção")
st.subheader("Correção de valor pelo CDI")

# 1. ESCOLHA DO ÍNDICE
indice = st.selectbox("Escolha o Índice", ["CDI", "IPCA", "IGP-M", "SELIC"])

# 2. INTERFACE
with st.container():
    st.write("---")
    if indice == "CDI":
        st.info("Obs.: Para a correção pelo CDI informe períodos a partir de 06/03/1986.")
    
    col_valor, col_perc = st.columns(2)
    with col_valor:
        valor = st.number_input("Valor a ser corrigido*", value=1000.0, step=100.0)
    with col_perc:
        percentual_cdi = st.number_input("% do CDI*", value=100.0) if indice == "CDI" else 100.0

    c_ini, c_fim = st.columns(2)
    if indice in ["IPCA", "IGP-M"]:
        fmt, ex, v_i, v_f = "%m/%Y", "MM/AAAA", "01/2024", "02/2026"
    else:
        fmt, ex, v_i, v_f = "%d/%m/%Y", "DD/MM/AAAA", "01/01/2024", "27/03/2026"

    with c_ini:
        d_ini_txt = st.text_input(f"Data inicial* ({ex})", value=v_i).strip()
    with c_fim:
        d_fim_txt = st.text_input(f"Data final* ({ex})", value=v_f).strip()

cods = {"IPCA": 433, "SELIC": 11, "CDI": 12, "IGP-M": 189}

if st.button("CORRIGIR VALOR"):
    try:
        dt_i = datetime.strptime(d_ini_txt, fmt)
        dt_f = datetime.strptime(d_fim_txt, fmt)
        
        with st.spinner('Conectando ao Banco Central...'):
            cod = cods[indice]
            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod}/dados?formato=json"
            
            # CAMUFLAGEM (Headers): Isso diz ao BCB que somos um navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Fazendo a requisição com a camuflagem
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                st.error(f"Erro {response.status_code}: O Banco Central bloqueou a conexão automatizada. Tente novamente em instantes.")
            else:
                dados_json = response.json()
                df = pd.DataFrame(dados_json)
                df['data'] = pd.to_datetime(df['data'], dayfirst=True)
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                
                mask = (df['data'] >= dt_i) & (df['data'] <= dt_f)
                df_f = df.loc[mask].copy()
                
                if df_f.empty:
                    st.warning("Nenhum dado encontrado para as datas informadas.")
                else:
                    fator = 1.0
                    ajuste = percentual_cdi / 100
                    for v in df_f['valor'].dropna():
                        fator *= (1 + ((v / 100) * ajuste))
                    
                    v_final = valor * fator
                    st.divider()
                    st.subheader(f"Resultado Final: R$ {v_final:,.2f}")
                    st.write(f"Fator de correção acumulado: **{fator:.6f}**")
                    st.metric("Variação Acumulada", f"{((fator-1)*100):.4f}%")
                    
                    with st.expander("Ver memória de cálculo"):
                        st.dataframe(df_f.sort_values(by='data', ascending=False))

    except Exception as e:
        st.error(f"Erro no processamento: {e}")

st.divider()
st.caption("Desenvolvido por Cristiano Esmeraldino - Dados oficiais do Banco Central")
