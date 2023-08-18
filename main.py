import pandas as pd
import streamlit as st

conn = st.experimental_connection('mysql', type='sql')


df = conn.query('SELECT * from dimavaliacoes;', ttl=600)


for row in df.itertuples():
    st.write(f"{row.id} has a :{row.tag}:")