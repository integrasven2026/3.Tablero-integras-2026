import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_folium import st_folium
import folium
import os
import io

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

# Inyección de Fuentes: Quicksand y Now (o Montserrat como fallback)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Quicksand:wght@600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, span, label, input, button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 700 !important;
    }

    h1, h2, h3, h4, h5, h6, .stSubheader {
        font-family: 'Now', 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
    }

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
    st.markdown(
        f"<h1 class='titulo-principal'>Tablero de Monitoreo - Consorcio Integras</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("**Socio Prime / Líder:** COOPI | **Socios:** HIAS, FLM, PLAFAM, PALUZ")

with col_header_logo:
    posibles_nombres = [
        "integras.jpg", 
        "Integras.jpg", 
        "Integras_logo.jpg", 
        "integras_logo.jpg", 
        "Integras_logo.png", 
        "integras_logo.png"
    ]
    logo_path = None
    
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            logo_path = nombre
            break

    URL_LOGO_GITHUB = "https://raw.githubusercontent.com/integrasven2026/3.Tablero-integras-2026/main/integras.jpg"

    if logo_path:
        try:
            st.image(logo_path, width="stretch")
        except TypeError:
            st.image(logo_path, width="stretch")
    else:
        try:
            st.image(URL_LOGO_GITHUB, width="stretch")
        except Exception:
            st.warning("⚠️ No se pudo cargar el logo 'integras.jpg'.")

st.markdown("---")

# META TOTAL DEL PROYECTO
META_PARTICIPANTES_UNICOS = 46122

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

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

# DICCIONARIO DE METAS DEL PROYECTO
METAS_INDICADORES = {
    "R1I2": {"meta": 883.8, "tipo": "numero", "etiqueta": "90% de 982 (884 pers.)"},
    "R1I3": {"meta": 910, "tipo": "numero", "etiqueta": "910"},
    "R1I4": {"meta": 4635, "tipo": "numero", "etiqueta": "75% de 6,180 (4,635 pers.)"},
    "R1I5": {"meta": 916.3, "tipo": "numero", "etiqueta": "70% de 1,309 (916 pers.)"},
    "R1I6": {"meta": 0.90, "tipo": "porcentaje", "etiqueta": "90%"},
    "R2I1": {"meta": 8622, "tipo": "numero", "etiqueta": "8,622"},
    "R2I2": {"meta": 0.80, "tipo": "porcentaje", "etiqueta": "80%"},
    "R2I3": {"meta": 20, "tipo": "numero", "etiqueta": "20"},
    "R2I4": {"meta": 0.30, "tipo": "porcentaje", "etiqueta": "30%"},
    "R2I5": {"meta": 5, "tipo": "numero", "etiqueta": "5"},
    "R3I1": {"meta": 177, "tipo": "numero", "etiqueta": "177"},
    "R3I2": {"meta": 34, "tipo": "numero", "etiqueta": "34"},
    "R4I1": {"meta": 3200, "tipo": "numero", "etiqueta": "3,200"},
    "R4I2": {"meta": 1200, "tipo": "numero", "etiqueta": "1,200"},
    "R4I3": {"meta": 2800, "tipo": "numero", "etiqueta": "2,800"},
    "R4I4": {"meta": 0.80, "tipo": "porcentaje", "etiqueta": "80%"},
    "R5I1": {"meta": 800, "tipo": "numero", "etiqueta": "800"},
    "R5I2": {"meta": 5100, "tipo": "numero", "etiqueta": "5,100"},
}

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE EXTRACCIÓN ROBUSTA
# -----------------------------------------------------------------------------
def extraer_valor_booleano(diccionario_beneficiario, lista_posibles_claves):
    """Busca en múltiples nombres de claves de Kobo y determina si el valor es AFIRMATIVO."""
    val_afirmativos = ["sí", "si", "yes", "1", "s", "true"]
    
    for clave in lista_posibles_claves:
        for k_item, v_item in diccionario_beneficiario.items():
            if clave.lower() in str(k_item).lower():
                val_str = str(v_item).lower().strip()
                if val_str in val_afirmativos or v_item == 1 or v_item is True:
                    return 1
    return 0

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
    
    claves_discapacidad = ["persona_con_discapacidad", "discapacidad", "count_discapacidad"]
    claves_indigena = ["poblacion_indigena", "indigena", "count_indigena"]
    claves_embarazada = ["embarazada", "lactante", "embarazada_o_lactante", "count_embarazada"]
    claves_lgbtiq = ["poblacion_lgbtiq", "lgbtiq", "count_lgbtiq"]

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
        
        ong_val = str(row.get("ong") or row.get("group_datos_act/ong") or "COOPI").upper().strip()

        base_info = {
            "_id": row.get("_id"),
            "Fecha": fecha_act,
            "Estado": estado_label,
            "Municipio": muni_label,
            "Comunidad": row.get("Comunidad") or row.get("group_datos_loc/Comunidad"),
            "ONG": ong_val,
            "Sector": sector_label,
            "Actividad": str(row.get("Actividad") or row.get("group_datos_act/Actividad") or "General").strip(),
            "Indicadores_Codigos": indicadores_raw,
            "Indicadores_Texto": " | ".join(indicadores_labels) if indicadores_labels else "Sin indicador"
        }
        
        beneficiarios = row.get("group_beneficiario", [])
        if isinstance(beneficiarios, list) and len(beneficiarios) > 0:
            for idx_b, b in enumerate(beneficiarios):
                b_info = base_info.copy()
                cid = str(b.get("group_beneficiario/CodigoID", "")).strip()
                doc = str(b.get("group_beneficiario/N_de_Documento_de_Identidad", "")).strip()
                
                b_info["Nombre"] = str(b.get("group_beneficiario/Nombre", "")).strip()
                b_info["Apellido"] = str(b.get("group_beneficiario/Apellido", "")).strip()
                b_info["Documento"] = doc
                b_info["CodigoID"] = cid
                
                if cid and cid.lower() not in ["none", "null", "", "0", "n/a"]:
                    b_info["ID_Unico"] = cid
                elif doc and doc.lower() not in ["none", "null", "", "0", "n/a"]:
                    b_info["ID_Unico"] = f"DOC_{doc}"
                else:
                    b_info["ID_Unico"] = f"REG_{row.get('_id')}_{idx_b}"

                sexo_raw = str(b.get("group_beneficiario/Sexo", "")).lower().strip()
                
                if sexo_raw in ["femenino", "f", "mujer"]:
                    sexo_norm = "Mujer"
                elif sexo_raw in ["masculino", "m", "hombre"]:
                    sexo_norm = "Hombre"
                else:
                    sexo_norm = "Otro"
                    
                b_info["Sexo"] = sexo_norm
                
                try:
                    edad = float(b.get("group_beneficiario/edad_", 0))
                except (ValueError, TypeError):
                    edad = 0
                b_info["Edad"] = edad
                
                if edad < 18:
                    b_info["Grupo_Demografico"] = "Niña" if sexo_norm == "Mujer" else "Niño"
                else:
                    b_info["Grupo_Demografico"] = "Mujer" if sexo_norm == "Mujer" else "Hombre"

                b_info["Es_Discapacidad"] = extraer_valor_booleano(b, claves_discapacidad)
                b_info["Es_Indigena"] = extraer_valor_booleano(b, claves_indigena)
                b_info["Es_Embarazada_Lactante"] = extraer_valor_booleano(b, claves_embarazada)
                
                lgbtiq_kobo = extraer_valor_booleano(b, claves_lgbtiq)
                b_info["Es_LGBTIQ"] = 1 if (lgbtiq_kobo == 1 or sexo_norm == "Otro") else 0

                registros_expandidos.append(b_info)
        else:
            base_info["CodigoID"] = f"ROW_{row.get('_id')}"
            base_info["ID_Unico"] = f"ROW_{row.get('_id')}"
            base_info["Sexo"] = "Otro"
            base_info["Es_Discapacidad"] = 0
            base_info["Es_Indigena"] = 0
            base_info["Es_Embarazada_Lactante"] = 0
            base_info["Es_LGBTIQ"] = 1
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
# 3. FILTROS LATERALES CON BOTÓN DE LIMPIEZA Y FILTRO POR SEXO
# -----------------------------------------------------------------------------
st.sidebar.header("Sincronización en Tiempo Real")

col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.button("🔄 Actualizar", width="stretch"):
        st.cache_data.clear()
        st.rerun()

if "f_mes" not in st.session_state: st.session_state.f_mes = "Todos"
if "f_socio" not in st.session_state: st.session_state.f_socio = "Todos"
if "f_estado" not in st.session_state: st.session_state.f_estado = "Todos"
if "f_muni" not in st.session_state: st.session_state.f_muni = "Todos"
if "f_sector" not in st.session_state: st.session_state.f_sector = "Todos"
if "f_sexo" not in st.session_state: st.session_state.f_sexo = "Todos"

def borrar_filtros():
    st.session_state.f_mes = "Todos"
    st.session_state.f_socio = "Todos"
    st.session_state.f_estado = "Todos"
    st.session_state.f_muni = "Todos"
    st.session_state.f_sector = "Todos"
    st.session_state.f_sexo = "Todos"

with col_btn2:
    st.button("🧹 Limpiar Filtros", on_click=borrar_filtros, width="stretch")

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
mes_sel = st.sidebar.selectbox("Mes del Reporte:", meses_disp, key="f_mes")

socios_disp = ["Todos"] + sorted([x for x in df_raw["ONG"].dropna().unique() if x])
socio_sel = st.sidebar.selectbox("Socio / ONG:", socios_disp, key="f_socio")

estados_disp = ["Todos"] + sorted([x for x in df_raw["Estado"].dropna().unique() if x])
estado_sel = st.sidebar.selectbox("Estado:", estados_disp, key="f_estado")

df_temp = df_raw if estado_sel == "Todos" else df_raw[df_raw["Estado"] == estado_sel]
munis_disp = ["Todos"] + sorted([x for x in df_temp["Municipio"].dropna().unique() if x])
muni_sel = st.sidebar.selectbox("Municipio:", munis_disp, key="f_muni")

sectores_disp = ["Todos"] + sorted([x for x in df_raw["Sector"].dropna().unique() if x])
sector_sel = st.sidebar.selectbox("Sector de Implementación:", sectores_disp, key="f_sector")

# FILTRO DE SEXO
sexo_disp = ["Todos", "Hombre", "Mujer", "Otro"]
sexo_sel = st.sidebar.selectbox("Sexo del Participante:", sexo_disp, key="f_sexo")

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
if sexo_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Sexo"] == sexo_sel]

# -----------------------------------------------------------------------------
# 4. MÉTRICAS CLAVE
# -----------------------------------------------------------------------------
total_impactados = len(df_filtered)
df_unicos = df_filtered.drop_duplicates(subset=["ID_Unico"])
total_unicos = len(df_unicos)

pct_meta = (total_unicos / META_PARTICIPANTES_UNICOS) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Impactados (Admite duplicidad)", f"{total_impactados:,}")
col2.metric("Total Participantes Únicos", f"{total_unicos:,}")
col3.metric("% Alcance de la Meta (46.122 pers.)", f"{pct_meta:.2f}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. GRUPOS DEMOGRÁFICOS Y NECESIDADES ESPECÍFICAS
# -----------------------------------------------------------------------------
st.subheader("Grupos Demográficos y Necesidades Específicas")

if total_unicos > 0 and "Grupo_Demografico" in df_unicos.columns:
    counts_u = df_unicos["Grupo_Demografico"].value_counts()
    
    p_mujeres = (counts_u.get("Mujer", 0) / total_unicos) * 100
    p_hombres = (counts_u.get("Hombre", 0) / total_unicos) * 100
    p_ninas = (counts_u.get("Niña", 0) / total_unicos) * 100
    p_ninos = (counts_u.get("Niño", 0) / total_unicos) * 100

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("% Mujeres (≥18 años)", f"{p_mujeres:.1f}%")
    d2.metric("% Hombres (≥18 años)", f"{p_hombres:.1f}%")
    d3.metric("% Niñas (<18 años)", f"{p_ninas:.1f}%")
    d4.metric("% Niños (<18 años)", f"{p_ninos:.1f}%")

st.markdown("#### Personas con Necesidades Específicas")

cnt_disc = int(df_unicos["Es_Discapacidad"].sum()) if "Es_Discapacidad" in df_unicos.columns else 0
cnt_indig = int(df_unicos["Es_Indigena"].sum()) if "Es_Indigena" in df_unicos.columns else 0
cnt_emb = int(df_unicos["Es_Embarazada_Lactante"].sum()) if "Es_Embarazada_Lactante" in df_unicos.columns else 0
cnt_lgbtiq = int(df_unicos["Es_LGBTIQ"].sum()) if "Es_LGBTIQ" in df_unicos.columns else 0

p_disc = (cnt_disc / total_unicos * 100) if total_unicos > 0 else 0
p_indig = (cnt_indig / total_unicos * 100) if total_unicos > 0 else 0
p_emb = (cnt_emb / total_unicos * 100) if total_unicos > 0 else 0
p_lgbtiq = (cnt_lgbtiq / total_unicos * 100) if total_unicos > 0 else 0

ne1, ne2, ne3, ne4 = st.columns(4)
ne1.metric("Personas con Discapacidad", f"{cnt_disc:,}", f"{p_disc:.1f}%")
ne2.metric("Comunidad Indígena", f"{cnt_indig:,}", f"{p_indig:.1f}%")
ne3.metric("Embarazada / Lactante", f"{cnt_emb:,}", f"{p_emb:.1f}%")
ne4.metric("Población LGBTIQ+", f"{cnt_lgbtiq:,}", f"{p_lgbtiq:.1f}%")

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
                    "Codigo_Ind": cod,
                    "Indicador": MAPA_INDICADORES.get(cod, cod),
                    "ID_Unico": row.get("ID_Unico")
                })
        else:
            records_ind.append({
                "Sector": sector_actual,
                "Codigo_Ind": "SI",
                "Indicador": f"Sin indicador ({sector_actual})",
                "ID_Unico": row.get("ID_Unico")
            })
            
    df_ind_flat = pd.DataFrame(records_ind)
    
    summary_ind = df_ind_flat.groupby(["Sector", "Codigo_Ind", "Indicador"]).agg(
        Valor_Absoluto=("ID_Unico", "count"),
        Participantes_Unicos=("ID_Unico", "nunique")
    ).reset_index()
    
    summary_ind["Porcentaje_Total"] = (summary_ind["Participantes_Unicos"] / total_unicos) * 100
    
    def obtener_meta_info(cod):
        meta_data = METAS_INDICADORES.get(cod)
        if meta_data:
            return meta_data["etiqueta"], meta_data["meta"], meta_data["tipo"]
        return "N/A", None, "ninguno"

    meta_etiquetas = []
    alcance_porcentajes = []

    for _, row_ind in summary_ind.iterrows():
        cod = row_ind["Codigo_Ind"]
        etiqueta_meta, valor_meta, tipo_meta = obtener_meta_info(cod)
        meta_etiquetas.append(etiqueta_meta)
        
        if valor_meta and valor_meta > 0:
            if tipo_meta == "numero":
                alcance = (row_ind["Participantes_Unicos"] / valor_meta) * 100
                alcance_porcentajes.append(f"{alcance:.1f}%")
            elif tipo_meta == "porcentaje":
                alcance_porcentajes.append(f"{row_ind['Porcentaje_Total']:.1f}% (de {etiqueta_meta})")
        else:
            alcance_porcentajes.append("N/A")

    summary_ind["Meta del Proyecto"] = meta_etiquetas
    summary_ind["% Alcance del Indicador"] = alcance_porcentajes
    summary_ind["% del Total"] = summary_ind["Porcentaje_Total"].map("{:.1f}%".format)
    
    summary_ind = summary_ind.sort_values(by=["Sector", "Valor_Absoluto"], ascending=[True, False])
    
    cols_ordenadas = [
        "Sector", 
        "Indicador", 
        "Valor_Absoluto", 
        "% del Total", 
        "Meta del Proyecto", 
        "% Alcance del Indicador"
    ]

    df_mostrar = summary_ind[cols_ordenadas].rename(columns={
        "Sector": "Sector",
        "Indicador": "Indicador del Proyecto",
        "Valor_Absoluto": "Valor Absoluto (Impactados)",
        "% del Total": "% del Total",
        "Meta del Proyecto": "Meta del Proyecto",
        "% Alcance del Indicador": "% Alcance del Indicador"
    })
    
    st.dataframe(
        df_mostrar,
        width="stretch",
        hide_index=True
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_mostrar.to_excel(writer, index=False, sheet_name='Indicadores')
    buffer.seek(0)

    st.download_button(
        label="📥 Descargar Desglose de Indicadores en Excel",
        data=buffer,
        file_name="Desglose_Indicadores_Consorcio_Integras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. GRÁFICOS INTERACTIVOS (POR PARTICIPANTES ÚNICOS)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

font_layout = dict(family="Quicksand", size=13)

with g1:
    st.subheader("Desglose por Sexo y Rango Etario (Participantes Únicos)")
    if total_unicos > 0 and "Grupo_Demografico" in df_unicos.columns:
        df_demo = df_unicos.groupby("Grupo_Demografico").size().reset_index(name="Cantidad")
        df_demo["Porcentaje"] = (df_demo["Cantidad"] / total_unicos) * 100
        df_demo["Etiqueta"] = df_demo.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.1f}%)", axis=1)
        
        fig_bar = px.bar(
            df_demo, 
            x="Grupo_Demografico", 
            y="Cantidad", 
            color="Grupo_Demografico",
            text="Etiqueta",
            title="Participantes Únicos por Rango Etario y Sexo",
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            showlegend=False,
            font=font_layout,
            title_font=dict(family="Now, Montserrat", size=16)
        )
        st.plotly_chart(fig_bar, width="stretch")

