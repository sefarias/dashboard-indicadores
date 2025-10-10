# app.py
import streamlit as st
from indicadores import brechas_ingresos, dependencia
# Si agregas nuevos indicadores, solo importarlos aquí:
# from indicadores import brechas_matricula, brechas_ocupacion, ...

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")

# --- Diccionario de dashboards ---
DASHBOARDS = {
    "Brechas de Ingresos": brechas_ingresos,
    "Dependencia": dependencia,
    # Aquí agregas nuevos indicadores:
    # "Brechas de Matrícula": brechas_matricula,
    # "Brechas de Ocupación": brechas_ocupacion,
}

# --- Selector de indicador ---
opcion = st.sidebar.radio("Selecciona un indicador:", list(DASHBOARDS.keys()))

# --- Mostrar el dashboard seleccionado ---
DASHBOARDS[opcion].mostrar_dashboard()
