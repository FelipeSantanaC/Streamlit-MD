import pandas as pd
import streamlit as st

conn = st.experimental_connection('mysql', type='sql')

avaliacoes = conn.query('SELECT * from dimavaliacoes;', ttl=600)
usuarios = conn.query('SELECT * from dimusuario;', ttl=600)
datas = conn.query('SELECT * from dimdatas;', ttl=600)
locais = conn.query('SELECT * from dimlocais;', ttl=600)
fatos = conn.query('SELECT * from fatonota;', ttl=600)

df_avaliacoes = pd.DataFrame(avaliacoes).drop(['version','date_to','date_from'], axis=1)
df_usuarios = pd.DataFrame(usuarios).drop(['version','date_to','date_from'],axis=1)
df_datas = pd.DataFrame(datas).drop(['version','date_to','date_from'],axis=1)
df_locais = pd.DataFrame(locais).drop(['version','date_to','date_from'],axis=1)
df_fatos = pd.DataFrame(fatos)

df_fatos = pd.merge(df_avaliacoes,df_fatos, left_on='keyAvaliacao', right_on='key_avaliacao')
df_fatos = pd.merge(df_usuarios,df_fatos, left_on='keyUsuario', right_on='key_usuario')
df_fatos = pd.merge(df_datas, df_fatos, left_on='keyData', right_on='key_data')
df_fatos = pd.merge(df_locais,df_fatos, left_on='keyLocal', right_on='key_local',how='left').dropna()
df_fatos.rename(columns={'Q1':"Segurança", 'Q2':"Infraestrutura", 'Q3':"Limpeza", 'Q4':"Funcionarios", 'Q5':"Localizacao", 'Q6':"Recursos",'Q7':"Atendimento", 'Q8':"Serviços", 'Q9':"Interatividade", 'Q10':"Precos"}, inplace=True)

st.dataframe(data=df_fatos.head(1000))

st.text('Filtre por tipo de local')
# List of options
options = df_fatos['tipo'].unique()

# Divide the options into three columns
col1, col2, col3 = st.columns(3)

# Iterate through the options and create checkboxes in each column
selected_options = []
for idx, option in enumerate(options):
    if idx % 3 == 0:
        selected_options.append(col1.checkbox(option))
    elif idx % 3 == 1:
        selected_options.append(col2.checkbox(option))
    else:
        selected_options.append(col3.checkbox(option))

# Display selected options
st.write("Selected options:", [option for option, selected in zip(options, selected_options) if selected])

st.text('Filtre por Unidade Federativa')
# List of options
options = df_fatos['estado'].unique()

# Divide the options into three columns
col1, col2, col3 = st.columns(3)

# Iterate through the options and create checkboxes in each column
selected_options = []
for idx, option in enumerate(options):
    if idx % 3 == 0:
        selected_options.append(col1.checkbox(option))
    elif idx % 3 == 1:
        selected_options.append(col2.checkbox(option))
    else:
        selected_options.append(col3.checkbox(option))

# Display selected options
st.write("Selected options:", [option for option, selected in zip(options, selected_options) if selected])


st.text('Filtre por tipo de usuário')
# List of options
options = list(df_fatos['tipoUsuario'].unique())
# Iterate through the options and create checkboxes in each column
selected_options = []
for option in options:
    selected = st.checkbox(option)
    if selected:
        selected_options.append(option)

# Display selected options
st.write("Selected options:", selected_options)

st.text('Filtre por ano')
# Set the year range
min_year = 1970
max_year = 2031

# Create a slider to select a year
values = st.slider(
    'Select a range of values',
    1970, 2031, (2000, 2010))
# Display the selected year
st.write("Selected Year:", values)