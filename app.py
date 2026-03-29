import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Cristiano Esmeraldino - Financeiro", page_icon="📈")

st.title("🏦 Calculadora de Correção Monetária")
st.subheader("Dados Oficiais do Banco Central (SGS)")

# Lista de meses e anos para os seletores
meses = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, 
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, 
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}
anos = list(range(1994, datetime.now().year + 1))[::-1] # De 1994 até hoje

# Formulário de entrada
with st.container():
    valor = st.number_input("Valor Original (R$)", value=19500.0, step=100.0)
    indice = st.selectbox("Escolha o Índice", ["IPCA (Inflação)", "SELIC", "CDI", "IGP-M"])
    
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Inicial**")
        mes_ini = st.selectbox("Mês Inicial", list(meses.keys()), key="mes_ini")
        ano_ini = st.selectbox("Ano Inicial", anos, key="ano_ini")
        
    with col2:
        st.write("**Data Final**")
        mes_fim = st.selectbox("Mês Final", list(meses.keys()), key="mes_fim", index=0)
        ano_fim = st.selectbox("Ano Final", anos, key="ano_fim")

# Mapeamento de códigos do BCB
codigos = {"IPCA (Inflação)": 433, "SELIC": 11, "CDI": 12, "IGP-M": 189}

if st.button("CALCULAR CORREÇÃO AGORA"):
    # Converte a seleção para datas reais (primeiro dia do mês)
    dt_inicio = datetime(ano_ini, meses[mes_ini], 1)
    dt_final = datetime(ano_fim, meses[mes_fim], 1)
    
    if dt_inicio > dt_final:
        st.error("A data inicial não pode ser maior que a data final.")
    else:
        try:
            with st.spinner('Consultando Banco Central...'):
                url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigos[indice]}/dados?formato=json"
                res = requests.get(url).json()
                df = pd.DataFrame(res)
                df['data'] = pd.to_datetime(df['data'], dayfirst=True)
                
                # Filtro do intervalo
                df_filtrado = df[(df['data'] >= dt_inicio) & (df['data'] <= dt_final)]
                
                if df_filtrado.empty:
                    st.warning("Ainda não existem dados oficiais para este período.")
                else:
                    fator = 1.0
                    for v in df_filtrado['valor']:
                        fator *= (1 + (float(v) / 100))
                    
                    valor_final = valor * fator
                    
                    st.divider()
                    st.success(f"### Valor Corrigido: R$ {valor_final:,.2f}")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Variação Acumulada", f"{round((fator-1)*100, 2)}%")
                    c2.metric("Ganho Real", f"R$ {(valor_final - valor):,.2f}")
                    
                    st.write("#### Histórico do Período")
                    st.line_chart(df_filtrado.set_index('data')['valor'].astype(float))
            
        except Exception as e:
            st.error("Erro ao conectar ao Banco Central. Tente novamente mais tarde.")

st.divider()
st.caption("App desenvolvido para cálculos de NTN e Debêntures - Cristiano Esmeraldino")
