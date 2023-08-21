import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go

conn = st.experimental_connection('mysql', type='sql')
#Carregar tabelas
avaliacoes = conn.query('SELECT * from dimavaliacoes;', ttl=600)
usuarios = conn.query('SELECT * from dimusuario;', ttl=600)
datas = conn.query('SELECT * from dimdatas;', ttl=600)
locais = conn.query('SELECT * from dimlocais;', ttl=600)
fatos = conn.query('SELECT * from fatonota;', ttl=600)
#Transformar em dataframes e excluir colunas
df_avaliacoes = pd.DataFrame(avaliacoes).drop(['version','date_to','date_from'], axis=1)
df_usuarios = pd.DataFrame(usuarios).drop(['version','date_to','date_from'],axis=1)
df_datas = pd.DataFrame(datas).drop(['version','date_to','date_from'],axis=1)
df_locais = pd.DataFrame(locais).drop(['version','date_to','date_from'],axis=1)
df_fatos = pd.DataFrame(fatos)
#Merge
df_fatos = pd.merge(df_avaliacoes,df_fatos, left_on='keyAvaliacao', right_on='key_avaliacao')
df_fatos = pd.merge(df_usuarios,df_fatos, left_on='keyUsuario', right_on='key_usuario')
df_fatos = pd.merge(df_datas, df_fatos, left_on='keyData', right_on='key_data')
df_fatos = pd.merge(df_locais,df_fatos, left_on='keyLocal', right_on='key_local',how='left').dropna()
df_fatos.rename(columns={'Q1':"Segurança", 'Q2':"Infraestrutura", 'Q3':"Limpeza", 'Q4':"Funcionarios", 'Q5':"Localizacao", 'Q6':"Recursos",'Q7':"Atendimento", 'Q8':"Serviços", 'Q9':"Interatividade", 'Q10':"Preços"}, inplace=True)
df_fatos['ano_id'] = df_fatos['ano_id'].astype(int)

#Barra lateral
#Tipo de local
st.sidebar.header('Filtre seus resultados')
local_types = df_fatos['tipo'].unique().tolist()
selected_local_types = st.sidebar.multiselect('Filtre por tipo de local', local_types)
#Unidade Federativa
state = df_fatos['estado'].unique().tolist()
selected_states = st.sidebar.multiselect('Filtre por Unidade Federativa', state)
#Tipo de usuário
user_types = df_fatos['tipoUsuario'].unique().tolist()
selected_user_type = st.sidebar.multiselect('Filtre por tipode usuário',user_types)
#Intervalo em anos
selected_years = st.sidebar.multiselect('Selecione o período de interesse',[2008,2009,2010])


#Main
st.header('Grupo 5')
st.subheader('Análises')
#Consulta com filtros
# Apply filters independently
filtered_df = df_fatos.copy()
if selected_local_types:
    filtered_df = filtered_df[filtered_df['tipo'].isin(selected_local_types)]
if selected_states:
    filtered_df = filtered_df[filtered_df['estado'].isin(selected_states)]
if selected_user_type:
    filtered_df = filtered_df[filtered_df['tipoUsuario'].isin(selected_user_type)]
if selected_years:
    filtered_df = filtered_df[filtered_df['ano_id'].isin(selected_years)]

# Display filtered table
st.dataframe(filtered_df)
st.subheader('Pergunta 1')
st.text('Existe uma variação na média das notas e da quantidade de avaliações de acordo com o mês do ano?')
filtered_df['mes_numeronoano'] = filtered_df['mes_numeronoano'].astype(int)
select_fato = filtered_df[['mes_numeronoano','nota','mes_texto']].sort_values('mes_numeronoano')
select_fato = select_fato.groupby('mes_numeronoano').agg({'nota':'mean' ,'mes_numeronoano':'count', 'mes_texto':'first'})

fig = go.Figure(
    data=go.Bar(
        x=select_fato['mes_texto'],
        y=select_fato['mes_numeronoano'],
        name="Total de avaliações",
        marker=dict(color="paleturquoise"),
    )
)
fig.add_trace(
    go.Scatter(
        x=select_fato['mes_texto'],
        y=select_fato['nota'],
        yaxis="y2",
        name="Nota",
        marker=dict(color="crimson"),
    )
)
fig.update_layout(
    legend=dict(orientation="h"),
    yaxis=dict(
        title=dict(text="Total de avaliações por mês"),
        side="left",
        range=[0, select_fato['mes_numeronoano'].max()],
    ),
    yaxis2=dict(
        title=dict(text="Média das notas"),
        side="right",
        range=[0, 5],
        overlaying="y",
        tickmode="sync",
    ),
)
st.plotly_chart(fig)

st.subheader('Pergunta 2')
st.text('Existe uma variação nas notas dadas pelos usuários de cadeiras derodas nas categorias de segurança, preço e atendimento, em função do decorrer do tempo e da condição do dia ser útil?')
nota_categoria = st.radio('Selecione a nota por categoria:', ('Segurança','Preços','Atendimento'))
select_fato2 = filtered_df[['Segurança','Atendimento','Preços','data_id','dia_ehdiautil','DAM']].sort_values('data_id')
select_fato2 = select_fato2[select_fato2['DAM'].str.contains('cadeira')]
select_fato2 = select_fato2.groupby('data_id').agg({'data_id':'first','Segurança':'mean' ,'Atendimento':'mean', 'Preços':'mean', 'dia_ehdiautil':'first'})
select_fato2['dia_ehdiautil'] = select_fato2['dia_ehdiautil'].astype(int)
select_fato2['dia_ehdiautil'].replace(0 , 'Não', inplace=True)
select_fato2['dia_ehdiautil'].replace(1 , 'Sim', inplace=True)
color_map = {
    'Sim': 'blue',   
    'Não': 'yellow'
}
fig = px.line(select_fato2, x="data_id", y=nota_categoria, color='dia_ehdiautil',  
              color_discrete_map=color_map,
            )
fig.update_layout(
    legend_title_text='Dia é útil?',
)
fig.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
)
st.plotly_chart(fig)

st.subheader('Pergunta 3')
st.text('Qual a média de notas das avaliações ao longo do ano para os usuários que usam muleta, protese ou bengala?')
nome_categoria = st.radio('Selecione o tipo de acessório:', ('muleta','protese','bengala'))
filtered_df['mes_numeronoano'] = filtered_df['mes_numeronoano'].astype(int)

select_fato = filtered_df[['mes_numeronoano','nota','mes_texto', 'DAM']].sort_values('mes_numeronoano')
select_fato = select_fato[select_fato['DAM'].str.contains(nome_categoria)]

select_fato = select_fato.groupby('mes_numeronoano').agg({'nota':'mean', 'mes_texto':'first'})


fig = go.Figure(
    data=go.Scatter(
        x=select_fato['mes_texto'],
        y=select_fato['nota'],
        name="Média das Avaliações",
        
        line=dict(color="red"),
    )
)

fig.update_layout(
    yaxis_title="Média das Avaliações") 

st.plotly_chart(fig)


