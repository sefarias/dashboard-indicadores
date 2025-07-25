import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Diccionario para mapear indicadores a carpetas y prefijos
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

# Sidebar de selección
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
region = st.sidebar.selectbox("Selecciona la región", list(range(1, 17)))

info = indicadores[indicador]
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{region}.xlsx")

try:
    # Cargar datos con coma decimal
    df = pd.read_excel(archivo, decimal=',')

    # Validar columnas esperadas
    columnas_esperadas = {'Cod_Comuna', 'Nombre_comuna', 'Sexo', 'YEAR_2018', 'YEAR_2022'}
    if not columnas_esperadas.issubset(df.columns):
        st.error("⚠️ El archivo no tiene las columnas esperadas.")
        st.stop()

    # Pivot para calcular brechas Hombre - Mujer por comuna
    pivot = df.pivot_table(index=['Cod_Comuna', 'Nombre_comuna'], 
                           columns='Sexo', 
                           values=['YEAR_2018', 'YEAR_2022'])

    # Aplanar columnas
    pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
    pivot = pivot.reset_index()

    # Verifica si existen ambas columnas Hombre y Mujer
    for col in ['YEAR_2018_Hombre', 'YEAR_2018_Mujer', 'YEAR_2022_Hombre', 'YEAR_2022_Mujer']:
        if col not in pivot.columns:
            st.error(f"⚠️ Falta la columna: {col} en el archivo de la Región {region}")
            st.stop()

    # Calcular brechas
    pivot['Brecha_2018'] = pivot['YEAR_2018_Hombre'] - pivot['YEAR_2018_Mujer']
    pivot['Brecha_2022'] = pivot['YEAR_2022_Hombre'] - pivot['YEAR_2022_Mujer']

    # Mostrar tabla
    st.subheader(f"{indicador} - Región {region}")
    st.dataframe(pivot[['Nombre_comuna', 'Brecha_2018', 'Brecha_2022']], use_container_width=True)

    # Gráfico comparativo
    st.subheader("Comparación de brechas por comuna")
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_data = pivot.sort_values('Brecha_2022', ascending=False)

    ax.hlines(y=plot_data['Nombre_comuna'], xmin=plot_data['Brecha_2018'], xmax=plot_data['Brecha_2022'], color='gray', alpha=0.5)
    ax.scatter(plot_data['Brecha_2018'], plot_data['Nombre_comuna'], color='skyblue', label='2018', s=100)
    ax.scatter(plot_data['Brecha_2022'], plot_data['Nombre_comuna'], color='red', label='2022', s=100)

    ax.set_xlabel("Brecha (Hombres - Mujeres)")
    ax.set_ylabel("Comuna")
    ax.legend()
    ax.set_title(f"{indicador} - Región {region}")
    st.pyplot(fig)

except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo: {archivo}")
except Exception as e:
    st.error(f"⚠️ Error inesperado: {e}")
