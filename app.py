import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configuración general
st.set_page_config(layout="wide")
sns.set(style="whitegrid")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.unicode_minus"] = False

# Título de la app
st.title("Gráfico de Dispersión Normalizado por Comuna y Región")

# Cargar datos
uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Validar columnas necesarias
    columnas_necesarias = {'region_casen', 'Nombre_comuna', 'variable', 'valor_normalizado'}
    if not columnas_necesarias.issubset(df.columns):
        st.error(f"El archivo debe contener las siguientes columnas: {columnas_necesarias}")
        st.stop()

    # Normalizar nombres
    df.columns = df.columns.str.strip()

    # Menú para seleccionar región
    regiones_disponibles = df["region_casen"].dropna().unique()
    region_seleccionada = st.selectbox("Selecciona una región:", sorted(regiones_disponibles))

    # Filtrar y pivotear
    df_filtrado = df[df["region_casen"] == region_seleccionada]
    df_pivot = df_filtrado.pivot_table(index=["Nombre_comuna", "region_casen"],
                                       columns="variable",
                                       values="valor_normalizado").reset_index()

    # Eliminar columnas no numéricas
    variables = df_pivot.columns.difference(["Nombre_comuna", "region_casen"])

    # Menú para seleccionar variables a comparar
    variable_x = st.selectbox("Selecciona la variable del eje X:", variables)
    variable_y = st.selectbox("Selecciona la variable del eje Y:", variables, index=1 if len(variables) > 1 else 0)

    # Generar gráfico para cada comuna
    comunas_disponibles = df_pivot["Nombre_comuna"].unique()

    for comuna_seleccionada in comunas_disponibles:
        st.markdown(f"### 📍 Comuna: {comuna_seleccionada}")
        df_chart = df_pivot[df_pivot["Nombre_comuna"] == comuna_seleccionada]

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(df_chart[variable_x], df_chart[variable_y], color='royalblue', s=80, edgecolor='black')

        # Agregar etiquetas
        for i, row in df_chart.iterrows():
            ax.text(row[variable_x] + 0.01, row[variable_y], row["Nombre_comuna"],
                    fontsize=9, color='black')

        # Línea diagonal
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Igualdad (X = Y)')

        # Líneas divisorias
        ax.axhline(0.5, color='gray', linestyle=':', linewidth=1)
        ax.axvline(0.5, color='gray', linestyle=':', linewidth=1)

        # Límites y etiquetas
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel(variable_x, fontsize=11, fontweight='bold')
        ax.set_ylabel(variable_y, fontsize=11, fontweight='bold')
        ax.set_title(f"Dispersión normalizada para {comuna_seleccionada}", fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        st.pyplot(fig)
