import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

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

# --- NUEVA función: obtener nombres y códigos de todas las regiones ---
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

# Obtener mapeo región_nombre -> región_codigo
mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codigo_region = mapeo_regiones[nombre_region]

# Cargar archivo correspondiente
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codigo_region}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# Asegurar formato decimal correcto
df["YEAR_2018"] = df["YEAR_2018"].astype(str).str.replace(",", ".").astype(float)
df["YEAR_2022"] = df["YEAR_2022"].astype(str).str.replace(",", ".").astype(float)

# Pivotear para tener Hombre/Mujer en columnas
df_pivot = df.pivot_table(
    index=["Cod_Comuna", "Nombre_comuna"],
    columns="Sexo",
    values=["YEAR_2018", "YEAR_2022"]
).reset_index()

# Aplanar columnas
df_pivot.columns = ['Cod_Comuna', 'Nombre_comuna', 'YEAR_2018_Hombre', 'YEAR_2018_Mujer', 'YEAR_2022_Hombre', 'YEAR_2022_Mujer']

# Calcular brechas
df_pivot["Brecha_2018"] = df_pivot["YEAR_2018_Hombre"] - df_pivot["YEAR_2018_Mujer"]
df_pivot["Brecha_2022"] = df_pivot["YEAR_2022_Hombre"] - df_pivot["YEAR_2022_Mujer"]

# Mostrar tabla
st.subheader(f"{indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_pivot[["Cod_Comuna", "Nombre_comuna", "Brecha_2018", "Brecha_2022"]], use_container_width=True)

# Gráfico
st.subheader("Comparación de brechas por comuna")

df_plot = df_pivot.sort_values(by="Brecha_2022", ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
ax.hlines(y=df_plot["Nombre_comuna"], xmin=df_plot["Brecha_2018"], xmax=df_plot["Brecha_2022"], color='gray', alpha=0.5)
ax.scatter(df_plot["Brecha_2018"], df_plot["Nombre_comuna"], color='skyblue', label='2018', s=100)
ax.scatter(df_plot["Brecha_2022"], df_plot["Nombre_comuna"], color='red', label='2022', s=100)

ax.set_xlabel("Brecha (Hombres - Mujeres)")
ax.set_ylabel("Comuna")
ax.set_title(f"{indicador} - {nombre_region}")
ax.legend()

st.pyplot(fig) 