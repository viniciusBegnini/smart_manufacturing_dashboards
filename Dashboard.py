import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---- Page Configs
st.set_page_config(layout= "wide")

# -------------------
#        Dados
# -------------------
dados = pd.read_csv('maquinas_limpo.csv')
dados['datetime'] = pd.to_datetime(dados['timestamp'])

# -------------------
#       Sidebar
# -------------------

st.sidebar.title('Filtros')

## Período
with st.sidebar.expander("Período"):
    date_min = dados['datetime'].min().to_pydatetime()
    date_max = dados['datetime'].max().to_pydatetime()
    todos_periodos = st.checkbox("Todo o período", value=True)

    if todos_periodos:
        f_datas = (date_min, date_max)
    else:
        f_datas = st.slider("Selecione o intervalo de datas", date_min, date_max, (date_min, date_max))

## Máquinas
with st.sidebar.expander("Máquinas"):
    all_machines = st.checkbox("Todas as máquinas", value=True)
    machines = dados['machine'].unique()
    selec_machines = machines if all_machines else st.multiselect("Selecione as máquinas", machines, default=machines)

## Status
with st.sidebar.expander("Status das máquinas"):
    all_status = st.checkbox("Todos os status", value=True)
    status = dados['machine_status'].unique()
    selec_status = status if all_status else st.multiselect("Selecione os status", status, default=status)

## Tipos de falha
with st.sidebar.expander("Tipos de Falha"):
    all_failures = st.checkbox("Todas as falhas", value=True)
    failures = dados['failure_type'].unique()
    selec_failures = failures if all_failures else st.multiselect("Selecione os tipos de falha", failures, default=failures)


query = '''
@f_datas[0] <= datetime <= @f_datas[1] and \
machine in @selec_machines and \
machine_status in @selec_status and \
failure_type in @selec_failures
'''
dados = dados.query(query)

# -------------------
#       Tabelas
# -------------------

anomalias = dados[dados['anomaly_flag'] == "Yes"]['machine'].value_counts().nlargest(10).reset_index()
anomalias.columns = ['machine', 'anomalias']

dados['falha_manutencao'] = ((dados['machine_status'] == 'Failure') | (dados['maintenance_required'] == 'Yes')).astype(int)
relacao = pd.crosstab(dados['anomaly_flag'], dados['falha_manutencao'], normalize='index') * 100
relacao = relacao.reset_index().melt(id_vars='anomaly_flag', var_name='Tipo', value_name='Percentual')

# -------------------
#       Gráficos
# -------------------

## Machine Status
fig_status_temporal = px.histogram (dados,
                                    x="datetime", 
                                    color="machine_status", 
                                    nbins=50, 
                                    title="Eventos ao longo do tempo")
fig_status_temporal.update_layout(yaxis_title='Quantidade eventos registrados', xaxis_title='Data')

fig_status_quantidade = px.pie (dados, 
                                names="machine_status", 
                                title="Status das máquinas")

## Temperatura
fig_temperatura = px.box(dados, 
                         x="machine", 
                         y="temperature", 
                         color="machine", 
                         title="Temperatura por máquina")
fig_temperatura.update_layout(yaxis_title='Temperatura', xaxis_title='Maquina')

## Vibração
fig_vibracao = px.box(dados, 
                         x="machine", 
                         y="vibration", 
                         color="machine", 
                         title="Vibração por máquina")
fig_vibracao.update_layout(yaxis_title='Vibração', xaxis_title='Maquina')

## Pressão
fig_pressao = px.box(dados, 
                     x="machine", 
                     y="pressure", 
                     color="machine", 
                     title="Pressão por máquina")
fig_pressao.update_layout(yaxis_title='Pressão', xaxis_title='Maquina')

## Consumo de energia
fig_energy_consumption = px.box(dados, 
                                x="machine", 
                                y="energy_consumption", 
                                color="machine", 
                                title="Consumo de energia por máquina")
fig_energy_consumption.update_layout(yaxis_title='Consumo de energia', xaxis_title='Maquina')

## Umidade
fig_umidade = px.box(dados, 
                    x="machine", 
                    y="humidity", 
                    color="machine", 
                    title="Umidade por máquina")
fig_umidade.update_layout(yaxis_title='Umidade', xaxis_title='Maquina')

## Falhas e anomalias
fig_tipos_falhas = px.histogram(dados, 
                                x="failure_type", 
                                color="failure_type", 
                                title="Tipos de falhas")
fig_tipos_falhas.update_layout(yaxis_title='Quantidade', xaxis_title='Tipos de falhas')

fig_temperatura_vibracao = px.scatter(dados, 
                                      x="temperature", 
                                      y="vibration", 
                                      color="machine_status", 
                                      title="Temperatura vs Vibração")
fig_temperatura_vibracao.update_layout(yaxis_title='', xaxis_title='')

fig_anomalias = px.pie(dados[dados['anomaly_flag'] == "Yes"], 
                       names="machine", 
                       title="Distribuição de Anomalias por Máquina")

fig_anomalias_top10 = px.bar(anomalias, 
                             x='anomalias', 
                             y='machine', 
                             orientation='h', 
                             title='Top 10 Máquinas com mais anomalias detectadas')
