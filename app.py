import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

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

    # Crear gráfico comparativo entre años 2018 y 2022
    st.subheader("Comparación de brechas por sexo entre 2018 y 2022")

    columnas_necesarias = ["Mujer_2018", "Mujer_2022", "Hombre_2018", "Hombre_2022"]
    if all(col in df_pivot.columns for col in columnas_necesarias):

        comunas_disponibles = df_pivot["Nombre_comuna"].unique()

        for comuna_seleccionada in comunas_disponibles:
            st.markdown(f"### 📍 Comuna: {comuna_seleccionada}")
            df_chart = df_pivot[df_pivot["Nombre_comuna"] == comuna_seleccionada]

        x_labels = ["2018", "2022"]

        # Gráfico de barras
        fig1, ax1 = plt.subplots()
        ax1.bar(x_labels, df_chart[["Mujer_2018", "Mujer_2022"]].values[0], label="Mujer", color=["#ff69b4", "#c71585"])
        ax1.bar(x_labels, -df_chart[["Hombre_2018", "Hombre_2022"]].values[0], label="Hombre", color=["#87ceeb", "#4682b4"])
        ax1.axhline(0, color='black')
        ax1.set_title("Gráfico de Barras: Brechas 2018 vs 2022")
        ax1.legend()
        st.pyplot(fig1)

        # Gráfico de líneas
        fig2, ax2 = plt.subplots()
        ax2.plot(x_labels, df_chart[["Mujer_2018", "Mujer_2022"]].values[0], marker="o", label="Mujer", color="#c71585")
        ax2.plot(x_labels, df_chart[["Hombre_2018", "Hombre_2022"]].values[0], marker="o", label="Hombre", color="#4682b4")
        ax2.set_title("Gráfico de Líneas: Evolución por sexo")
        ax2.legend()
        st.pyplot(fig2)

        # Gráfico de áreas apiladas
        fig3, ax3 = plt.subplots()
        mujer_vals = df_chart[["Mujer_2018", "Mujer_2022"]].values[0]
        hombre_vals = df_chart[["Hombre_2018", "Hombre_2022"]].values[0]
        ax3.stackplot(x_labels, mujer_vals, hombre_vals, labels=["Mujer", "Hombre"], colors=["#ff69b4", "#87ceeb"])
        ax3.set_title("Gráfico de Áreas Apiladas")
        ax3.legend(loc='upper left')
        st.pyplot(fig3)

        # Gráfico de radar
        import numpy as np
        from math import pi

        categories = ['2018', '2022']
        values_mujer = df_chart[["Mujer_2018", "Mujer_2022"]].values.flatten().tolist()
        values_hombre = df_chart[["Hombre_2018", "Hombre_2022"]].values.flatten().tolist()

        # Radar requiere cerrar el círculo
        values_mujer += values_mujer[:1]
        values_hombre += values_hombre[:1]
        angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
        angles += angles[:1]

        fig4, ax4 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax4.plot(angles, values_mujer, color="#c71585", linewidth=2, label='Mujer')
        ax4.fill(angles, values_mujer, color="#c71585", alpha=0.25)

        ax4.plot(angles, values_hombre, color="#4682b4", linewidth=2, label='Hombre')
        ax4.fill(angles, values_hombre, color="#4682b4", alpha=0.25)

        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories)
        ax4.set_title("Gráfico de Radar: Comparación 2018-2022")
        ax4.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        st.pyplot(fig4)

                # Gráfico de dispersión mejorado tipo lollipop
        st.subheader("Gráfico de Dispersión Mejorado (Tipo Lollipop)")

        fig5, ax5 = plt.subplots(figsize=(8, 5))

        x_vals = [2018, 2022]
        mujer_vals = df_chart[["Mujer_2018", "Mujer_2022"]].values[0]
        hombre_vals = df_chart[["Hombre_2018", "Hombre_2022"]].values[0]

        # Líneas horizontales conectando los puntos (lollipop)
        ax5.plot(x_vals, mujer_vals, color='#c71585', marker='o', linewidth=2, markersize=10, label='Mujer')
        ax5.plot(x_vals, hombre_vals, color='#4682b4', marker='o', linewidth=2, markersize=10, label='Hombre')

        # Línea de referencia vertical en el promedio (opcional)
        promedio_valor = (sum(mujer_vals) + sum(hombre_vals)) / 4
        ax5.axhline(y=promedio_valor, color='gray', linestyle='--', linewidth=1, label='Promedio')

        # Títulos y etiquetas
        ax5.set_xticks(x_vals)
        ax5.set_xticklabels(["2018", "2022"])
        ax5.set_ylabel("Valor")
        ax5.set_title("Brechas por Sexo entre 2018 y 2022 (Dispersión + Lollipop)", fontsize=12)
        ax5.legend()
        ax5.grid(True, axis='y', linestyle='--', alpha=0.5)

        # Opcional: anotaciones
        ax5.annotate(f"{mujer_vals[0]:.1f}", (2018, mujer_vals[0]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color="#c71585")
        ax5.annotate(f"{mujer_vals[1]:.1f}", (2022, mujer_vals[1]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color="#c71585")
        ax5.annotate(f"{hombre_vals[0]:.1f}", (2018, hombre_vals[0]), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9, color="#4682b4")
        ax5.annotate(f"{hombre_vals[1]:.1f}", (2022, hombre_vals[1]), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9, color="#4682b4")

        st.pyplot(fig5)



        # Gráfico tipo "dot plot" agrupado (lollipop doble)
        st.subheader("Gráfico de Puntos Agrupados: Comparación por Sexo y Año")

        fig6, ax6 = plt.subplots(figsize=(8, 5))

        # Valores
        mujer_2018 = df_chart["Mujer_2018"].values[0]
        mujer_2022 = df_chart["Mujer_2022"].values[0]
        hombre_2018 = df_chart["Hombre_2018"].values[0]
        hombre_2022 = df_chart["Hombre_2022"].values[0]

        # Coordenadas Y
        categorias = ['2018', '2022']
        y_pos = range(len(categorias))

        # Puntos
        ax6.plot([mujer_2018, mujer_2022], y_pos, marker='o', linestyle='-', color='#c71585', label='Mujer')
        ax6.plot([hombre_2018, hombre_2022], y_pos, marker='o', linestyle='-', color='#4682b4', label='Hombre')

        # Línea vertical de referencia (opcional)
        ax6.axvline(x=0, color='gray', linestyle='--', linewidth=0.7)

        ax6.set_yticks(y_pos)
        ax6.set_yticklabels(categorias)
        ax6.set_xlabel("Valor")
        ax6.set_title("Posición relativa por sexo en 2018 y 2022")
        ax6.legend()
        st.pyplot(fig6)


    else:
        st.warning("Faltan columnas clave como 'Mujer_2018' o 'Hombre_2022' en la tabla pivote para generar los gráficos.")
