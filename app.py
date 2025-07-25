import streamlit as st
import pandas as pd
import os

# Título de la app
st.title("Dashboard de Indicadores Regionales")

# Ruta base donde están tus archivos Excel
ruta_base = "F:/Users/sfarias/Documents/Curso Python/.vscode/Reportes_Comunales/Salidas/Excel"

# Obtener la lista de archivos de Excel
archivos = sorted([f for f in os.listdir(ruta_base) if f.endswith(".xlsx") and "Region" in f])

# Crear un diccionario para mapear número de región a nombre de región
mapa_regiones = {}
for archivo in archivos:
    ruta_archivo = os.path.join(ruta_base, archivo)
    df_temp = pd.read_excel(ruta_archivo)
    if 'Nombre_Region' in df_temp.columns:
        nombre_region = df_temp['Nombre_Region'].iloc[0]
        numero_region = int(archivo.split("_")[3].split(".")[0])
        mapa_regiones[nombre_region] = numero_region

# Mostrar en el selectbox los nombres de las regiones
region_nombre_seleccionada = st.selectbox("Selecciona la región", list(mapa_regiones.keys()))

# Obtener el número de región correspondiente al nombre seleccionado
region_numero = mapa_regiones[region_nombre_seleccionada]

# Construir el nombre del archivo a cargar
archivo_region = f"Brechas_Ingresos_Region_{region_numero}_transpuesto.xlsx"
ruta_archivo = os.path.join(ruta_base, archivo_region)

# Cargar el archivo Excel
df = pd.read_excel(ruta_archivo)

# Asegurar que los nombres de columna estén como se espera
if "Sexo" in df.columns:
    # Pivotear los datos
    pivot = df.pivot(index="Nombre_comuna", columns="Sexo", values="YEAR_2022")

    # Calcular la brecha
    if "Hombre" in pivot.columns and "Mujer" in pivot.columns:
        pivot["Brecha_2022"] = pivot["Hombre"] - pivot["Mujer"]

        # Mostrar resultados
        st.subheader(f"Brecha de ingresos por comuna - {region_nombre_seleccionada}")
        st.dataframe(pivot.style.format("{:.0f}"))
    else:
        st.error("Las columnas 'Hombre' y 'Mujer' no se encuentran en el archivo.")
else:
    st.error("La columna 'Sexo' no se encuentra en el archivo.")
