import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Cargar y fusionar hojas ---
@st.cache_data
def cargar_datos(path):
    hoja1 = pd.read_excel(path, sheet_name='Region_13_1')
    hoja2 = pd.read_excel(path, sheet_name='Region_13_2')
    df = pd.concat([hoja1, hoja2], ignore_index=True)
    return df

# Ruta al archivo Excel
archivo = 'data/Region_13.xlsx'  # Ajusta la ruta si está en otro lugar

df = cargar_datos(archivo)

# --- Título y filtros ---
st.title("Indicadores comunales por provincia - Región Metropolitana")

# Ordenar provincias alfabéticamente
provincias = sorted(df["Nombre_Provincia"].dropna().unique())
provincia_seleccionada = st.selectbox("Selecciona una provincia", provincias)

# Filtrar por provincia
df_filtrado = df[df["Nombre_Provincia"] == provincia_seleccionada]

# Ordenar comunas por porcentaje para claridad
df_ordenado = df_filtrado.sort_values("YEAR_2022", ascending=False)

# --- Gráfico 1: Porcentaje 2022 ---
st.subheader("Porcentaje de personas en 2022")

fig1, ax1 = plt.subplots()
ax1.barh(df_ordenado["Nombre_comuna"], df_ordenado["YEAR_2022"], color="#1f77b4")
ax1.set_xlabel("Porcentaje")
ax1.invert_yaxis()
st.pyplot(fig1)

# --- Gráfico 2: Variación porcentual ---
st.subheader("Variación porcentual respecto al año anterior")

df_var = df_filtrado.sort_values("Var_Porc", ascending=False)

fig2, ax2 = plt.subplots()
ax2.barh(df_var["Nombre_comuna"], df_var["Var_Porc"], color="#ff7f0e")
ax2.set_xlabel("Variación porcentual (%)")
ax2.invert_yaxis()
st.pyplot(fig2)