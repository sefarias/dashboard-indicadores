import streamlit as st
from indicadores import dependencia, brechas_ingresos

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")
opcion = st.sidebar.selectbox(
    "Selecciona el indicador a visualizar:",
    ["Dependencia", "Brechas de Ingresos"]
)

if opcion == "Dependencia":
    dependencia.mostrar_dashboard()

elif opcion == "Brechas de Ingresos":
    brechas_ingresos.mostrar_dashboard()
