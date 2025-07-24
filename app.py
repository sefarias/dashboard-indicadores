import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuración inicial
st.set_page_config(layout="wide")
st.title("Dashboard de Brechas por Comuna")

# Diccionario de indicadores y carpetas
indicadores = {
    "Ingreso": "Datos/BRECHAS_ING",
    "Matrícula": "Datos/BRECHAS_MAT",
    "Ocupación": "Datos/BRECHAS_OCU"
}

# Selección del indicador
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
carpeta = indicadores[indicador]

# Obtener lista de regiones desde los archivos
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith(".xlsx")])
regiones = [f.split("_")[-1].replace(".xlsx", "") for f in archivos]
region_elegida = st.sidebar.selectbox("Selecciona la región", regiones)

# Construir la ruta del archivo correspondiente
archivo_region = [f for f in archivos if f.endswith(f"_{region_elegida}.xlsx")][0]
ruta_archivo = os.path.join(carpeta, archivo_region)

# Leer datos
df = pd.read_excel(ruta_archivo)

# Filtrar y calcular brecha
df_filtrado = df[df["Sexo"].isin(["Hombre", "Mujer"])]
pivot = df_filtrado.pivot(index="Nombre_comuna", columns="Sexo", values="YEAR_2022").reset_index()
pivot["Brecha_2022"] = pivot["Hombre"] - pivot["Mujer"]
pivot = pivot.sort_values("Brecha_2022", ascending=False)

# Mostrar título dinámico
st.subheader(f"Brecha {indicador.lower()} por comuna - Región {region_elegida}")

# Gráfico
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(pivot["Nombre_comuna"], pivot["Brecha_2022"], color="#1f77b4", height=0.5)
ax.invert_yaxis()
ax.set_xlabel("Brecha Hombre - Mujer")
ax.set_ylabel("Comuna")
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Mostrar tabla
st.dataframe(pivot, use_container_width=True)
