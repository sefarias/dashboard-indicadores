import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Mapeo de indicadores a carpetas y prefijos
indicadores = {
    "Brechas de Ingresos": ("BRECHAS_ING", "Brechas_Ingresos_Region_"),
    "Brechas de Matrícula": ("BRECHAS_MAT", "Brechas_Matricula_Region_"),
    "Brechas de Ocupación": ("BRECHAS_OCU", "Brechas_Ocupacion_Region_")
}

# Sidebar para seleccionar el indicador y región
st.sidebar.title("Dashboard de Indicadores de Brechas")
indicador_seleccionado = st.sidebar.selectbox("Selecciona un indicador", list(indicadores.keys()))
region_seleccionada = st.sidebar.selectbox("Selecciona una región", list(range(1, 17)))

# Ruta al archivo Excel correspondiente
carpeta, prefijo = indicadores[indicador_seleccionado]
archivo = f"Datos/{carpeta}/{prefijo}{region_seleccionada}.xlsx"

# Verificar si el archivo existe
if not os.path.exists(archivo):
    st.error(f"No se encontró el archivo: {archivo}")
else:
    # Leer datos
    df = pd.read_excel(archivo)
    
    # Filtrar solo Total o ambos sexos (si quieres filtrar por Sexo también puedes agregar selectbox)
    df_filtrado = df[df["Sexo"] == "Total"]

    st.title(indicador_seleccionado)
    st.subheader(f"Región {region_seleccionada} - Porcentaje YEAR_2022 por comuna")

    # Ordenar por valor 2022
    df_filtrado_sorted = df_filtrado.sort_values("YEAR_2022", ascending=False)

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(
        df_filtrado_sorted["Nombre_comuna"],
        df_filtrado_sorted["YEAR_2022"],
        color="#1f77b4",
        height=0.5
    )
    ax.invert_yaxis()
    ax.set_xlabel("Porcentaje YEAR_2022", fontsize=12)
    ax.set_ylabel("Comuna", fontsize=12)

    # Ajustar fuente de los ejes
    ax.tick_params(axis='both', labelsize=10)

    st.pyplot(fig)
