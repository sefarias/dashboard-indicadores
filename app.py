# app.py

import streamlit as st
from indicadores import brechas_ingresos, dependencia, ingresos

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")
opcion = st.sidebar.radio(
    "Selecciona un indicador:",
    ["Brechas de Ingresos", "Dependencia", "Ingresos"]
)

DASHBOARDS = {
    "Brechas de Ingresos": brechas_ingresos,
    "Dependencia": dependencia,
    "Ingresos": ingresos
}

if opcion in DASHBOARDS:
    DASHBOARDS[opcion].mostrar_dashboard()
