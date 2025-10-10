# app.py

import streamlit as st
from indicadores import brechas_ingresos, dependencia

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")
opcion = st.sidebar.radio(
    "Selecciona un indicador:",
    ["Brechas de Ingresos", "Dependencia"]
)

DASHBOARDS = {
    "Brechas de Ingresos": brechas_ingresos,
    "Dependencia": dependencia
}

DASHBOARDS[opcion].mostrar_dashboard()