with g2:
    st.subheader("Participantes Únicos por Sector")
    if total_unicos > 0 and "Sector" in df_filtered.columns:
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
        st.plotly_chart(fig_pie, width="stretch")

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. UBICACIÓN GEOGRÁFICA Y MAPA
# -----------------------------------------------------------------------------
st.subheader("Ubicación Geográfica por Municipio")

m1, m2 = st.columns([1, 1])

with m1:
    st.markdown("### Participantes Únicos por Municipio")
    if total_unicos > 0 and "Municipio" in df_unicos.columns:
        df_muni = df_unicos.groupby(["Estado", "Municipio"]).size().reset_index(name="Participantes_Unicos")
        df_muni["Porcentaje"] = (df_muni["Participantes_Unicos"] / total_unicos) * 100
        df_muni["Etiqueta"] = df_muni.apply(lambda r: f"{r['Participantes_Unicos']} ({r['Porcentaje']:.1f}%)", axis=1)
        df_muni = df_muni.sort_values(by="Participantes_Unicos", ascending=True)
        
        fig_muni = px.bar(
            df_muni,
            y="Municipio",
            x="Participantes_Unicos",
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
        st.plotly_chart(fig_muni, width="stretch")

with m2:
    st.markdown("### Cobertura de la Intervención")
    
    mapa = folium.Map(location=[7.8, -65.5], zoom_start=6, tiles="CartoDB positron")
    
    if total_unicos > 0:
        mapa_df = df_filtered.drop_duplicates(subset=["ID_Unico", "Sector"]).groupby(["Estado", "Municipio", "Sector"]).size().reset_index(name="Cantidad")
        muni_totales = df_unicos.groupby(["Estado", "Municipio"]).size().reset_index(name="Total_Unicos")
        
        for idx, m_row in muni_totales.iterrows():
            est = m_row["Estado"]
            mun = m_row["Municipio"]
            tot = m_row["Total_Unicos"]
            
            coords = COORDENADAS_MUNICIPIOS.get(mun, [7.8, -65.5])
            
            sectores_muni = mapa_df[(mapa_df["Estado"] == est) & (mapa_df["Municipio"] == mun)]
            sec_html = "".join([f"<li><b>{r['Sector']}:</b> {r['Cantidad']} personas únicas</li>" for _, r in sectores_muni.iterrows()])
            
            popup_content = f"""
            <div style='font-family: Quicksand, sans-serif; font-weight: 700; font-size: 12px; width: 200px;'>
                <h4 style='font-family: Now, Montserrat, sans-serif; margin-bottom: 5px; color: {COLOR_AGUAMARINA};'>{mun}</h4>
                <b>Estado:</b> {est}<br>
                <b>Participantes Únicos:</b> {tot}<br><br>
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

st.markdown("---")

# -----------------------------------------------------------------------------
# 9. SEGUIMIENTO A LAS ACTIVIDADES DEL CONSORCIO (REPORTE PARA SOCIOS)
# -----------------------------------------------------------------------------
st.subheader("Seguimiento de Actividades por Socio y Sector")

# Definición de metas por actividad y socio (Marco Lógico Consorcio INTEGRAS)
METAS_ACTIVIDADES = {
    "General Protection Case Management": {
        "Sector": "Protección",
        "Meta_Proyecto": 2108,
        "Metas_Socios": {"COOPI": 1000, "FLM": 608, "HIAS": 500},
    },
    "Child-Friendly Spaces (CFS)": {
        "Sector": "Protección",
        "Meta_Proyecto": 3526,
        "Metas_Socios": {"HIAS": 1500, "FLM": 1100, "COOPI": 926},
    },
    "Legal Aid & Documentation": {
        "Sector": "Protección",
        "Meta_Proyecto": 1047,
        "Metas_Socios": {"COOPI": 400, "HIAS": 350, "FLM": 297},
    },
    "Individual Protection Assistance (IPA)": {
        "Sector": "Protección",
        "Meta_Proyecto": 3194,
        "Metas_Socios": {"COOPI": 1200, "HIAS": 1000, "FLM": 994},
    },
    "Legal Aid on HLP": {
        "Sector": "Protección",
        "Meta_Proyecto": 62,
        "Metas_Socios": {"COOPI": 25, "HIAS": 20, "FLM": 17},
    },
    "IPC Equipment & Bio-safety": {
        "Sector": "WASH",
        "Meta_Proyecto": 2752,
        "Metas_Socios": {"COOPI": 2000, "PALUZ": 752},
    },
    "Essential Health & Medicines": {
        "Sector": "Salud",
        "Meta_Proyecto": 752,
        "Metas_Socios": {"PALUZ": 752},
    },
    "Health Staff Capacity Building": {
        "Sector": "Salud",
        "Meta_Proyecto": 90,
        "Metas_Socios": {"PALUZ": 90},
    },
    "Sexual & Reproductive Health (SRH)": {
        "Sector": "Salud",
        "Meta_Proyecto": 1144,
        "Metas_Socios": {"PLAFAM": 750, "PALUZ": 394},
    },
    "Clinical Waste Management": {
        "Sector": "WASH",
        "Meta_Proyecto": 30,
        "Metas_Socios": {"COOPI": 30},
    },
}

socios_disponibles = sorted(
    list(
        set(
            df_filtered["ONG"].unique().tolist()
            if "ONG" in df_filtered.columns
            else ["COOPI"]
        ).union({"COOPI", "HIAS", "FLM", "PALUZ", "PLAFAM"})
    )
)

col_s1, col_s2 = st.columns([1, 3])
with col_s1:
    socio_reporte = st.selectbox(
        "Filtrar Reporte por Socio:",
        options=["TODOS"] + socios_disponibles,
        index=0
    )

filas_reporte = []

for act_nombre, datos in METAS_ACTIVIDADES.items():
    sec = datos["Sector"]
    meta_proy = datos["Meta_Proyecto"]
    metas_socios = datos["Metas_Socios"]

    if socio_reporte != "TODOS":
        if socio_reporte not in metas_socios:
            continue
        meta_socio = metas_socios[socio_reporte]
        
        df_act = df_filtered[
            (df_filtered["ONG"] == socio_reporte) &
            (
                df_filtered["Actividad"].str.contains(act_nombre, regex=False, case=False, na=False) |
                df_filtered["Sector"].str.contains(sec, regex=False, case=False, na=False)
            )
        ]
        alcanzado_abs = len(df_act)
        alcanzado_unicos = df_act["ID_Unico"].nunique() if "ID_Unico" in df_act.columns else alcanzado_abs
        pct = (alcanzado_unicos / meta_socio * 100) if meta_socio > 0 else 0.0

        filas_reporte.append({
            "Sector": sec,
            "Actividad": act_nombre,
            "Socio": socio_reporte,
            "Meta Proyecto": meta_proy,
            "Meta Socio": meta_socio,
            "Alcanzado (Impactados)": alcanzado_abs,
            "Alcanzado (Únicos)": alcanzado_unicos,
            "% Avance Socio": round(pct, 1)
        })
    else:
        for s_nombre, meta_socio in metas_socios.items():
            df_act = df_filtered[
                (df_filtered["ONG"] == s_nombre) &
                (
                    df_filtered["Actividad"].str.contains(act_nombre, regex=False, case=False, na=False) |
                    df_filtered["Sector"].str.contains(sec, regex=False, case=False, na=False)
                )
            ]
            alcanzado_abs = len(df_act)
            alcanzado_unicos = df_act["ID_Unico"].nunique() if "ID_Unico" in df_act.columns else alcanzado_abs
            pct = (alcanzado_unicos / meta_socio * 100) if meta_socio > 0 else 0.0

            filas_reporte.append({
                "Sector": sec,
                "Actividad": act_nombre,
                "Socio": s_nombre,
                "Meta Proyecto": meta_proy,
                "Meta Socio": meta_socio,
                "Alcanzado (Impactados)": alcanzado_abs,
                "Alcanzado (Únicos)": alcanzado_unicos,
                "% Avance Socio": round(pct, 1)
            })

df_reporte_act = pd.DataFrame(filas_reporte)

if not df_reporte_act.empty:
    st.dataframe(
        df_reporte_act.style.format({
            "Meta Proyecto": "{:,}",
            "Meta Socio": "{:,}",
            "Alcanzado (Impactados)": "{:,}",
            "Alcanzado (Únicos)": "{:,}",
            "% Avance Socio": "{:.1f}%"
        }),
        width="stretch",
        hide_index=True
    )
else:
    st.info("No se registraron actividades correspondientes a los filtros seleccionados.")
