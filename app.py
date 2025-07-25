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

# Filtrar columnas específicas
columnas_mostrar = ["Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2022"]
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes]

# Mostrar tabla original
st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado, use_container_width=True)

# Crear segunda tabla: pivotear por sexo y crear columnas Hombre_2018, Mujer_2018, Hombre_2022, Mujer_2022
if all(col in df.columns for col in ["Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2022"]):
    # Limpiar y normalizar columna Sexo
    df['Sexo'] = df['Sexo'].astype(str).str.strip().str.capitalize()

    # Filtrar sólo sexos esperados
    df = df[df['Sexo'].isin(['Hombre', 'Mujer'])]

    # Pivot con agregación sumando valores
    df_pivot = df.pivot_table(
        index=["Nombre_comuna"],
        columns="Sexo",
        values=["YEAR_2018", "YEAR_2022"],
        aggfunc='sum',
        fill_value=0
    )

    # Renombrar columnas
    new_columns = {}
    for col in df_pivot.columns:
        año = col[0].split('_')[1]  # '2018' o '2022'
        sexo = col[1]  # Ya capitalizado
        new_col_name = f"{sexo}_{año}"
        new_columns[col] = new_col_name

    df_pivot.rename(columns=new_columns, inplace=True)
    df_pivot = df_pivot.reset_index()

    columnas_orden = ["Nombre_comuna", "Hombre_2018", "Mujer_2018", "Hombre_2022", "Mujer_2022"]
    columnas_orden_final = [c for c in columnas_orden if c in df_pivot.columns]

    st.subheader("Tabla Pivot: Valores por Sexo y Año")
    st.dataframe(df_pivot[columnas_orden_final], use_container_width=True)
else:
    st.warning("No se pueden pivotear los datos: faltan columnas necesarias ('Nombre_comuna', 'Sexo', 'YEAR_2018', 'YEAR_2022').")
