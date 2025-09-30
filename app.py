import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Función para formatear números con coma y 2 decimales
# ---------------------------
def format_number(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------------------
# Configuración de la app
# ---------------------------
st.set_page_config(page_title="Análisis CASEN 2024 - Educación", layout="wide")

st.title("📊 Análisis CASEN 2024 - Educación")

# Cargar archivo Excel
archivo = st.file_uploader("Sube un archivo Excel con los indicadores", type=["xlsx"])

if archivo:
    # Mostrar nombres de hojas
    xls = pd.ExcelFile(archivo)
    hoja = st.selectbox("Selecciona el indicador", xls.sheet_names)

    df = pd.read_excel(archivo, sheet_name=hoja)

    st.subheader("Datos Tabulados")
    # Mostrar tabla con formato decimal coma y 2 decimales
    st.dataframe(df.style.format(lambda x: format_number(x) if isinstance(x, float) else x))

    # ---------------------------
    # Indicador Dependencia: gráficos especiales
    # ---------------------------
    if hoja.lower() == "dependencia":
        # Selección de año
        anios = [c for c in df.columns if c != "Comuna"]
        anio_seleccionado = st.selectbox("Selecciona un año para el gráfico de columnas", anios)

        df_dep = df.copy()

        # 📊 Gráfico de Barras
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

        # Formateo de valores en texto y hover
        fig_bar.update_traces(
            texttemplate="%{y:.2f}",
            textposition="outside",
            hovertemplate="Comuna: %{x}<br>Valor: %{y:.2f}"
        )

        # Eje Y fijo en 0–100 y formato ticks con coma
        fig_bar.update_layout(
            xaxis_tickangle=-90,
            showlegend=False,
            yaxis=dict(title="Valor (%)", range=[0, 100], tickformat=".2f")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 📈 Gráfico de Líneas
        st.subheader("Gráfico de Líneas - Serie Completa")
        df_long = df_dep.melt(id_vars="Comuna", var_name="Año", value_name="Valor")

        fig_line = px.line(
            df_long,
            x="Año",
            y="Valor",
            color="Comuna",
            markers=True,
            labels={"Valor": "Valor (%)", "Año": "Año"},
            title="Serie de Dependencia por Comuna"
        )

        # Tooltip y formato de hover
        fig_line.update_traces(
            hovertemplate="Comuna: %{legendgroup}<br>Año: %{x}<br>Valor: %{y:.2f}"
        )

        # Eje Y fijo en 0–100 y ticks con coma
        fig_line.update_layout(
            yaxis=dict(title="Valor (%)", range=[0, 100], tickformat=".2f"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_line, use_container_width=True)
