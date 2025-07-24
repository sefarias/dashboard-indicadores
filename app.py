import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Diccionario para mapear la selección del usuario a carpetas y archivos
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

# Selección del indicador
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))

# Selección de región
region = st.sidebar.selectbox("Selecciona la región", list(range(1, 17)))

# Construir ruta del archivo Excel según indicador y región
info = indicadores[indicador]
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{region}.xlsx")

# Cargar datos
df = pd.read_excel(archivo)

# Pivot para YEAR_2018 y YEAR_2022, con columnas Hombre y Mujer por comuna
pivot_2018 = df.pivot_table(index='Nombre_comuna', columns='Sexo', values='YEAR_2018').reset_index()
pivot_2022 = df.pivot_table(index='Nombre_comuna', columns='Sexo', values='YEAR_2022').reset_index()

# Combinar ambos pivotes en un solo DataFrame
df_pivot = pivot_2018.merge(pivot_2022, on='Nombre_comuna', suffixes=('_2018', '_2022'))

# Calcular brechas (Hombre - Mujer)
df_pivot['Brecha_2018'] = df_pivot['Hombre_2018'] - df_pivot['Mujer_2018']
df_pivot['Brecha_2022'] = df_pivot['Hombre_2022'] - df_pivot['Mujer_2022']

# Ordenar para visualización descendente por Brecha_2022
df_pivot = df_pivot.sort_values(by='Brecha_2022', ascending=False)

# Mostrar tabla con brechas
st.subheader(f"{indicador} - Región {region}")
st.dataframe(df_pivot[['Nombre_comuna', 'Brecha_2018', 'Brecha_2022']], use_container_width=True)

# Gráfico lollipop comparativo
st.subheader("Comparación de brechas por comuna")

fig, ax = plt.subplots(figsize=(12, 6))
ax.hlines(y=df_pivot['Nombre_comuna'], xmin=df_pivot['Brecha_2018'], xmax=df_pivot['Brecha_2022'], color='gray', alpha=0.5)
ax.scatter(df_pivot['Brecha_2018'], df_pivot['Nombre_comuna'], color='skyblue', label='2018', s=100)
ax.scatter(df_pivot['Brecha_2022'], df_pivot['Nombre_comuna'], color='red', label='2022', s=100)

ax.set_xlabel("Brecha (Hombre - Mujer)")
ax.set_ylabel("Comuna")
ax.legend()
ax.set_title(f"{indicador} - Región {region}")

st.pyplot(fig)
