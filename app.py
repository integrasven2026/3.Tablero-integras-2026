import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_folium import st_folium
import folium
import os

# -----------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL CONSORCIO INTEGRAS
# -----------------------------------------------------------------------------
COLOR_AGUAMARINA = '#17C3B2'  # Verde / Azul Agua Marina oficial

PALETA_INTEGRAS = [
    COLOR_AGUAMARINA,  # Turquesa / Agua Marina
    '#D89FE3',         # Morado / Orquídea
    '#F3A738',         # Naranja / Dorado
    '#08327D',         # Azul Marino
    '#0072CE'          # Azul Celeste
]

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y FUENTES PERSONALIZADAS (CSS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tablero Consorcio Integras | COOPI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de Fuentes: Quicksand y Now (o Montserrat como fallback de Now)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Quicksand:wght@600;700&display=swap');

    /* Aplicar Quicksand Bold a todo el cuerpo de la aplicación */
    html, body, [class*="css"], .stMarkdown, p, div, span, label, input, button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Tipografía para los Títulos principales y subsecciones (Now Bold / Montserrat) */
    h1, h2, h3, h4, h5, h6, .stSubheader {
        font-family: 'Now', 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Personalización del Título Principal */
    .titulo-principal {
        font-family: 'Now', 'Montserrat', sans-serif !important;
        color: #17C3B2 !important;
        margin-bottom: 5px !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ENCABEZADO Y LOGO
# -----------------------------------------------------------------------------
col_header_title, col_header_logo = st.columns([3, 1])

with col_header_title:
    # Título principal en color Azul Agua Marina (#17C3B2) con fuente Now Bold
    st.markdown(
        f"<h1 class='titulo-principal'>Tablero de Monitoreo - Consorcio Integras</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("**Socio Prime / Líder:** COOPI | **Socios:** HIAS, FLM, PLAFAM, PALUZ")

with col_header_logo:
    # Búsqueda flexible del archivo del logo
    posibles_nombres = ["Integras_logo.jpg", "Integras_logo.png", "integras_logo.jpg", "integras_logo.png", "Integras_logo.jpeg"]
    logo_path = None
    
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            logo_path = nombre
            break

    if logo_path:
        try:
            st.image(logo_path, use_container_width=True)
        except TypeError:
            st.image(logo_path, use_column_width=True)
    else:
        st.warning("⚠️ Coloque el archivo 'Integras_logo.jpg' en la misma carpeta del script.")

st.markdown("---")

# META TOTAL DEL PROYECTO
META_PARTICIPANTES_UNICOS = 46122

# Diccionario de Meses en Español
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Mapeo de Códigos a Nombres Reales (Estados y Municipios)
MAPA_ESTADOS = {
    "VE01": "Distrito Capital",
    "VE07": "Bolívar",
    "VE10": "Delta Amacuro",
    "VE15": "Miranda",
    "VE19": "Sucre",
    "VE24": "La Guaira"
}

MAPA_MUNICIPIOS = {
    "VE0101": "Libertador",
    "VE0701": "Caroní",
    "VE0707": "Angostura",
    "VE1003": "Pedernales",
    "VE1004": "Tucupita",
    "VE1515": "Paz Castillo",
    "VE1519": "Sucre (Miranda)",
    "VE1520": "Urdaneta",
    "VE1903": "Arismendi",
    "VE1905": "Bermúdez",
    "VE1908": "Cruz Salmerón Acosta",
    "VE1914": "Sucre (Sucre)",
    "VE2401": "Vargas"
}

COORDENADAS_MUNICIPIOS = {
    "Libertador": [10.5000, -66.9167],
    "Caroní": [8.2833, -62.7167],
    "Angostura": [7.5333, -63.8833],
    "Pedernales": [9.9667, -62.2500],
    "Tucupita": [9.0622, -62.0531],
    "Paz Castillo": [10.2167, -66.6667],
    "Sucre (Miranda)": [10.4833, -66.8167],
    "Urdaneta": [10.1500, -66.8833],
    "Arismendi": [10.7167, -62.5167],
    "Bermúdez": [10.6333, -63.2500],
    "Cruz Salmerón Acosta": [10.6167, -64.2000],
    "Sucre (Sucre)": [10.2833, -63.8833],
    "Vargas": [10.6000, -66.9333]
}

MAPA_INDICADORES = {
    "R1I2": "R1I2: Porcentaje de niños y cuidadores cuyas necesidades/riesgos urgentes de protección infantil se han abordado a través del proceso de gestión de casos.",
    "R1I3": "R1I3: Número de personas que accedieron a asistencia jurídica gratuita.",
    "R1I4": "R1I4: Porcentaje de aumento del conocimiento entre los participantes sobre el tema de protección en cuestión.",
    "R1I5": "R1I5: Porcentaje de las personas que reciben apoyo psicosocial adecuado informan de una mejoría en su salud mental y bienestar psicosocial O en su capacidad para afrontar las dificultades.",
    "R1I6": "R1I6: Porcentaje de casos de alto riesgo de violencia de género supervisados. (KRI)",
    "R1SI": "R1SI: Sin indicador",
    "R2I1": "R2I1: Número total de consultas de atención primaria de salud",
    "R2I2": "R2I2: Porcentaje de partos atendidos por personal sanitario cualificado (médicos, enfermeras, matronas)",
    "R2I3": "R2I3: Número de consultas por staff al día",
    "R2I4": "R2I4: Tasa de abandono ANC4/ANC1",
    "R2I5": "R2I5: Número de centros sanitarios que implementan la segregación de residuos y siguen las normas de gestión y tratamiento recomendadas.",
    "R2SI": "R2SI: Sin indicador",
    "R3I1": "R3I1: Número de niños menores de 5 años ingresados para el tratamiento de la desnutrición aguda grave o moderada",
    "R3I2": "R3I2: Número de mujeres embarazadas y/o lactantes ingresadas para tratamiento por desnutrición aguda moderada grave o de alto riesgo.",
    "R3SI": "R3SI: Sin indicador",
    "R4I1": "R4I1: Número de personas beneficiarias que tienen acceso a agua suficiente y segura para uso doméstico.",
    "R4I2": "R4I2: Número de personas que tienen acceso regular y adecuado al jabón para satisfacer sus necesidades higiénicas.",
    "R4I3": "R4I3: Número de personas con acceso a instalaciones dignas, seguras, limpias y funcionales para la eliminación de excretas.",
    "R4I4": "R4I4: Porcentaje de la población objetivo que recibió asistencia y que fue sensibilizada sobre prácticas seguras de gestión de residuos.",
    "R4SI": "R4SI: Sin indicador",
    "R5I1": "R5I1: Número de personas cubiertas por los planes de acción temprana/contingencia.",
    "R5I2": "R5I2: Número de alertas atendidas",
    "R5SI": "R5SI: Sin indicador"
}

# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS DESDE KOBOTOOLBOX
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
        sector_raw = str(row.get("Resultado") or row.get("group_datos_act/Resultado") or "").strip()
        sector_map = {
            "R1": "Protección",
            "R2": "Salud",
            "R3": "Nutrición",
            "R4": "WASH",
            "R5": "Respuesta a Emergencia"
        }
        sector_label = sector_map.get(sector_raw, sector_raw)
        
        estado_code = str(row.get("Estado") or row.get("group_datos_loc/Estado") or "").strip()
        estado_label = MAPA_ESTADOS.get(estado_code, estado_code)
        
        muni_code = str(row.get("Municipio") or row.get("group_datos_loc/Municipio") or "").strip()
        muni_label = MAPA_MUNICIPIOS.get(muni_code, muni_code)
        
        fecha_act = row.get("Fecha_de_la_Actividad") or row.get("group_datos_act/Fecha_de_la_Actividad") or row.get("_submission_time")
        
        ind_val = row.get("Indicadores_resultados") or row.get("group_datos_act/Indicadores_resultados") or ""
        indicadores_raw = str(ind_val).split()
        indicadores_labels = [MAPA_INDICADORES.get(ind, ind) for ind in indicadores_raw if ind]
        
        base_info = {
            "_id": row.get("_id"),
            "Fecha": fecha_act,
            "Estado": estado_label,
            "Municipio": muni_label,
            "Comunidad": row.get("Comunidad") or row.get("group_datos_loc/Comunidad"),
            "ONG": row.get("ong") or row.get("group_datos_act/ong"),
            "Sector": sector_label,
            "Actividad": row.get("Actividad") or row.get("group_datos_act/Actividad"),
            "Indicadores_Codigos": indicadores_raw,
            "Indicadores_Texto": " | ".join(indicadores_labels) if indicadores_labels else "Sin indicador"
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
                
                if edad < 18:
                    b_info["Grupo_Demografico"] = "Niña" if sexo_raw in ["femenino", "f", "mujer"] else "Niño"
                else:
                    b_info["Grupo_Demografico"] = "Mujer" if sexo_raw in ["femenino", "f", "mujer"] else "Hombre"
                
                registros_expandidos.append(b_info)
        else:
            registros_expandidos.append(base_info)
            
    df = pd.DataFrame(registros_expandidos)
    
    if not df.empty and "Fecha" in df.columns:
        df["Fecha_DT"] = pd.to_datetime(df["Fecha"], errors='coerce')
        df["Mes_Reporte"] = df["Fecha_DT"].apply(
            lambda x: f"{x.year} - {MESES_ES.get(x.month, '')}" if pd.notnull(x) else "Sin Fecha"
        )
    else:
        df["Mes_Reporte"] = "Sin Fecha"
        
    return df

# Cargar credenciales
try:
    KOBO_TOKEN = st.secrets["KOBO_TOKEN"]
    ASSET_ID = st.secrets["ASSET_ID"]
    df_raw = cargar_datos_kobo(ASSET_ID, KOBO_TOKEN)
except Exception:
    st.info("Por favor, configura tu KOBO_TOKEN y ASSET_ID en Secrets.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. FILTROS LATERALES
# -----------------------------------------------------------------------------
st.sidebar.header("Sincronización en Tiempo Real")

if st.sidebar.button("Actualizar Datos Ahora"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Filtros de Consulta")

if df_raw.empty:
    st.warning("No se encontraron registros en el formulario de KoboToolbox.")
    st.stop()

# Filtro Mes del Reporte
meses_ordenados = sorted([m for m in df_raw["Mes_Reporte"].unique() if m != "Sin Fecha"])
if "Sin Fecha" in df_raw["Mes_Reporte"].values:
    meses_ordenados.append("Sin Fecha")
meses_disp = ["Todos"] + meses_ordenados
mes_sel = st.sidebar.selectbox("Mes del Reporte:", meses_disp)

socios_disp = ["Todos"] + sorted([x for x in df_raw["ONG"].dropna().unique() if x])
socio_sel = st.sidebar.selectbox("Socio / ONG:", socios_disp)

estados_disp = ["Todos"] + sorted([x for x in df_raw["Estado"].dropna().unique() if x])
estado_sel = st.sidebar.selectbox("Estado:", estados_disp)

df_temp = df_raw if estado_sel == "Todos" else df_raw[df_raw["Estado"] == estado_sel]
munis_disp = ["Todos"] + sorted([x for x in df_temp["Municipio"].dropna().unique() if x])
muni_sel = st.sidebar.selectbox("Municipio:", munis_disp)

sectores_disp = ["Todos"] + sorted([x for x in df_raw["Sector"].dropna().unique() if x])
sector_sel = st.sidebar.selectbox("Sector de Implementación:", sectores_disp)

# Aplicar Filtros
df_filtered = df_raw.copy()
if mes_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Mes_Reporte"] == mes_sel]
if socio_sel != "Todos":
    df_filtered = df_filtered[df_filtered["ONG"] == socio_sel]
if estado_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Estado"] == estado_sel]
if muni_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Municipio"] == muni_sel]
if sector_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Sector"] == sector_sel]

# -----------------------------------------------------------------------------
# 4. MÉTRICAS CLAVE
# -----------------------------------------------------------------------------
total_impactados = len(df_filtered)

if "Documento" in df_filtered.columns and "CodigoID" in df_filtered.columns:
    df_filtered["ID_Unico"] = df_filtered["Documento"].replace("", None).fillna(df_filtered["CodigoID"])
    total_unicos = df_filtered["ID_Unico"].nunique()
else:
    total_unicos = total_impactados

pct_meta = (total_unicos / META_PARTICIPANTES_UNICOS) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Impactados (Admite duplicidad)", f"{total_impactados:,}")
col2.metric("Total Participantes Únicos", f"{total_unicos:,}")
col3.metric("% Alcance de la Meta (46.122 pers.)", f"{pct_meta:.2f}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. GRUPOS DE PARTICIPANTES
# -----------------------------------------------------------------------------
st.subheader("Grupos de Participantes")

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
# 6. TABLA DESGLOSE DE INDICADORES
# -----------------------------------------------------------------------------
st.subheader("Desglose de Indicadores del Proyecto")

if total_impactados > 0:
    records_ind = []
    for idx, row in df_filtered.iterrows():
        codigos = row.get("Indicadores_Codigos", [])
        sector_actual = row.get("Sector", "Sin Sector")
        
        if isinstance(codigos, list) and len(codigos) > 0:
            for cod in codigos:
                records_ind.append({
                    "Sector": sector_actual,
                    "Indicador": MAPA_INDICADORES.get(cod, cod),
                    "ID_Unico": row.get("ID_Unico")
                })
        else:
            records_ind.append({
                "Sector": sector_actual,
                "Indicador": f"Sin indicador ({sector_actual})",
                "ID_Unico": row.get("ID_Unico")
            })
            
    df_ind_flat = pd.DataFrame(records_ind)
    
    summary_ind = df_ind_flat.groupby(["Sector", "Indicador"]).agg(
        Valor_Absoluto=("ID_Unico", "count"),
        Participantes_Unicos=("ID_Unico", "nunique")
    ).reset_index()
    
    summary_ind["Porcentaje (%)"] = (summary_ind["Valor_Absoluto"] / total_impactados) * 100
    summary_ind["Porcentaje (%)"] = summary_ind["Porcentaje (%)"].map("{:.1f}%".format)
    
    summary_ind = summary_ind.sort_values(by=["Sector", "Valor_Absoluto"], ascending=[True, False])
    
    st.dataframe(
        summary_ind[["Sector", "Indicador", "Valor_Absoluto", "Porcentaje (%)", "Participantes_Unicos"]].rename(columns={
            "Sector": "Sector",
            "Indicador": "Indicador del Proyecto",
            "Valor_Absoluto": "Valor Absoluto (Impactados)",
            "Porcentaje (%)": "% del Total",
            "Participantes_Unicos": "Participantes Únicos"
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. GRÁFICOS INTERACTIVOS (CON FUENTES ESTILIZADAS)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

font_layout = dict(family="Quicksand", size=13)

with g1:
    st.subheader("Desglose por Sexo y Rango Etario")
    if total_impactados > 0 and "Grupo_Demografico" in df_filtered.columns:
        df_demo = df_filtered.groupby("Grupo_Demografico").size().reset_index(name="Cantidad")
        df_demo["Porcentaje"] = (df_demo["Cantidad"] / total_impactados) * 100
        df_demo["Etiqueta"] = df_demo.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.1f}%)", axis=1)
        
        fig_bar = px.bar(
            df_demo, 
            x="Grupo_Demografico", 
            y="Cantidad", 
            color="Grupo_Demografico",
            text="Etiqueta",
            title="Participantes por Rango Etario y Sexo",
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            showlegend=False,
            font=font_layout,
            title_font=dict(family="Now, Montserrat", size=16)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with g2:
    st.subheader("Participantes Únicos por Sector")
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
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_pie.update_traces(textinfo="label+value+percent")
        fig_pie.update_layout(
            showlegend=False,
            font=font_layout,
            title_font=dict(family="Now, Montserrat", size=16)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. UBICACIÓN GEOGRÁFICA Y MAPA
# -----------------------------------------------------------------------------
st.subheader("Ubicación Geográfica por Municipio")

m1, m2 = st.columns([1, 1])

with m1:
    st.markdown("### Participantes Impactados por Municipio")
    if total_impactados > 0 and "Municipio" in df_filtered.columns:
        df_muni = df_filtered.groupby(["Estado", "Municipio"]).size().reset_index(name="Impactados")
        df_muni["Porcentaje"] = (df_muni["Impactados"] / total_impactados) * 100
        df_muni["Etiqueta"] = df_muni.apply(lambda r: f"{r['Impactados']} ({r['Porcentaje']:.1f}%)", axis=1)
        df_muni = df_muni.sort_values(by="Impactados", ascending=True)
        
        fig_muni = px.bar(
            df_muni,
            y="Municipio",
            x="Impactados",
            color="Estado",
            orientation="h",
            text="Etiqueta",
            height=400,
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_muni.update_traces(textposition="outside")
        fig_muni.update_layout(
            showlegend=False,
            font=font_layout
        )
        st.plotly_chart(fig_muni, use_container_width=True)

with m2:
    st.markdown("### Cobertura de la Intervención")
    
    mapa = folium.Map(location=[7.8, -65.5], zoom_start=6, tiles="CartoDB positron")
    
    if total_impactados > 0:
        mapa_df = df_filtered.groupby(["Estado", "Municipio", "Sector"]).size().reset_index(name="Cantidad")
        muni_totales = df_filtered.groupby(["Estado", "Municipio"]).size().reset_index(name="Total_Impactados")
        
        for idx, m_row in muni_totales.iterrows():
            est = m_row["Estado"]
            mun = m_row["Municipio"]
            tot = m_row["Total_Impactados"]
            
            coords = COORDENADAS_MUNICIPIOS.get(mun, [7.8, -65.5])
            
            sectores_muni = mapa_df[(mapa_df["Estado"] == est) & (mapa_df["Municipio"] == mun)]
            sec_html = "".join([f"<li><b>{r['Sector']}:</b> {r['Cantidad']} personas</li>" for _, r in sectores_muni.iterrows()])
            
            popup_content = f"""
            <div style='font-family: Quicksand, sans-serif; font-weight: 700; font-size: 12px; width: 200px;'>
                <h4 style='font-family: Now, Montserrat, sans-serif; margin-bottom: 5px; color: {COLOR_AGUAMARINA};'>{mun}</h4>
                <b>Estado:</b> {est}<br>
                <b>Total Impactados:</b> {tot}<br><br>
                <b>Desglose por Sector:</b>
                <ul style='margin-top: 5px; padding-left: 15px;'>
                    {sec_html}
                </ul>
            </div>
            """
            
            folium.CircleMarker(
                location=coords,
                radius=min(tot * 3, 20) + 6,
                popup=folium.Popup(popup_content, max_width=250),
                color=COLOR_AGUAMARINA,
                fill=True,
                fill_color=COLOR_AGUAMARINA,
                fill_opacity=0.7
            ).add_to(mapa)
            
    st_folium(mapa, width=500, height=380)
