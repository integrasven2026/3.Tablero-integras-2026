import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Tablero INTEGRAS 2026 - COOPI",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. CARGA Y PREPARACIÓN DE DATOS (Simulación / Carga desde Kobo + GitHub)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_data():
    # Sustituir esta estructura por tu lectura real desde API Kobo / GitHub
    # Ejemplo de estructura de datos de registros de atenciones/servicios
    data = {
        "id_servicio": range(1, 389),
        "id_participante": [f"PART-{i}" for i in np.random.randint(1, 193, 388)],
        "mes": np.random.choice(["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"], 388),
        "socio": np.random.choice(["COOPI", "LWF", "PUI", "CESVI"], 388),
        "estado": np.random.choice(["Distrito Capital", "Miranda", "La Guaira", "Bolívar", "Sucre"], 388),
        "municipio": np.random.choice(["Libertador", "Chacao", "Vargas", "Caroni", "Sucre"], 388),
        "sector": np.random.choice(["Protección", "WASH", "Salud"], 388),
        "actividad": np.random.choice([
            "General Protection Case Management", 
            "Child-Friendly Spaces (CFS)", 
            "Individual Protection Assistance (IPA)",
            "IPC Equipment & Bio-safety", 
            "Essential Health & Medicines"
        ], 388),
        "sexo": np.random.choice(["Femenino", "Masculino", "Otro"], 388),
        "grupo_demografico": np.random.choice(["Niños (<18)", "Adultos (18-59)", "Adultos Mayores (60+)"], 388)
    }
    df = pd.DataFrame(data)
    
    # Limpieza de espacios en blanco
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

df_raw = load_data()

# Carga de Metas por Proyecto y Socio (Tabla de Referencia)
metas_data = {
    "sector": ["Protección", "Protección", "Protección", "WASH", "Salud"],
    "actividad": [
        "General Protection Case Management", 
        "Child-Friendly Spaces (CFS)", 
        "Individual Protection Assistance (IPA)",
        "IPC Equipment & Bio-safety", 
        "Essential Health & Medicines"
    ],
    "meta_proyecto": [2108, 3526, 3194, 2752, 752]
}
df_metas = pd.DataFrame(metas_data)

# -----------------------------------------------------------------------------
# 2. PANEL LATERAL (SIDEBAR) - FILTROS GENERALES
# -----------------------------------------------------------------------------
st.sidebar.title("Sincronización Híbrida\n(Kobo + GitHub)")

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("🔄 Actualizar"):
    st.cache_data.clear()
    st.rerun()

if col_btn2.button("🧹 Limpiar Filtros"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros de Consulta General")

# Listas de opciones dinámicas con opción 'Todos'
lista_meses = ["Todos"] + sorted(list(df_raw["mes"].unique()))
lista_socios = ["Todos"] + sorted(list(df_raw["socio"].unique()))
lista_estados = ["Todos"] + sorted(list(df_raw["estado"].unique()))
lista_sectores = ["Todos"] + sorted(list(df_raw["sector"].unique()))
lista_sexos = ["Todos"] + sorted(list(df_raw["sexo"].unique()))
lista_grupos = ["Todos"] + sorted(list(df_raw["grupo_demografico"].unique()))

# Selectboxes del Sidebar
mes_sel = st.sidebar.selectbox("Mes del Reporte:", lista_meses, key="sb_mes")
socio_sidebar = st.sidebar.selectbox("Socio / ONG:", lista_socios, key="sb_socio")
estado_sidebar = st.sidebar.selectbox("Estado:", lista_estados, key="sb_estado")
sector_sidebar = st.sidebar.selectbox("Sector de Implementación:", lista_sectores, key="sb_sector")
sexo_sel = st.sidebar.selectbox("Sexo del Participante:", lista_sexos, key="sb_sexo")
grupo_sel = st.sidebar.selectbox("Grupo Demográfico:", lista_grupos, key="sb_grupo")

# -----------------------------------------------------------------------------
# 3. LÓGICA DE FILTRADO EN CASCADA
# -----------------------------------------------------------------------------
df_filtrado = df_raw.copy()

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["mes"] == mes_sel]
if socio_sidebar != "Todos":
    df_filtrado = df_filtrado[df_filtrado["socio"] == socio_sidebar]
