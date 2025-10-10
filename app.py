import streamlit as st
from indicadores import brechas_ingresos

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores Regionales")

st.sidebar.title("📊 Panel de Indicadores")
opcion = st.sidebar.radio("Selecciona un indicador:", ["Brechas de Ingresos", "Dependencia"])

if opcion == "Brechas de Ingresos":
    brechas_ingresos.mostrar_dashboard()
elif opcion == "Dependencia":
    st.info("Módulo de dependencia en desarrollo.")
