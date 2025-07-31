import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Diccionario de indicadores
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

# Función: obtener mapeo {nombre región: código región}
def obtener_mapeo_regiones(info):
    carpeta = info["carpeta"]
    regiones_list = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xlsx"):
            path = os.path.join(carpeta, archivo)
            try:
                df_temp = pd.read_excel(path)
                if "Codigo_Region" in df_temp.columns and "Nombre_Region" in df_temp.columns:
                    regiones_list.append(df_temp[["Codigo_Region", "Nombre_Region"]])
            except Exception as e:
                st.warning(f"Error leyendo {archivo}: {e}")

    if regiones_list:
        regiones_concat = pd.concat(regiones_list).drop_duplicates()
        return dict(zip(regiones_concat["Nombre_Region"], regiones_concat["Codigo_Region"]))

    return {}

# Sidebar
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
info = indicadores[indicador]

# Obtener nombres de regiones
mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codigo_region = mapeo_regiones[nombre_region]

# Leer archivo correspondiente
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codigo_region}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# Mostrar tabla original
columnas_mostrar = ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2019", "YEAR_2020", "YEAR_2021", "YEAR_2022"]
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes]
st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado, use_container_width=True)

# Segunda tabla con pivot por sexo
if all(col in df.columns for col in ["Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo", "YEAR_2018", "YEAR_2022"]):

    df['Sexo'] = df['Sexo'].astype(str).str.strip().str.capitalize()
    df = df[df['Sexo'].isin(['Hombre', 'Mujer'])].copy()

    for col in [c for c in df.columns if c.startswith("YEAR_")]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df_pivot = df.pivot_table(
        index=["Nombre_Region", "Nombre_Provincia", "Nombre_comuna"],
        columns="Sexo",
        values=[c for c in df.columns if c.startswith("YEAR_")],
        aggfunc="sum",
        fill_value=0
    )

    df_pivot.columns = [f"{sexo}_{año.split('_')[1]}" for año, sexo in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    st.subheader("Tabla pivot con valores por sexo y año")
    st.dataframe(df_pivot, use_container_width=True)

    # Gráfico: Barras comparativas de brechas
    st.subheader("Gráfico de Brechas por Comuna (2018 vs 2022)")
    if all(col in df_pivot.columns for col in ["Mujer_2018", "Mujer_2022", "Hombre_2018", "Hombre_2022"]):
        df_pivot["Brecha_2018"] = df_pivot["Hombre_2018"] - df_pivot["Mujer_2018"]
        df_pivot["Brecha_2022"] = df_pivot["Hombre_2022"] - df_pivot["Mujer_2022"]

        fig, ax = plt.subplots(figsize=(10, 6))
        ancho = 0.35
        x = range(len(df_pivot))
        ax.bar(x, df_pivot["Brecha_2018"], width=ancho, label='Brecha 2018', color='#a1c9f4')
        ax.bar([i + ancho for i in x], df_pivot["Brecha_2022"], width=ancho, label='Brecha 2022', color='#ffb482')
        ax.set_xticks([i + ancho / 2 for i in x])
        ax.set_xticklabels(df_pivot["Nombre_comuna"], rotation=90)
        ax.set_title("Comparación de Brechas Hombre - Mujer por Comuna")
        ax.legend()
        st.pyplot(fig)

        # Gráfico de dispersión con línea identidad
        st.subheader("Dispersión de Brechas (2018 vs 2022)")
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.scatterplot(data=df_pivot, x="Brecha_2018", y="Brecha_2022", ax=ax2)
        for i in range(df_pivot.shape[0]):
            ax2.text(df_pivot["Brecha_2018"][i] + 0.1, df_pivot["Brecha_2022"][i] + 0.1, df_pivot["Nombre_comuna"][i], fontsize=7)

        max_val = max(df_pivot["Brecha_2018"].max(), df_pivot["Brecha_2022"].max())
        min_val = min(df_pivot["Brecha_2018"].min(), df_pivot["Brecha_2022"].min())
        ax2.plot([min_val, max_val], [min_val, max_val], 'k--', label="Línea identidad")
        ax2.axhline(0, color='gray', linewidth=0.5)
        ax2.axvline(0, color='gray', linewidth=0.5)
        ax2.set_xlabel("Brecha 2018")
        ax2.set_ylabel("Brecha 2022")
        ax2.set_title("Brecha Hombre - Mujer: 2018 vs 2022")
        ax2.legend()
        st.pyplot(fig2)

        # Gráfico de líneas por comuna
        st.subheader("Evolución de Brechas por Comuna (2018 a 2022)")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        for i in range(len(df_pivot)):
            ax3.plot([2018, 2022], [df_pivot["Brecha_2018"][i], df_pivot["Brecha_2022"][i]], marker='o', label=df_pivot["Nombre_comuna"][i])
        ax3.set_xticks([2018, 2022])
        ax3.set_ylabel("Brecha (Hombre - Mujer)")
        ax3.set_title("Evolución de la Brecha por Comuna")
        ax3.grid(True)
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
        st.pyplot(fig3)

        if all(col in df_pivot.columns for col in ["Mujer_2018", "Mujer_2022", "Hombre_2018", "Hombre_2022"]):
            df_prov = df_pivot.groupby("Nombre_Provincia")[["Hombre_2018", "Mujer_2018", "Hombre_2022", "Mujer_2022"]].mean().reset_index()
            df_prov["Brecha_2018"] = df_prov["Hombre_2018"] - df_prov["Mujer_2018"]
            df_prov["Brecha_2022"] = df_prov["Hombre_2022"] - df_prov["Mujer_2022"]

            st.subheader("Brecha Promedio por Provincia")

            fig4, ax4 = plt.subplots(figsize=(8, 6))
            df_prov_sorted = df_prov.sort_values("Brecha_2022", ascending=False)
            ax4.barh(df_prov_sorted["Nombre_Provincia"], df_prov_sorted["Brecha_2022"], color="#77c9d4")
            ax4.set_xlabel("Brecha (Hombre - Mujer) 2022")
            ax4.set_title("Brecha Promedio por Provincia - Año 2022")
            plt.tight_layout()
            st.pyplot(fig4)

        st.subheader("Distribución de Brechas por Comuna")

        fig5, ax5 = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=df_pivot[["Brecha_2018", "Brecha_2022"]], ax=ax5)
        ax5.set_ylabel("Brecha (Hombre - Mujer)")
        ax5.set_title("Distribución de Brechas en Comunas para 2018 y 2022")
        st.pyplot(fig5)

        st.subheader("Mapa de calor de Brechas por Comuna y Año")

        df_heat = df_pivot.set_index("Nombre_comuna")[["Brecha_2018", "Brecha_2022"]]
        fig6, ax6 = plt.subplots(figsize=(10, max(6, len(df_heat)*0.2)))  # Ajusta alto según número comunas
        sns.heatmap(df_heat, cmap="coolwarm", annot=True, fmt=".2f", ax=ax6)
        ax6.set_xlabel("Año")
        ax6.set_ylabel("Comuna")
        st.pyplot(fig6)


        st.subheader("Evolución Completa de Brechas por Comuna (2018-2022)")

        años = [2018, 2022]
        for año in años:
            df_pivot[f"Brecha_{año}"] = df_pivot[f"Hombre_{año}"] - df_pivot[f"Mujer_{año}"]

        fig7, ax7 = plt.subplots(figsize=(12, 6))
        for i in range(len(df_pivot)):
            ax7.plot(años, df_pivot.loc[i, [f"Brecha_{a}" for a in años]], marker='o', label=df_pivot.loc[i, "Nombre_comuna"])
        ax7.set_xticks(años)
        ax7.set_ylabel("Brecha (Hombre - Mujer)")
        ax7.set_title("Evolución Completa de la Brecha por Comuna")
        ax7.grid(True)
        ax7.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
        st.pyplot(fig7)
    else:
        st.warning("No hay columnas suficientes para calcular las brechas para todas las comunas.")



