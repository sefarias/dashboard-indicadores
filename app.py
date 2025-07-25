import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
archivo = 'data.xlsx'  # Reemplaza con la ruta correcta si es necesario
df = pd.read_excel(archivo, sheet_name='Cruce_5')

# Eliminar filas con valores nulos en las columnas clave
df = df.dropna(subset=['region_casen', 'porcentaje', 'Nombre_Region'])

# Obtener lista única de regiones con nombre y número
regiones = df[['region_casen', 'Nombre_Region']].drop_duplicates().sort_values('region_casen')
region_dict = dict(zip(regiones['Nombre_Region'], regiones['region_casen']))

# Sidebar para seleccionar la región
region_nombre = st.sidebar.selectbox('Selecciona la región', list(region_dict.keys()))
region_codigo = region_dict[region_nombre]

# Filtrar por la región seleccionada
df_region = df[df['region_casen'] == region_codigo]

# Crear el gráfico de barras
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(df_region['variable'], df_region['porcentaje'], color='#1f77b4')
ax.set_title(f'Distribución porcentual por variable - {region_nombre}', fontsize=14)
ax.set_ylabel('Porcentaje')
ax.set_xlabel('Variable')
ax.tick_params(axis='x', rotation=45)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

# Mostrar los datos de la región seleccionada
st.dataframe(df_region)
