import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import datetime

# Ruta absoluta al archivo Excel
archivo = "Datos/Dependencia_Region_13.xlsx"

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
    st.title("Dashboard por Provincia - Región Metropolitana")

    # Botón para recargar los datos desde el Excel
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
        st.success("Datos recargados correctamente.")

    # Cargar datos (con caché)
    df = cargar_datos(archivo)

    # Mostrar fecha y hora de carga
    st.caption(f"📅 Última carga: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

    height_val =0.30
    fuente = fm.FontProperties(family='Arial', size=14)  # Cambia Arial y tamaño

    st.subheader("Porcentaje YEAR_2022 por comuna")
    fig1, ax1 = plt.subplots(figsize=(10, 6))  # Ajusta tamaño aquí
    df_filtrado_sorted = df_filtrado.sort_values("YEAR_2022", ascending=False)
    ax1.barh(df_filtrado_sorted["Nombre_comuna"], df_filtrado_sorted["YEAR_2022"], color="#1f77b4", height=height_val)
    ax1.invert_yaxis()
    ax1.set_xlabel("Porcentaje YEAR_2022")
    ax1.set_ylabel("Comuna")


    # Cambiar tamaño de etiquetas eje Y
    ax1.tick_params(axis='y', labelsize=14)  # Cambia 14 por el tamaño deseado

    # Alternativa para cambiar fuente y tamaño (más control):
    etiquetas = ax1.get_yticklabels()
    for etiqueta in etiquetas:
        etiqueta.set_fontsize(14)
        etiqueta.set_fontfamily('Arial')  # Cambia según la fuente que quieras

    st.pyplot(fig1)

    # Gráfico de variación porcentual Var_Porc
    st.subheader("Variación porcentual Var_Porc por comuna")
    fig2, ax2 = plt.subplots(figsize=(10, 6))  # Ajusta tamaño aquí
    df_filtrado_sorted_var = df_filtrado.sort_values("Var_Porc", ascending=False)
    ax2.barh(df_filtrado_sorted_var["Nombre_comuna"], df_filtrado_sorted_var["Var_Porc"], color="#ff7f0e", height=height_val)
    ax2.invert_yaxis()
    ax2.set_xlabel("Variación porcentual Var_Porc")
    ax2.set_ylabel("Comuna")

    # Cambiar tamaño de etiquetas eje Y
    ax2.tick_params(axis='y', labelsize=14)  # Cambia 14 por el tamaño deseado

    # Alternativa para cambiar fuente y tamaño (más control):
    etiquetas = ax2.get_yticklabels()
    for etiqueta in etiquetas:
        etiqueta.set_fontsize(14)
        etiqueta.set_fontfamily('Arial')  # Cambia según la fuente que quieras

    st.pyplot(fig2)

except FileNotFoundError:
    st.error(f"No se encontró el archivo: {archivo}")
except Exception as e:
    st.error(f"Error al cargar o procesar los datos: {e}")
