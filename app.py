import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_folium import st_folium
import folium

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (SINTAXIS CORREGIDA: layout="wide")
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tablero Consorcio Integras | COOPI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Tablero de Monitoreo - Consorcio Integras")
st.markdown("**Socio Prime / Líder:** COOPI | **Socios:** HIAS, FLM, PLAFAM, PALUZ")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS DESDE KOBOTOOLBOX (SERVIDOR UNIÓN EUROPEA)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def cargar_datos_kobo(asset_id, token, kobo_url="https://eu.kobotoolbox.org"):
    headers = {"Authorization": f"Token {token}"}
    url = f"{kobo_url}/api/v2/assets/{asset_id}/data.json"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"Error al conectar con KoboToolbox API (Código {response.status_code})")
            return pd.DataFrame()
        
        data = response.json().get('results', [])
        if not data:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Excepción al consultar la API de Kobo: {e}")
        return pd.DataFrame()

    registros_expandidos = []
    
    for row in data:
        sector_raw = str(row.get("Resultado", "")).strip()
        sector_map = {
            "R1": "Protección",
            "R2": "Salud",
            "R3": "Nutrición",
            "R4": "WASH",
            "R5": "Respuesta a Emergencia"
        }
        sector_label = sector_map.get(sector_raw, sector_raw)
        
        base_info = {
            "_id": row.get("_id"),
            "Fecha": row.get("Fecha_de_la_Actividad"),
            "Estado": row.get("Estado"),
            "Municipio": row.get("Municipio"),
            "Comunidad": row.get("Comunidad"),
            "ONG": row.get("ong"),
            "Sector": sector_label,
            "Actividad": row.get("Actividad")
        }
        
        beneficiarios = row.get("group_beneficiario", [])
        if isinstance(beneficiarios, list) and len(beneficiarios) > 0:
            for b in beneficiarios:
                b_info = base_info.copy()
                b_info["Nombre"] = b.get("group_beneficiario/Nombre", "")
                b_info["Apellido"] = b.get("group_beneficiario/Apellido", "")
                b_info["Documento"] = b.get("group_beneficiario/N_de_Documento_de_Identidad", "")
                b_info["CodigoID"] = b.get("group_beneficiario/CodigoID", "")
                
                sexo_raw = str(b.get("group_beneficiario/Sexo", "")).lower().strip()
                b_info["Sexo"] = sexo_raw
                
                try:
                    edad = float(b.get("group_beneficiario/edad_", 0))
                except (ValueError, TypeError):
                    edad = 0
                b_info["Edad"] = edad
                
                # Regla: Menores de 18 años son Niños/Niñas
                if edad < 18:
                    b_info["Grupo_Demografico"] = "Niña" if sexo_raw in ["femenino", "f", "mujer"] else "Niño"
                else:
                    b_info["Grupo_Demografico"] = "Mujer" if sexo_raw in ["femenino", "f", "mujer"] else "Hombre"
                
                registros_expandidos.append(b_info)
        else:
            registros_expandidos.append(base_info)
            
    return pd.DataFrame(registros_expandidos)

# Cargar credenciales desde Secrets
try:
    KOBO_TOKEN = st.secrets["KOBO_TOKEN"]
    ASSET_ID = st.secrets["ASSET_ID"]
    df_raw = cargar_datos_kobo(ASSET_ID, KOBO_TOKEN)
except Exception:
    st.info("👋 Por favor, configura tu `KOBO_TOKEN` y `ASSET_ID` en **Advanced settings -> Secrets** dentro de Streamlit Cloud.")
    st.stop()

