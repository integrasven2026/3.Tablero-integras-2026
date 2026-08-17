import io
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# --- 1. SECCIÓN DE FILTROS ---
col1, col2, col3 = st.columns(3)

with col1:
    socios = ["TODOS"] + sorted(df["Socio"].dropna().unique().tolist())
    socio_sel = st.selectbox("Filtrar por Socio:", socios)

with col2:
    sectores = ["TODOS"] + sorted(df["Sector"].dropna().unique().tolist())
    sector_sel = st.selectbox("Filtrar por Sector:", sectores)

with col3:
    localidades = (
        ["TODOS"] + sorted(df["Localidad"].dropna().unique().tolist())
        if "Localidad" in df.columns
        else ["TODOS"]
    )
    localidad_sel = st.selectbox("Filtrar por Localidad:", localidades)

# Aplicar lógica de filtrado
df_filtered = df.copy()

if socio_sel != "TODOS":
    df_filtered = df_filtered[df_filtered["Socio"] == socio_sel]

if sector_sel != "TODOS":
    df_filtered = df_filtered[df_filtered["Sector"] == sector_sel]

if localidad_sel != "TODOS" and "Localidad" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Localidad"] == localidad_sel]


# --- 2. DESCARGA A EXCEL ---
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Seguimiento")

st.download_button(
    label="📊 Descargar reporte en Excel",
    data=buffer.getvalue(),
    file_name="seguimiento_actividades.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# Visualización de la tabla filtrada
st.dataframe(df_filtered, use_container_width=True)


# --- 3. GRÁFICO DE BARRAS (VALOR ABSOLUTO Y PORCENTAJE) ---
if not df_filtered.empty:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras: Valores Absolutos (Alcanzados)
    fig.add_trace(
        go.Bar(
            x=df_filtered["Actividad"],
            y=df_filtered["Alcanzados"],
            name="Alcanzados (Absoluto)",
            text=df_filtered["Alcanzados"],
            textposition="auto",
            marker_color="#2b5c8f",
        ),
        secondary_y=False,
    )

    # Barras: Porcentaje de Avance
    fig.add_trace(
        go.Bar(
            x=df_filtered["Actividad"],
            y=df_filtered["% Avance Socio"],
            name="% Avance Socio",
            text=df_filtered["% Avance Socio"].apply(
                lambda x: f"{x:.1f}%" if pd.notnull(x) else ""
            ),
            textposition="auto",
            marker_color="#e67e22",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title_text="Resultados por Actividad (Absoluto vs. Porcentaje)",
        barmode="group",
        xaxis_title="Actividades",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        height=500,
    )

    fig.update_yaxes(title_text="Alcanzados (Personas / Meta)", secondary_y=False)
    fig.update_yaxes(
        title_text="% Avance", secondary_y=True, showgrid=False, ticksuffix="%"
    )

    st.plotly_chart(fig, use_container_width=True)