fig_anomalias_top10.update_layout(yaxis_title="Máquina", xaxis_title="Quantidade de Anomalias", yaxis=dict(categoryorder='total ascending'))

fig_vib_anomalia = px.box(dados, x='anomaly_flag', y='vibration',
                           color='anomaly_flag',
                           title='Vibração x Anomalia',
                           labels={'anomaly_flag': 'Anomalia', 'vibration': 'Vibração'},
                           category_orders={'anomaly_flag': [0, 1]})

fig_temp_anomalia = px.box(dados, x='anomaly_flag', y='temperature',
                            color='anomaly_flag',
                            title='Temperatura x Anomalia',
                            labels={'anomaly_flag': 'Anomalia', 'temperature': 'Temperatura (°C)'},
                            category_orders={'anomaly_flag': [0, 1]})

fig_relacao = px.bar(relacao,
                     x='anomaly_flag',
                     y='Percentual',
                     color='Tipo',
                     title='Ocorrência de Falha ou Manutenção em Registros com/sem Anomalias',
                     labels={'anomaly_flag': 'Anomalia', 'Percentual': 'Percentual (%)'},
                     text_auto='.2f')

# -------------------
#      Dashboard
# -------------------
st.title("Dados coletados de sensores em máquinas (smart manufacturing)")

tab_home, tab_sensores, tab_risco = st.tabs(['Home', 'Sensores', 'Risco e Falhas'])

with tab_home:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Registros", len(dados))

    with col2:
        st.metric("Máquinas Monitoradas", dados['machine'].nunique())

    with col3:
        st.metric("Falhas Registradas", (dados['failure_type'] != 'Normal').sum())

    st.plotly_chart(fig_status_quantidade)
    st.plotly_chart(fig_status_temporal)

with tab_sensores:
    col1, col2 = st.columns(2)
    with col1:
        valor_max = dados['temperature'].max()
        maquina_max = dados[dados['temperature'] == valor_max]['machine'].iloc[0]
        st.metric(f'A Máquina que registrou a temperatura maxíma foi {maquina_max} ', f'{valor_max:.2f} °C.')
    with col2:
        valor_min = dados['temperature'].min()
        maquina_min = dados[dados['temperature'] == valor_min]['machine'].iloc[0]
        st.metric(f'A Máquina que registrou a temperatura mínima foi {maquina_min} ', f'{valor_min:.2f} °C.')
    st.plotly_chart(fig_temperatura)

    col1, col2 = st.columns(2)
    with col1:
        valor_max = dados['vibration'].max()
        maquina_max = dados[dados['vibration'] == valor_max]['machine'].iloc[0]
        st.metric(f"A máquina com maior vibração registrada foi {maquina_max}", f"{valor_max:.2f}")
    with col2:
        valor_min = dados['vibration'].min()
        maquina_min = dados[dados['vibration'] == valor_min]['machine'].iloc[0]
        st.metric(f"A máquina com menor vibração registrada foi {maquina_min}", f"{valor_min:.2f}")
    st.plotly_chart(fig_vibracao)

    col1, col2 = st.columns(2)
    with col1:
        valor_max = dados['pressure'].max()
        maquina_max = dados[dados['pressure'] == valor_max]['machine'].iloc[0]
        st.metric(f"A máquina com maior pressão registrada foi {maquina_max}", f"{valor_max:.2f} Pa")
    with col2:
        valor_min = dados['pressure'].min()
        maquina_min = dados[dados['pressure'] == valor_min]['machine'].iloc[0]
        st.metric(f"A máquina com menor pressão registrada foi {maquina_min}", f"{valor_min:.2f} Pa")
    st.plotly_chart(fig_pressao)
    
    col1, col2 = st.columns(2)
    with col1:
        valor_max = dados['energy_consumption'].max()
        maquina_max = dados[dados['energy_consumption'] == valor_max]['machine'].iloc[0]
        st.metric(f"A máquina com maior consumo de energia foi {maquina_max}", f"{valor_max:.2f} kWh")
    with col2:
        valor_min = dados['energy_consumption'].min()
        maquina_min = dados[dados['energy_consumption'] == valor_min]['machine'].iloc[0]
        st.metric(f"A máquina com menor consumo de energia foi {maquina_min}", f"{valor_min:.2f} kWh")
    st.plotly_chart(fig_energy_consumption)
    
    col1, col2 = st.columns(2)
    with col1:
        valor_max = dados['humidity'].max()
        maquina_max = dados[dados['humidity'] == valor_max]['machine'].iloc[0]
        st.metric(f"A máquina com maior umidade registrada foi {maquina_max}", f"{valor_max:.2f} %")
    with col2:
        valor_min = dados['humidity'].min()
        maquina_min = dados[dados['humidity'] == valor_min]['machine'].iloc[0]
        st.metric(f"A máquina com menor umidade registrada foi {maquina_min}", f"{valor_min:.2f} %")
    st.plotly_chart(fig_umidade)

with tab_risco:

    st.plotly_chart(fig_tipos_falhas)

    st.plotly_chart(fig_temperatura_vibracao)

    st.plotly_chart(fig_anomalias_top10)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_vib_anomalia)
        st.plotly_chart(fig_anomalias)
    with col2:
        st.plotly_chart(fig_temp_anomalia)
        st.plotly_chart(fig_relacao)
    
 