import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Diccionario de indicadores
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
    },
    "Dependencia": {
        "carpeta": "Datos/DEPENDENCIA",
        "prefijo": "Dependencia_Region_"
    }
}

# Renombrar columnas para mejor presentación
nombres_columnas = {
    "Nombre_Region": "Región",
    "Nombre_Provincia": "Provincia",
    "Nombre_comuna": "Comuna",
    "Sexo": "Sexo",
    "YEAR_2018": "Año 2018",
    "YEAR_2019": "Año 2019",
    "YEAR_2020": "Año 2020",
    "YEAR_2021": "Año 2021",
    "YEAR_2022": "Año 2022",
    "YEAR_2023": "Año 2023",
}

# Función: obtener mapeo {nombre región: código región}
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

# Sidebar
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
info = indicadores[indicador]

# Obtener nombres de regiones
mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codigo_region = mapeo_regiones[nombre_region]

# Leer archivo correspondiente
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codigo_region}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# Renombrar columnas si existen en el DataFrame
df.rename(columns=nombres_columnas, inplace=True)

# Mostrar tabla original
columnas_mostrar = list(nombres_columnas.values())
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes]
st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado, use_container_width=True)

# ============= GRÁFICOS ESPECIALES PARA DEPENDENCIA =============
if indicador == "Dependencia":
    # Limpiar nombres de columnas de años
    columnas_anos = [col for col in df_filtrado.columns if col.startswith("Año ")]
    df_dep = df_filtrado.copy()

    # Selección de año para gráfico de columnas
    anio_seleccionado = st.sidebar.selectbox("Selecciona el año para el gráfico de columnas", columnas_anos)

    st.subheader(f"Gráfico de Columnas - {anio_seleccionado}")
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    df_dep_sorted = df_dep.sort_values(anio_seleccionado, ascending=False)
    ax_bar.bar(df_dep_sorted["Comuna"], df_dep_sorted[anio_seleccionado], color="#4a90e2")
    ax_bar.set_xlabel("Comuna")
    ax_bar.set_ylabel("Valor")
    ax_bar.set_title(f"Dependencia por Comuna - {anio_seleccionado}")
    ax_bar.tick_params(axis="x", rotation=90)
    st.pyplot(fig_bar)

    # Gráfico de líneas con toda la serie
    st.subheader("Evolución de Dependencia por Comuna (Serie Completa)")
    fig_line, ax_line = plt.subplots(figsize=(12, 6))
    for _, row in df_dep.iterrows():
        ax_line.plot(columnas_anos, row[columnas_anos], marker='o', label=row["Comuna"])
    ax_line.set_xlabel("Año")
    ax_line.set_ylabel("Valor")
    ax_line.set_title("Evolución de la Dependencia por Comuna")
    ax_line.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
    ax_line.grid(True)
    st.pyplot(fig_line)

# ============= RESTO DE INDICADORES (BRECHAS) =============
elif all(col in df.columns for col in ["Sexo", "Año 2018", "Año 2022"]):

    df['Sexo'] = df['Sexo'].astype(str).str.strip().str.capitalize()
    df = df[df['Sexo'].isin(['Hombre', 'Mujer'])].copy()

    for col in [c for c in df.columns if c.startswith("Año ")]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df_pivot = df.pivot_table(
        index=["Región", "Provincia", "Comuna"],
        columns="Sexo",
        values=[c for c in df.columns if c.startswith("Año ")],
        aggfunc="sum",
        fill_value=0
    )

    df_pivot.columns = [f"{sexo}_{año.split(' ')[1]}" for año, sexo in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    st.subheader("Tabla pivot con valores por sexo y año")
    st.dataframe(df_pivot, use_container_width=True)

    # (Aquí van los gráficos de brechas como en tu código original)
