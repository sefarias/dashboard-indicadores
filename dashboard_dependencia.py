import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Título
st.title("Dashboard de Indicadores de Dependencia")

# Cargar datos desde el repositorio (sin uploader)
archivo = "Datos/Dependencia_Region_13.xlsx"
df = pd.read_excel(archivo)

# Mostrar datos
st.subheader("Vista previa de los datos")
st.dataframe(df)

# Gráfico de barras
st.subheader("Gráfico de dependencia por categoría")

if 'Categoria' in df.columns and 'Valor' in df.columns:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['Categoria'], df['Valor'], color='skyblue')
    ax.set_xlabel("Categoría")
    ax.set_ylabel("Valor")
    ax.set_title("Dependencia por Categoría")
    st.pyplot(fig)
else:
    st.warning("Las columnas 'Categoria' y 'Valor' no están en el archivo.")
