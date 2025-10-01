import pandas as pd
import streamlit as st
import os
import plotly.express as px
import geopandas as gpd

st.set_page_config(layout="wide")

# ================= DICCIONARIOS =================
indicadores = {
    "Brechas de Ingresos": {"carpeta": "Datos/BRECHAS_ING", "prefijo": "Brechas_Ingresos_Region_"},
    "Brechas de Matrícula": {"carpeta": "Datos/BRECHAS_MAT", "prefijo": "Brechas_Matricula_Region_"},
    "Brechas de Ocupación": {"carpeta": "Datos/BRECHAS_OCU", "prefijo": "Brechas_Ocupacion_Region_"},
    "Dependencia": {"carpeta": "Datos/DEPENDENCIA", "prefijo": "Dependencia_Region_"}
}

mapa_columnas = {
    "Nombre_Region": "Región",
    "Nombre_Provincia": "Provincia",
    "Nombre_comuna": "Comuna",
    "Sexo": "Sexo",
    "YEAR_2018": "Año 2018",
    "YEAR_2019": "Año 2019",
    "YEAR_2020": "Año 2020",
    "YEAR_2021": "Año 2021",
    "YEAR_2022": "Año 2022",
    "YEAR_2023": "Año 2023",
    "Hombre_2018": "Hombres 2018",
    "Mujer_2018": "Mujeres 2018",
    "Hombre_2022": "Hombres 2022",
    "Mujer_2022": "Mujeres 2022",
    "Brecha_2018": "Brecha 2018 (H-M)",
    "Brecha_2022": "Brecha 2022 (H-M)"
}

# ================= FUNCIONES =================
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

def format_number(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ================= SIDEBAR =================
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
info = indicadores[indicador]

mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codigo_region = mapeo_regiones[nombre_region]

# ================= LEER DATOS =================
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codigo_region}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# Normalización de códigos de comuna
if "Cod_Comuna" in df.columns:
    df["Cod_Comuna"] = df["Cod_Comuna"].astype(str).str.zfill(5)

# ================= TABLA =================
columnas_mostrar = [
    "Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo",
    "YEAR_2018", "YEAR_2019", "YEAR_2020", "YEAR_2021", "YEAR_2022", "YEAR_2023"
]
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes].rename(columns=mapa_columnas)

st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado.style.format(lambda x: format_number(x) if isinstance(x, float) else x), use_container_width=True)

# ================= MAPA =================
if indicador == "Dependencia":
    try:
        # Cargar shapefile de comunas
        shp_path = r"F:\Users\sfarias\Documents\Curso Python\.vscode\dashboard-indicadores\Datos\MAPAS\comunas_tratadas\comunas_continental.shp"
        gdf = gpd.read_file(shp_path)

        # Normalizar códigos de comuna en el shapefile
        gdf["cod_comuna"] = gdf["cod_comuna"].astype(str).str.zfill(5)
        gdf = gdf.rename(columns={"cod_comuna": "Cod_Comuna"})

        # Merge shapefile + datos
        gdf_merged = gdf.merge(df, on="Cod_Comuna", how="left")

        # Selección de año
        columnas_anos = [col for col in df_filtrado.columns if col.startswith("Año ")]
        anio_mapa = st.selectbox("Selecciona el año para visualizar en el mapa", columnas_anos, index=len(columnas_anos)-1)

        # Mapa
        st.subheader(f"Mapa de Dependencia - {anio_mapa}")
        fig_map = px.choropleth(
            gdf_merged,
            geojson=gdf_merged.geometry,
            locations=gdf_merged.index,
            color=anio_mapa,
            hover_name="Comuna",
            projection="mercator",
            color_continuous_scale="RdYlGn_r",
            labels={anio_mapa: "Valor (%)"}
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_coloraxes(colorbar_title="Valor (%)")
        st.plotly_chart(fig_map, use_container_width=True)

    except Exception as e:
        st.warning(f"No se pudo generar el mapa: {e}")