if df_raw.empty:
    st.warning("No se encontraron registros en el formulario de KoboToolbox.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. FILTROS LATERALES
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Filtros de Consulta")

socios_disp = ["Todos"] + sorted([x for x in df_raw["ONG"].dropna().unique() if x])
socio_sel = st.sidebar.selectbox("Socio / ONG:", socios_disp)

estados_disp = ["Todos"] + sorted([x for x in df_raw["Estado"].dropna().unique() if x])
estado_sel = st.sidebar.selectbox("Estado:", estados_disp)

df_temp = df_raw if estado_sel == "Todos" else df_raw[df_raw["Estado"] == estado_sel]
munis_disp = ["Todos"] + sorted([x for x in df_temp["Municipio"].dropna().unique() if x])
muni_sel = st.sidebar.selectbox("Municipio:", munis_disp)

sectores_disp = ["Todos"] + sorted([x for x in df_raw["Sector"].dropna().unique() if x])
sector_sel = st.sidebar.selectbox("Sector de Implementación:", sectores_disp)

# Aplicación de filtros
df_filtered = df_raw.copy()
if socio_sel != "Todos":
    df_filtered = df_filtered[df_filtered["ONG"] == socio_sel]
if estado_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Estado"] == estado_sel]
if muni_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Municipio"] == muni_sel]
if sector_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Sector"] == sector_sel]

# -----------------------------------------------------------------------------
# 4. MÉTRICAS CLAVE (KPIs)
# -----------------------------------------------------------------------------
total_impactados = len(df_filtered)

if "Documento" in df_filtered.columns and "CodigoID" in df_filtered.columns:
    df_filtered["ID_Unico"] = df_filtered["Documento"].replace("", None).fillna(df_filtered["CodigoID"])
    total_unicos = df_filtered["ID_Unico"].nunique()
else:
    total_unicos = total_impactados

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Impactados", f"{total_impactados:,}")
col2.metric("Participantes Únicos", f"{total_unicos:,}")
col3.metric("Estados Atendidos", df_filtered["Estado"].nunique() if total_impactados > 0 else 0)
col4.metric("Municipios", df_filtered["Municipio"].nunique() if total_impactados > 0 else 0)
col5.metric("Sectores", df_filtered["Sector"].nunique() if total_impactados > 0 else 0)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. GRUPOS DE PARTICIPANTES (% MUJERES, HOMBRES, NIÑAS, NIÑOS)
# -----------------------------------------------------------------------------
st.subheader("👥 Grupos de Participantes")

if total_impactados > 0 and "Grupo_Demografico" in df_filtered.columns:
    counts = df_filtered["Grupo_Demografico"].value_counts()
    
    p_mujeres = (counts.get("Mujer", 0) / total_impactados) * 100
    p_hombres = (counts.get("Hombre", 0) / total_impactados) * 100
    p_ninas = (counts.get("Niña", 0) / total_impactados) * 100
    p_ninos = (counts.get("Niño", 0) / total_impactados) * 100

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("% Mujeres (≥18 años)", f"{p_mujeres:.1f}%")
    d2.metric("% Hombres (≥18 años)", f"{p_hombres:.1f}%")
    d3.metric("% Niñas (<18 años)", f"{p_ninas:.1f}%")
    d4.metric("% Niños (<18 años)", f"{p_ninos:.1f}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS INTERACTIVOS (BARRAS Y TORTA)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Desglose por Sexo y Rango Etario")
    if total_impactados > 0 and "Grupo_Demografico" in df_filtered.columns:
        df_demo = df_filtered.groupby("Grupo_Demografico").size().reset_index(name="Cantidad")
        fig_bar = px.bar(
            df_demo, 
            x="Grupo_Demografico", 
            y="Cantidad", 
            color="Grupo_Demografico",
            text="Cantidad",
            title="Participantes por Rango Etario y Sexo",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

with g2:
    st.subheader("🥧 Participantes Únicos por Sector")
    if total_impactados > 0 and "Sector" in df_filtered.columns:
        df_sec_unicos = df_filtered.drop_duplicates(subset=["ID_Unico", "Sector"])
        df_sec_cnt = df_sec_unicos["Sector"].value_counts().reset_index()
        df_sec_cnt.columns = ["Sector", "Unicos"]
        
        fig_pie = px.pie(
            df_sec_cnt, 
            values="Unicos", 
            names="Sector",
            hole=0.4,
            title="Distribución por Sector de Implementación",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. UBICACIÓN GEOGRÁFICA Y BARRAS POR MUNICIPIO
# -----------------------------------------------------------------------------
st.subheader("🗺️ Ubicación Geográfica por Municipio")

m1, m2 = st.columns([1, 1])

with m1:
    st.markdown("### Participantes Impactados por Municipio")
    if total_impactados > 0 and "Municipio" in df_filtered.columns:
        df_muni = df_filtered.groupby(["Estado", "Municipio"]).size().reset_index(name="Impactados")
        df_muni = df_muni.sort_values(by="Impactados", ascending=True)
        
        fig_muni = px.bar(
            df_muni,
            y="Municipio",
            x="Impactados",
            color="Estado",
            orientation="h",
            text="Impactados",
            height=400
        )
        fig_muni.update_traces(textposition="outside")
        st.plotly_chart(fig_muni, use_container_width=True)

with m2:
    st.markdown("### Cobertura de la Intervención")
    mapa = folium.Map(location=[7.8, -65.5], zoom_start=6, tiles="CartoDB positron")
    st_folium(mapa, width=500, height=380)
   
