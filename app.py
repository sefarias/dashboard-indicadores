import pandas as pd
import streamlit as st
import os
import plotly.express as px
import geopandas as gpd

st.set_page_config(layout="wide")

# Diccionario de indicadores
indicadores = {
    "Brechas de Ingresos": {"carpeta": "Datos/BRECHAS_ING", "prefijo": "Brechas_Ingresos_Region_"},
    "Brechas de Matrícula": {"carpeta": "Datos/BRECHAS_MAT", "prefijo": "Brechas_Matricula_Region_"},
    "Brechas de Ocupación": {"carpeta": "Datos/BRECHAS_OCU", "prefijo": "Brechas_Ocupacion_Region_"},
    "Dependencia": {"carpeta": "Datos/DEPENDENCIA", "prefijo": "Dependencia_Region_"}
}

# Diccionario de nombres más legibles
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

# Función para obtener mapeo de regiones
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

# Función para formatear números con coma y 2 decimales
def format_number(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Sidebar para seleccionar indicador y región
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

# Mantener columnas de códigos para merge
columnas_codigos = ["Cod_Comuna", "Codigo_Region"]

# Columnas a mostrar con nombres legibles
columnas_mostrar = [
    "Nombre_Region", "Nombre_Provincia", "Nombre_comuna", "Sexo",
    "YEAR_2018", "YEAR_2019", "YEAR_2020", "YEAR_2021", "YEAR_2022", "YEAR_2023"
]

columnas_presentes = [col for col in columnas_mostrar + columnas_codigos if col in df.columns]

# Renombrar solo las columnas de visualización
columnas_renombrar = {k:v for k,v in mapa_columnas.items() if k in df.columns}
df_filtrado = df[columnas_presentes].rename(columns=columnas_renombrar)

# Mostrar tabla
st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codigo_region})")
st.dataframe(df_filtrado.style.format(lambda x: format_number(x) if isinstance(x, float) else x), use_container_width=True)

# ============= GRÁFICOS ESPECIALES PARA DEPENDENCIA =============
if indicador == "Dependencia":
    columnas_anos = [col for col in df_filtrado.columns if col.startswith("Año ")]
    df_dep = df_filtrado.copy()

    # --- Selección de año para gráfico de columnas en el flujo central ---
    anio_seleccionado = st.selectbox(
        "Selecciona el año para el gráfico de columnas",
        columnas_anos,
        index=columnas_anos.index("Año 2022") if "Año 2022" in columnas_anos else 0
    )

    # Gráfico de Columnas
    st.subheader(f"Gráfico de Columnas - {anio_seleccionado}")
    fig_bar = px.bar(
        df_dep.sort_values(anio_seleccionado, ascending=False),
        x="Comuna",
        y=anio_seleccionado,
        color="Comuna",
        text=anio_seleccionado,
        labels={"Comuna": "Comuna", anio_seleccionado: "Valor"},
        title=f"Dependencia por Comuna - {anio_seleccionado}"
    )
    fig_bar.update_traces(
        texttemplate=[format_number(v) for v in df_dep[anio_seleccionado]],
        textposition='outside',
        hovertemplate=[f"Comuna: {c}<br>Valor: {format_number(v)}" for c, v in zip(df_dep["Comuna"], df_dep[anio_seleccionado])]
    )
    fig_bar.update_layout(
        xaxis_tickangle=-90,
        showlegend=False,
        yaxis=dict(title="Valor (%)", range=[0, 100])
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de Líneas
    st.subheader("Evolución de Dependencia por Comuna (Serie Completa)")
    df_melt = df_dep.melt(id_vars=["Comuna"], value_vars=columnas_anos,
                          var_name="Año", value_name="Valor")
    fig_line = px.line(
        df_melt,
        x="Año",
        y="Valor",
        color="Comuna",
        markers=True,
        title="Evolución de la Dependencia por Comuna",
        custom_data=["Comuna", "Valor"]
    )
    fig_line.update_traces(
        mode="lines+markers",
        hovertemplate="Comuna: %{customdata[0]}<br>Año: %{x}<br>Valor: %{customdata[1]:.2f} %"
    )
    fig_line.update_layout(
        yaxis=dict(title="Valor (%)", range=[0, 100]),
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ===== MAPA DE DEPENDENCIA POR COMUNA =====
st.subheader(f"Mapa de Dependencia por Comuna - {anio_seleccionado}")
try:
    gdf = gpd.read_file(r"F:/Users/sfarias/Documents/Curso Python/.vscode/dashboard-indicadores/Datos/MAPAS/comunas_tratadas/comunas_continental.shp")
    
    # Merge usando cod_comuna y Cod_Comuna
    gdf_merged = gdf.merge(df_dep, left_on='cod_comuna', right_on='Cod_Comuna', how='inner')
    
    # Filtrar por región seleccionada
    gdf_merged_region = gdf_merged[gdf_merged['Codigo_Region'] == codigo_region].copy()
    
    # Renombrar la columna de comuna para Plotly
    gdf_merged_region = gdf_merged_region.rename(columns={"Comuna_y": "Comuna"})
    
    # Graficar
    fig_map = px.choropleth_mapbox(
        gdf_merged_region,
        geojson=gdf_merged_region.geometry.__geo_interface__,
        locations=gdf_merged_region.index,
        color=anio_seleccionado,
        hover_name="Comuna",
        hover_data={anio_seleccionado: ':.2f'},
        mapbox_style="carto-positron",
        center={"lat": gdf_merged_region.geometry.centroid.y.mean(),
                "lon": gdf_merged_region.geometry.centroid.x.mean()},
        zoom=6,
        color_continuous_scale="Viridis"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

except Exception as e:
    st.error(f"No se pudo generar el mapa: {e}")

