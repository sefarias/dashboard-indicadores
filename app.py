import pandas as pd
import streamlit as st
import os

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
    }
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

# Mostrar tabla original
columnas_mostrar = ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2019", "YEAR_2020", "YEAR_2021", "YEAR_2022"]
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes]
st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado, use_container_width=True)

# Segunda tabla con pivot por sexo
if all(col in df.columns for col in ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2022"]):
    
    # Limpieza de columna Sexo
    df['Sexo'] = df['Sexo'].astype(str).str.strip().str.capitalize()
    df = df[df['Sexo'].isin(['Hombre', 'Mujer'])].copy()

    # Asegurar columnas numéricas
    for col in [c for c in df.columns if c.startswith("YEAR_")]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Hacer pivot para pasar Sexo a columnas
    df_pivot = df.pivot_table(
        index=["Nombre_Region", "Nombre_Provincia", "Nombre_comuna"],
        columns="Sexo",
        values=[c for c in df.columns if c.startswith("YEAR_")],
        aggfunc="sum",
        fill_value=0
    )

    # Renombrar columnas a formato Hombre_2018, Mujer_2018, etc.
    df_pivot.columns = [f"{sexo}_{año.split('_')[1]}" for año, sexo in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    st.subheader("Tabla pivot con valores por sexo y año")
    st.dataframe(df_pivot, use_container_width=True)
else:
    st.warning("Faltan columnas necesarias para hacer el pivot.")
