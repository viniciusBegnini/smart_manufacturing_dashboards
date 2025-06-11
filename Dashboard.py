import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Page Configs
st.set_page_config(layout= "wide")

# -------------------
#        Dados
# -------------------
dados = pd.read_csv('maquinas_limpo.csv')


# -------------------
#       Tabelas
# -------------------

# -------------------
#       Gráficos
# -------------------

# -------------------
#      Dashboard
# -------------------
st.title("Dados coletados de sensores em máquinas(smart manufacturing)")


st.dataframe(dados)