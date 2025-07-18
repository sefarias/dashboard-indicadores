import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta absoluta al archivo Excel (ajusta si cambia)
archivo = "F:/Users/sfarias/Documents/Curso Python/.vscode/dashboard-indicadores/Datos/Dependencia_Region_13.xlsx"

# Mostrar rutas para depurar
st.write("Directorio actual:", os.getcwd())
st.write("Archivo que intenta cargar:", archivo)

@st.cache_data
def cargar_datos(path):
    hoja1 = pd.read_excel(path, sheet_name='Region_13_1')
    hoja2 = pd.read_excel(path, sheet_name='Region_13_2')
    df = pd.concat([hoja1, hoja2], ignore_index=True)
    return df

try:
    df = cargar_datos(archivo)

    st.title("Dashboard por Provincia - Región Metropolitana")

    # Eliminar filas que no son comunas
    df = df[~df["Nombre_comuna"].str.startswith("Provincia de")]
    df = df[df["Nombre_comuna"] != "Region Metropolitana"]
    df = df[df["Nombre_comuna"] != "Nacional"]

    # Selección de provincia
    provincias = sorted(df["Nombre_Provincia"].dropna().unique())
    provincia_seleccionada = st.selectbox("Selecciona una provincia", provincias)

    # Filtrar comunas por provincia
    df_filtrado = df[df["Nombre_Provincia"] == provincia_seleccionada]

    # Mostrar tabla con comunas filtradas
    st.subheader(f"Comunas en {provincia_seleccionada}")
    st.dataframe(df_filtrado[["Nombre_comuna", "YEAR_2022", "Var_Porc"]])

    # Gráfico de porcentaje YEAR_2022
    st.subheader("Porcentaje YEAR_2022 por comuna")
    fig1, ax1 = plt.subplots()
    df_filtrado_sorted = df_filtrado.sort_values("YEAR_2022", ascending=False)
    ax1.barh(df_filtrado_sorted["Nombre_comuna"], df_filtrado_sorted["YEAR_2022"], color="#1f77b4")
    ax1.invert_yaxis()
    ax1.set_xlabel("Porcentaje YEAR_2022")
    ax1.set_ylabel("Comuna")
    st.pyplot(fig1)

    # Gráfico de variación porcentual Var_Porc
    st.subheader("Variación porcentual Var_Porc por comuna")
    fig2, ax2 = plt.subplots()
    df_filtrado_sorted_var = df_filtrado.sort_values("Var_Porc", ascending=False)
    ax2.barh(df_filtrado_sorted_var["Nombre_comuna"], df_filtrado_sorted_var["Var_Porc"], color="#ff7f0e")
    ax2.invert_yaxis()
    ax2.set_xlabel("Variación porcentual Var_Porc")
    ax2.set_ylabel("Comuna")
    st.pyplot(fig2)

except FileNotFoundError:
    st.error(f"No se encontró el archivo: {archivo}")
except Exception as e:
    st.error(f"Error al cargar o procesar los datos: {e}")
