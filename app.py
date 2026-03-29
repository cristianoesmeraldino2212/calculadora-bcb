import streamlit as st
import requests
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Adriano Lopes - Financeiro", page_icon="📈")

st.title("🏦 Calculadora de Correção Monetária")
st.subheader("Dados Oficiais do Banco Central (SGS)")

# Formulário de entrada
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor Original (R$)", value=19500.0, step=100.0)
    with col2:
        indice = st.selectbox("Escolha o Índice", ["IPCA (Inflação)", "SELIC", "CDI", "IGP-M"])

    data_inicio = st.date_input("Data Inicial da Correção")

# Mapeamento de códigos do BCB
codigos = {"IPCA (Inflação)": 433, "SELIC": 11, "CDI": 12, "IGP-M": 189}

if st.button("CALCULAR CORREÇÃO AGORA"):
    try:
        # Busca na API do Banco Central
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigos[indice]}/dados?formato=json"
        res = requests.get(url).json()
        df = pd.DataFrame(res)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        
        # Filtro de data
        data_ini_dt = pd.to_datetime(data_inicio)
        df_filtrado = df[df['data'] >= data_ini_dt]
        
        # Cálculo do fator acumulado
        fator = 1.0
        for v in df_filtrado['valor']:
            fator *= (1 + (float(v) / 100))
        
        valor_final = valor * fator
        
        # Exibição de Resultados
        st.divider()
        st.success(f"### Valor Corrigido: R$ {valor_final:,.2f}")
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("Variação do Índice", f"{round((fator-1)*100, 2)}%")
        col_res2.metric("Ganho Nominal", f"R$ {(valor_final - valor):,.2f}")
        
        # Gráfico de evolução do índice
        st.write("#### Evolução Mensal do Índice (%)")
        st.line_chart(df_filtrado.set_index('data')['valor'].astype(float))
        
    except Exception as e:
        st.error("Erro ao conectar ao Banco Central. Tente novamente.")

st.caption("App desenvolvido para cálculos de NTN e Debêntures - Adriano Lopes")