import streamlit as st
from indicadores import brechas_ingresos, dependencia  # Importar todos los dashboards existentes

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")
opcion = st.sidebar.radio(
    "Selecciona un indicador:",
    ["Brechas de Ingresos", "Dependencia"]  # Aquí puedes agregar más nombres en el futuro
)

# --- Lógica para mostrar dashboards ---
if opcion == "Brechas de Ingresos":
    brechas_ingresos.mostrar_dashboard()
elif opcion == "Dependencia":
    dependencia.mostrar_dashboard()
