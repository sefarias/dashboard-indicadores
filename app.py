import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Títulos
st.title("Dashboard de Indicadores de Brechas de Género")
st.markdown("Fuente: Subsecretaría de Evaluación Social")

# Ruta base donde están los archivos (ajusta si cambias de carpeta)
ruta_base = "data"

# Cargar los nombres de regiones desde uno de los archivos
df_nombres = pd.read_excel(os.path.join(ruta_base, "Brechas_Ingresos_Region_1.xlsx"))
nombre_region = df_nombres["Nombre_Region"].iloc[0]

# Crear diccionario para mapear número -> nombre de región
region_map = {}
for i in range(1, 17):
    archivo = f"Brechas_Ingresos_Region_{i}.xlsx"
    df = pd.read_excel(os.path.join(ruta_base, archivo))
    region_map[i] = df["Nombre_Region"].iloc[0]

# Mostrar los nombres en el selectbox, pero trabajar con el número internamente
region_seleccionada = st.selectbox(
    "Selecciona la región:",
    options=list(region_map.keys()),
    format_func=lambda x: region_map[x]
)

# Función para cargar datos de una región
def cargar_datos(tipo, region_num):
    archivo = f"{tipo}_Region_{region_num}.xlsx"
    ruta = os.path.join(ruta_base, archivo)
    return pd.read_excel(ruta)

# Cargar datos según la región seleccionada
df_ingresos = cargar_datos("Brechas_Ingresos", region_seleccionada)
df_matricula = cargar_datos("Brechas_Matricula", region_seleccionada)
df_ocupacion = cargar_datos("Brechas_Ocupacion", region_seleccionada)

# Convertir a porcentajes y redondear
for df in [df_ingresos, df_matricula, df_ocupacion]:
    if "Brecha_2022" in df.columns:
        df["Brecha_2022"] = df["Brecha_2022"] * 100
        df["Brecha_2022"] = df["Brecha_2022"].round(1)

# Crear gráficos
st.subheader("Brecha de Ingresos 2022")
fig1 = px.bar(
    df_ingresos.sort_values("Brecha_2022"),
    x="Brecha_2022",
    y="Nombre_comuna",
    orientation="h",
    labels={"Brecha_2022": "Brecha (%)", "Nombre_comuna": "Comuna"},
    color_discrete_sequence=["#26418f"]
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Brecha de Matrícula Educación Superior 2022")
fig2 = px.bar(
    df_matricula.sort_values("Brecha_2022"),
    x="Brecha_2022",
    y="Nombre_comuna",
    orientation="h",
    labels={"Brecha_2022": "Brecha (%)", "Nombre_comuna": "Comuna"},
    color_discrete_sequence=["#197278"]
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Brecha de Ocupación Laboral 2022")
fig3 = px.bar(
    df_ocupacion.sort_values("Brecha_2022"),
    x="Brecha_2022",
    y="Nombre_comuna",
    orientation="h",
    labels={"Brecha_2022": "Brecha (%)", "Nombre_comuna": "Comuna"},
    color_discrete_sequence=["#f8961e"]
)
st.plotly_chart(fig3, use_container_width=True)
