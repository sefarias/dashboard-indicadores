import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Indicadores", layout="wide")
st.title("📊 Dashboard de Indicadores")

# Cargar archivo Excel
archivo = st.file_uploader("📂 Cargar archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    st.subheader("Vista previa de los datos:")
    st.dataframe(df)

    columnas = df.columns.tolist()
    if len(columnas) >= 2:
        col_x = st.selectbox("📌 Eje X", columnas)
        col_y = st.selectbox("📈 Eje Y", columnas, index=1)

        fig = px.bar(df, x=col_x, y=col_y, title=f"{col_y} por {col_x}")
        st.plotly_chart(fig, use_container_width=True)
