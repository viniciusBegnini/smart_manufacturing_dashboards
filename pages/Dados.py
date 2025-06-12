import streamlit as st
import pandas as pd


@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# -----------
#   Dados
# -----------
dados = pd.read_csv('maquinas_limpo.csv')



# -----------
#   Dashboard
# -----------
st.title('Dados')


with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), default=list(dados.columns))

dados_filtrados = dados[colunas]

st.dataframe(dados_filtrados)
st.markdown( f':gray[{dados_filtrados.shape[0]} linhas x {dados_filtrados.shape[1]} colunas]' )


st.download_button(
    label='Download CSV',
    data=converte_csv(dados),
    file_name='dados.csv',
    mime='text/csv',
    icon=':material/download:'
)