if estado_sidebar != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sidebar]
if sector_sidebar != "Todos":
    df_filtrado = df_filtrado[df_filtrado["sector"] == sector_sidebar]
if sexo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["sexo"] == sexo_sel]
if grupo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["grupo_demografico"] == grupo_sel]

# -----------------------------------------------------------------------------
# 4. PANEL PRINCIPAL - METRICAS Y FILTROS SECUNDARIOS (INLINE)
# -----------------------------------------------------------------------------
st.subheader("Seguimiento General del Proyecto INTEGRAS")

# Cálculo de KPIs superiores
total_servicios = len(df_filtrado)
participantes_unicos = df_filtrado["id_participante"].nunique()
meta_global = 46122
porcentaje_alcance = (participantes_unicos / meta_global) * 100

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Total de Servicios a Participantes", f"{total_servicios:,}")
col_kpi2.metric("Total Participantes Únicos", f"{participantes_unicos:,}")
col_kpi3.metric(f"% Alcance de la Meta ({meta_global:,} pers.)", f"{porcentaje_alcance:.2f}%")

st.markdown("---")
st.title("Seguimiento de Actividades por Socio, Sector y Localidad")

# Filtros locales interactivos dentro de la vista principal
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    socio_local = st.selectbox(
        "Filtrar Reporte por Socio:", 
        ["TODOS"] + sorted(list(df_filtrado["socio"].unique())),
        key="local_socio"
    )

with f_col2:
    sector_local = st.selectbox(
        "Filtrar por Sector:", 
        ["TODOS"] + sorted(list(df_filtrado["sector"].unique())),
        key="local_sector"
    )

with f_col3:
    estado_local = st.selectbox(
        "Filtrar por Localidad (Estado):", 
        ["TODOS"] + sorted(list(df_filtrado["estado"].unique())),
        key="local_estado"
    )

# Aplicar filtros secundarios locales al DataFrame
df_tabla = df_filtrado.copy()

if socio_local != "TODOS":
    df_tabla = df_tabla[df_tabla["socio"] == socio_local]
if sector_local != "TODOS":
    df_tabla = df_tabla[df_tabla["sector"] == sector_local]
if estado_local != "TODOS":
    df_tabla = df_tabla[df_tabla["estado"] == estado_local]

# -----------------------------------------------------------------------------
# 5. CONSTRUCCIÓN Y CÁLCULO DE LA TABLA DINÁMICA DE SEGUIMIENTO
# -----------------------------------------------------------------------------
# Agrupar alcances reales por Sector y Actividad
alcanzados_df = df_tabla.groupby(["sector", "actividad"]).agg(
    Alcanzados=("id_servicio", "count")
).reset_index()

# Fusionar metas teóricas con el alcance real filtrado
df_resumen = pd.merge(df_metas, alcanzados_df, on=["sector", "actividad"], how="left")
df_resumen["Alcanzados"] = df_resumen["Alcanzados"].fillna(0).astype(int)

# Asignar Socio según el filtro seleccionado
if socio_local != "TODOS":
    df_resumen["Socio"] = socio_local
elif socio_sidebar != "Todos":
    df_resumen["Socio"] = socio_sidebar
else:
    df_resumen["Socio"] = "TODOS (Consorcio)"

# Asignar Metas del Socio
df_resumen["Meta Socio"] = df_resumen["meta_proyecto"]

# Calcular porcentaje de avance dinámico
df_resumen["% Avance Socio"] = np.where(
    df_resumen["Meta Socio"] > 0,
    (df_resumen["Alcanzados"] / df_resumen["Meta Socio"]) * 100,
    0.0
)

# Renombrar y ordenar columnas finales
df_final = df_resumen[[
    "sector", "actividad", "Socio", "meta_proyecto", "Meta Socio", "Alcanzados", "% Avance Socio"
]].rename(columns={
    "sector": "Sector",
    "actividad": "Actividad",
    "meta_proyecto": "Meta Proyecto",
    "% Avance Socio": "% Avance Socio"
})

# -----------------------------------------------------------------------------
# 6. RENDERIZADO DE LA TABLA CON FORMATO
# -----------------------------------------------------------------------------
st.dataframe(
    df_final.style.format({
        "Meta Proyecto": "{:,.0f}",
        "Meta Socio": "{:,.0f}",
        "Alcanzados": "{:,.0f}",
        "% Avance Socio": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)
