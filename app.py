import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi

st.set_page_config(layout="wide")

# --- Diccionario de indicadores ---
indicadores = {
    "Brechas de Ingresos": {
        "carpeta": "Datos/BRECHAS_ING",
        "prefijo": "Brechas_Ingresos_Region_"
    },
    "Brechas de Matrícula": {
        "carpeta": "Datos/BRECHAS_MAT",
        "prefijo": "Brechas_Matricula_Region_"
    },
    "Brechas de Ocupación": {
        "carpeta": "Datos/BRECHAS_OCU",
        "prefijo": "Brechas_Ocupacion_Region_"
    }
}

# --- Función para obtener códigos de región ---
def obtener_mapeo_regiones(info):
    carpeta = info["carpeta"]
    regiones_list = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xlsx"):
            path = os.path.join(carpeta, archivo)
            try:
                df_temp = pd.read_excel(path)
                if "Codigo_Region" in df_temp.columns and "Nombre_Region" in df_temp.columns:
                    regiones_list.append(df_temp[["Codigo_Region", "Nombre_Region"]])
            except Exception as e:
                st.warning(f"Error leyendo {archivo}: {e}")

    if regiones_list:
        regiones_concat = pd.concat(regiones_list).drop_duplicates()
        return dict(zip(regiones_concat["Nombre_Region"], regiones_concat["Codigo_Region"]))
    return {}

# --- Sidebar de selección ---
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
info = indicadores[indicador]

mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codigo_region = mapeo_regiones[nombre_region]

# --- Leer datos ---
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codigo_region}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# --- Tabla original ---
columnas_mostrar = ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", 
                    "YEAR_2018", "YEAR_2019", "YEAR_2020", "YEAR_2021", "YEAR_2022"]
df_filtrado = df[[col for col in columnas_mostrar if col in df.columns]]
st.subheader(f"Datos originales - {indicador} - {nombre_region}")
st.dataframe(df_filtrado, use_container_width=True)

# --- Pivotear datos por sexo ---
if all(col in df.columns for col in ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2022"]):
    df['Sexo'] = df['Sexo'].astype(str).str.strip().str.capitalize()
    df = df[df['Sexo'].isin(['Hombre', 'Mujer'])].copy()

    for col in [c for c in df.columns if c.startswith("YEAR_")]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df_pivot = df.pivot_table(
        index=["Nombre_Region", "Nombre_Provincia", "Nombre_comuna"],
        columns="Sexo",
        values=[c for c in df.columns if c.startswith("YEAR_")],
        aggfunc="sum",
        fill_value=0
    )

    df_pivot.columns = [f"{sexo}_{año.split('_')[1]}" for año, sexo in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    st.subheader("Tabla pivote con valores por sexo y año")
    st.dataframe(df_pivot, use_container_width=True)

    # --- Gráficos comparativos ---
    columnas_necesarias = ["Mujer_2018", "Mujer_2022", "Hombre_2018", "Hombre_2022"]
    if all(col in df_pivot.columns for col in columnas_necesarias):
        comuna_seleccionada = st.selectbox("Selecciona una comuna para comparar:", 
                                           df_pivot["Nombre_comuna"].unique())
        df_chart = df_pivot[df_pivot["Nombre_comuna"] == comuna_seleccionada]

        mujer_vals = df_chart[["Mujer_2018", "Mujer_2022"]].values[0]
        hombre_vals = df_chart[["Hombre_2018", "Hombre_2022"]].values[0]
        x_labels = ["2018", "2022"]

        # --- Gráfico de barras ---
        fig1, ax1 = plt.subplots()
        ax1.bar(x_labels, mujer_vals, label="Mujer", color=["#ff69b4", "#c71585"])
        ax1.bar(x_labels, -hombre_vals, label="Hombre", color=["#87ceeb", "#4682b4"])
        ax1.axhline(0, color='black')
        ax1.set_title("Gráfico de Barras: Brechas 2018 vs 2022")
        ax1.legend()
        st.pyplot(fig1)

        # --- Gráfico de líneas ---
        fig2, ax2 = plt.subplots()
        ax2.plot(x_labels, mujer_vals, marker="o", label="Mujer", color="#c71585")
        ax2.plot(x_labels, hombre_vals, marker="o", label="Hombre", color="#4682b4")
        ax2.set_title("Gráfico de Líneas: Evolución por sexo")
        ax2.legend()
        st.pyplot(fig2)

        # --- Áreas apiladas ---
        fig3, ax3 = plt.subplots()
        ax3.stackplot(x_labels, mujer_vals, hombre_vals, labels=["Mujer", "Hombre"], colors=["#ff69b4", "#87ceeb"])
        ax3.set_title("Gráfico de Áreas Apiladas")
        ax3.legend(loc='upper left')
        st.pyplot(fig3)

        # --- Radar ---
        categories = ['2018', '2022']
        values_mujer = list(mujer_vals) + [mujer_vals[0]]
        values_hombre = list(hombre_vals) + [hombre_vals[0]]
        angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
        angles += angles[:1]

        fig4, ax4 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax4.plot(angles, values_mujer, color="#c71585", linewidth=2, label='Mujer')
        ax4.fill(angles, values_mujer, color="#c71585", alpha=0.25)
        ax4.plot(angles, values_hombre, color="#4682b4", linewidth=2, label='Hombre')
        ax4.fill(angles, values_hombre, color="#4682b4", alpha=0.25)
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories)
        ax4.set_title("Radar: Comparación 2018-2022")
        ax4.legend(loc='upper right')
        st.pyplot(fig4)

        # --- Dispersión tipo lollipop ---
        fig5, ax5 = plt.subplots(figsize=(8, 5))
        ax5.plot([2018, 2022], mujer_vals, color='#c71585', marker='o', linewidth=2, label='Mujer')
        ax5.plot([2018, 2022], hombre_vals, color='#4682b4', marker='o', linewidth=2, label='Hombre')
        ax5.axhline(y=np.mean([*mujer_vals, *hombre_vals]), color='gray', linestyle='--', linewidth=1, label='Promedio')
        ax5.set_xticks([2018, 2022])
        ax5.set_title("Dispersión Lollipop: 2018 vs 2022")
        ax5.legend()
        ax5.grid(True, axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig5)

        # --- Dot Plot agrupado horizontal ---
        fig6, ax6 = plt.subplots(figsize=(8, 5))
        y_pos = range(2)
        ax6.plot([mujer_vals[0], mujer_vals[1]], y_pos, marker='o', linestyle='-', color='#c71585', label='Mujer')
        ax6.plot([hombre_vals[0], hombre_vals[1]], y_pos, marker='o', linestyle='-', color='#4682b4', label='Hombre')
        ax6.axvline(x=0, color='gray', linestyle='--', linewidth=0.7)
        ax6.set_yticks(y_pos)
        ax6.set_yticklabels(["2018", "2022"])
        ax6.set_xlabel("Valor")
        ax6.set_title("Dot Plot: Comparación 2018-2022 por Sexo")
        ax6.legend()
        st.pyplot(fig6)
    else:
        st.warning("Faltan columnas clave para generar los gráficos.")
else:
    st.warning("No se puede crear la tabla pivote por falta de columnas necesarias.")
