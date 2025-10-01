import os
import pandas as pd
import streamlit as st
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
                if "codregion" in df_temp.columns and "Nombre_Region" in df_temp.columns:
                    regiones_list.append(df_temp[["codregion", "Nombre_Region"]])
            except Exception as e:
                st.warning(f"Error leyendo {archivo}: {e}")
    if regiones_list:
        regiones_concat = pd.concat(regiones_list).drop_duplicates()
        return dict(zip(regiones_concat["Nombre_Region"], regiones_concat["codregion"]))
    return {}

# Formato números
def format_number(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Sidebar: indicador y región
indicador = st.sidebar.selectbox("Selecciona el indicador", list(indicadores.keys()))
info = indicadores[indicador]

mapeo_regiones = obtener_mapeo_regiones(info)
if not mapeo_regiones:
    st.error("No se pudo leer la lista de regiones.")
    st.stop()

nombre_region = st.sidebar.selectbox("Selecciona la región", sorted(mapeo_regiones.keys()))
codregion = mapeo_regiones[nombre_region]

# Leer archivo
archivo = os.path.join(info["carpeta"], f"{info['prefijo']}{codregion}.xlsx")
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo para la región {nombre_region}.")
    st.stop()

# Filtrar columnas y renombrar
columnas_mostrar = ["Nombre_Region","Nombre_Provincia","Nombre_comuna","Sexo",
                    "YEAR_2018","YEAR_2019","YEAR_2020","YEAR_2021","YEAR_2022","YEAR_2023","cod_comuna"]
columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
df_filtrado = df[columnas_presentes].rename(columns=mapa_columnas)

st.subheader(f"Datos seleccionados - {indicador} - {nombre_region} (Región {codregion})")
st.dataframe(df_filtrado.style.format(lambda x: format_number(x) if isinstance(x,float) else x), use_container_width=True)

# ============ Dependencia: gráficos y mapa ============
if indicador == "Dependencia":
    columnas_anos = [col for col in df_filtrado.columns if col.startswith("Año ")]
    df_dep = df_filtrado.copy()

    # Selección año para gráfico de columnas
    anio_seleccionado = st.selectbox("Selecciona el año para el gráfico de columnas",
                                     columnas_anos,
                                     index=columnas_anos.index("Año 2022") if "Año 2022" in columnas_anos else 0)

    # Gráfico de columnas
    st.subheader(f"Gráfico de Columnas - {anio_seleccionado}")
    fig_bar = px.bar(
        df_dep.sort_values(anio_seleccionado, ascending=False),
        x="Comuna",
        y=anio_seleccionado,
        color="Comuna",
        text=anio_seleccionado,
        labels={"Comuna":"Comuna", anio_seleccionado:"Valor"},
        title=f"Dependencia por Comuna - {anio_seleccionado}"
    )
    fig_bar.update_traces(
        texttemplate=[format_number(v) for v in df_dep[anio_seleccionado]],
        textposition='outside',
        hovertemplate=[f"Comuna: {c}<br>Valor: {format_number(v)}" for c,v in zip(df_dep["Comuna"], df_dep[anio_seleccionado])]
    )
    fig_bar.update_layout(xaxis_tickangle=-90, showlegend=False, yaxis=dict(title="Valor (%)", range=[0,100]))
    st.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de líneas serie completa
    st.subheader("Evolución de Dependencia por Comuna (Serie Completa)")
    df_melt = df_dep.melt(id_vars=["Comuna"], value_vars=columnas_anos,
                          var_name="Año", value_name="Valor")
    fig_line = px.line(df_melt, x="Año", y="Valor", color="Comuna", markers=True, title="Evolución de la Dependencia por Comuna",
                       custom_data=["Comuna","Valor"])
    fig_line.update_traces(mode="lines+markers",
                           hovertemplate="Comuna: %{customdata[0]}<br>Año: %{x}<br>Valor: %{customdata[1]:.2f} %")
    fig_line.update_layout(yaxis=dict(title="Valor (%)", range=[0,100]), hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

# ================= Mapa de Dependencia =================
st.subheader("Mapa de Dependencia por Comuna (Continental)")

# Leer shapefile continental
shapefile_path = r"F:\Users\sfarias\Documents\Curso Python\.vscode\dashboard-indicadores\Datos\MAPAS\comunas_tratadas\comunas_continental.shp"
if not os.path.exists(shapefile_path):
    st.error("No se encontró el shapefile continental. Verifica la ruta.")
else:
    gdf = gpd.read_file(shapefile_path)

    # Filtrar por la región seleccionada
    gdf_region = gdf[gdf['codregion'] == codregion]

    # Merge con datos de dependencia
    df_merge = df_dep.copy()
    if 'cod_comuna' not in gdf_region.columns:
        st.error("El shapefile no tiene la columna 'cod_comuna'.")
    else:
        gdf_region = gdf_region.merge(df_merge, left_on='cod_comuna', right_on='cod_comuna')

        # Reproyectar a lat/lon
        gdf_region = gdf_region.to_crs(epsg=4326)

        # Comprobar geometría vacía
        n_empty = gdf_region.geometry.is_empty.sum()
        if n_empty > 0:
            st.warning(f"{n_empty} comunas no tienen geometría válida y no se mostrarán.")

        # Determinar columna de hover
        if 'Comuna_y' in gdf_region.columns:
            hover_col = 'Comuna_y'
        elif 'Nombre_comuna' in gdf_region.columns:
            hover_col = 'Nombre_comuna'
        else:
            hover_col = 'cod_comuna'

        # Ajustar rango de color según los datos
        min_val = gdf_region[anio_seleccionado].min()
        max_val = gdf_region[anio_seleccionado].max()

        # Crear choropleth
        fig_map = px.choropleth(
            gdf_region,
            geojson=gdf_region.__geo_interface__,
            locations=gdf_region.index,
            color=anio_seleccionado,
            hover_name=hover_col,
            projection="mercator",
            color_continuous_scale="Viridis",
            range_color=(min_val, max_val)
        )

        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_colorbar=dict(title="Dependencia (%)")
        )

        st.plotly_chart(fig_map, use_container_width=True)


