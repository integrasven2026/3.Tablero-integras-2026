import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
import folium
import os
import io
import re

# -----------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL CONSORCIO INTEGRAS
# -----------------------------------------------------------------------------
COLOR_AGUAMARINA = '#17C3B2'  # Verde / Azul Agua Marina oficial
COLOR_ROSADO_AAP = '#D89FE3'   # Morado / Rosado Orquídea para Reporte AAP
COLOR_VERDE_ABIERTO = '#28A745' # Verde para Casos Abiertos / En Proceso

PALETA_INTEGRAS = [
    COLOR_AGUAMARINA,  # Turquesa / Agua Marina
    COLOR_ROSADO_AAP,  # Morado / Orquídea / Rosado
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

    .titulo-aap {
        font-family: 'Now', 'Montserrat', sans-serif !important;
        color: #D89FE3 !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
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

# METAS DEL PROYECTO
META_PARTICIPANTES_UNICOS = 46122
META_BENEFICIARIOS_PROYECTO = 32000
META_PQRS_AAP = META_BENEFICIARIOS_PROYECTO * 0.10  # 10% = 3,200 PQRS

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

font_layout = dict(family="Quicksand", size=13)

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE EXTRACCIÓN ROBUSTA
# -----------------------------------------------------------------------------
def extraer_valor_booleano(diccionario_beneficiario, lista_posibles_claves):
    val_afirmativos = ["sí", "si", "yes", "1", "s", "true"]
    for clave in lista_posibles_claves:
        for k_item, v_item in diccionario_beneficiario.items():
            if clave.lower() in str(k_item).lower():
                val_str = str(v_item).lower().strip()
                if val_str in val_afirmativos or v_item == 1 or v_item is True:
                    return 1
    return 0

def extraer_campo_dinamico(row_dict, palabras_clave, valor_defecto="Sin especificar"):
    for key, value in row_dict.items():
        if value is None or str(value).strip() == "":
            continue
        key_lower = str(key).lower()
        if any(pc.lower() in key_lower for pc in palabras_clave):
            return str(value).strip()
    return valor_defecto

def limpiar_texto_categoria(texto):
    if not texto:
        return "Sin Especificar"
    texto_limpio = re.sub(r'[\d_]+', ' ', str(texto)).strip()
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    return texto_limpio.title() if texto_limpio else "Sin Especificar"

def extraer_estatus_caso_especifico(row_dict):
    prioridades = [
        "Estatus del PQRS / Estatus de caso",
        "Estatus del PQRS/ Estatus de caso",
        "Estatus de caso",
        "estatus_caso",
        "estatus_de_caso",
        "estatus_pqrs",
        "estatus",
        "seguimiento"
    ]
    for p in prioridades:
        for key, value in row_dict.items():
            if value is not None and str(value).strip() != "" and p.lower() in str(key).lower():
                return str(value).strip()
                
    for key, value in row_dict.items():
        if value is None or str(value).strip() == "":
            continue
        key_lower = str(key).lower()
        if ("estatus" in key_lower or "resolucion" in key_lower or "seguimiento" in key_lower) and not ("geo" in key_lower or "loc" in key_lower or "municipio" in key_lower):
            return str(value).strip()
            
    return "Recibido"

def extraer_fecha_aap(row_dict):
    claves_fecha = ["fecha", "fecha_recepcion", "fecha_pqrs", "today", "date", "_submission_time"]
    for cf in claves_fecha:
        for key, value in row_dict.items():
            if value and cf in str(key).lower():
                v_str = str(value).strip()
                if len(v_str) >= 8:
                    return v_str
    return None

# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS DESDE KOBOTOOLBOX (FORMULARIO PRINCIPAL Y AAP)
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

# CARGA Y BÚSQUEDA DINÁMICA DE CAMPOS KOBO AAP
@st.cache_data(ttl=3600)
def cargar_datos_aap(asset_id_aap, token_aap, kobo_url="https://eu.kobotoolbox.org"):
    headers = {"Authorization": f"Token {token_aap}"}
    url = f"{kobo_url}/api/v2/assets/{asset_id_aap}/data.json"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return pd.DataFrame()
        
        data = response.json().get('results', [])
        if not data:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    aap_rows = []
    for r in data:
        canal = extraer_campo_dinamico(r, ["canal"], "Buzón")
        tipo_pqrs_raw = extraer_campo_dinamico(r, ["tipo", "retroalimentacion"], "Información")
        estado_caso = extraer_estatus_caso_especifico(r)
        fecha_aap = extraer_fecha_aap(r)

        socio_val = str(r.get("ong") or r.get("socio") or r.get("group_pqrs/socio") or "COOPI").upper().strip()

        discapacidad = extraer_valor_booleano(r, ["discapacidad", "discapaz", "pcd"])
        indigena = extraer_valor_booleano(r, ["indigena", "poblacion_indigena", "etnia"])
        lgbtiq = extraer_valor_booleano(r, ["lgbtiq", "lgbt", "poblacion_lgbtiq"])
        embarazada = extraer_valor_booleano(r, ["embarazada", "lactante", "embarazada_o_lactante"])
        
        sexo_raw = str(r.get("sexo") or r.get("group_pqrs/sexo") or "").lower().strip()
        try:
            edad = float(r.get("edad") or r.get("group_pqrs/edad") or 0)
        except (ValueError, TypeError):
            edad = 0
            
        es_nina = 1 if (edad < 18 and edad > 0 and sexo_raw in ["femenino", "f", "mujer"]) or ("niña" in str(r).lower()) else 0
        es_nino = 1 if (edad < 18 and edad > 0 and sexo_raw in ["masculino", "m", "hombre"]) or ("niño" in str(r).lower()) else 0

        estado_geo_val = extraer_campo_dinamico(r, ["estado_geo", "group_datos_loc/Estado", "Estado"], "General")

        aap_rows.append({
            "_id": r.get("_id"),
            "Canal": limpiar_texto_categoria(canal),
            "Tipo_PQRS": limpiar_texto_categoria(tipo_pqrs_raw),
            "Estado_Caso": limpiar_texto_categoria(estado_caso),
            "Fecha": fecha_aap,
            "Discapacidad": discapacidad,
            "Indigena": indigena,
            "LGBTIQ": lgbtiq,
            "Embarazada": embarazada,
            "Es_Nina": es_nina,
            "Es_Nino": es_nino,
            "Socio": socio_val,
            "Estado_Geo": MAPA_ESTADOS.get(estado_geo_val, estado_geo_val)
        })

    df_aap = pd.DataFrame(aap_rows)
    
    if not df_aap.empty and "Fecha" in df_aap.columns:
        df_aap["Fecha_DT"] = pd.to_datetime(df_aap["Fecha"], errors='coerce')
        df_aap = df_aap.sort_values(by="Fecha_DT")
        df_aap["Mes_Reporte"] = df_aap["Fecha_DT"].apply(
            lambda x: f"{x.year} - {MESES_ES.get(x.month, '')}" if pd.notnull(x) else "Sin Fecha"
        )
    else:
        df_aap["Mes_Reporte"] = "Sin Fecha"

    return df_aap

# Cargar credenciales
try:
    KOBO_TOKEN = st.secrets["KOBO_TOKEN"]
    ASSET_ID = st.secrets["ASSET_ID"]
    df_raw = cargar_datos_kobo(ASSET_ID, KOBO_TOKEN)
except Exception:
    st.info("Por favor, configura tu KOBO_TOKEN y ASSET_ID en Secrets.")
    st.stop()

# Cargar datos AAP
ASSET_ID_AAP = "aRbFg8ig22Ts5JFFvsWNaE"
TOKEN_AAP = "a18c017a2e697f4ea1272375dae261ccec6b19d7"
df_aap_raw = cargar_datos_aap(ASSET_ID_AAP, TOKEN_AAP)

# -----------------------------------------------------------------------------
# 3. FILTROS LATERALES
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
st.sidebar.header("Filtros de Consulta General")

if df_raw.empty:
    st.warning("No se encontraron registros en el formulario de KoboToolbox.")
    st.stop()

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

sexo_disp = ["Todos", "Hombre", "Mujer", "Otro"]
sexo_sel = st.sidebar.selectbox("Sexo del Participante:", sexo_disp, key="f_sexo")

# Aplicar Filtros Generales
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
col1.metric("Total de Servicios a Participantes", f"{total_impactados:,}")
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
# 6. SEGUIMIENTO DE ACTIVIDADES POR SOCIO, SECTOR Y LOCALIDAD
# -----------------------------------------------------------------------------
st.subheader("Seguimiento de Actividades por Socio, Sector y Localidad")

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

col_act1, col_act2, col_act3 = st.columns(3)

with col_act1:
    socio_reporte = st.selectbox(
        "Filtrar Reporte por Socio:",
        options=["TODOS"] + socios_disponibles,
        index=0,
        key="act_socio_sel"
    )

with col_act2:
    sectores_act_list = ["TODOS"] + sorted(list(set(d["Sector"] for d in METAS_ACTIVIDADES.values())))
    sector_reporte = st.selectbox(
        "Filtrar por Sector:",
        options=sectores_act_list,
        index=0,
        key="act_sector_sel"
    )

with col_act3:
    localidades_list = ["TODOS"] + sorted([x for x in df_filtered["Estado"].dropna().unique() if x])
    localidad_reporte = st.selectbox(
        "Filtrar por Localidad (Estado):",
        options=localidades_list,
        index=0,
        key="act_localidad_sel"
    )

df_act_base = df_filtered.copy()
if localidad_reporte != "TODOS":
    df_act_base = df_act_base[df_act_base["Estado"] == localidad_reporte]

filas_reporte = []

for act_nombre, datos in METAS_ACTIVIDADES.items():
    sec = datos["Sector"]
    meta_proy = datos["Meta_Proyecto"]
    metas_socios = datos["Metas_Socios"]

    if sector_reporte != "TODOS" and sec != sector_reporte:
        continue

    if socio_reporte != "TODOS":
        if socio_reporte not in metas_socios:
            continue
        meta_socio = metas_socios[socio_reporte]
        
        df_act = df_act_base[
            (df_act_base["ONG"] == socio_reporte) &
            (
                df_act_base["Actividad"].str.contains(act_nombre, regex=False, case=False, na=False) |
                df_act_base["Sector"].str.contains(sec, regex=False, case=False, na=False)
            )
        ]
        alcanzado_val = df_act["ID_Unico"].nunique() if "ID_Unico" in df_act.columns else len(df_act)
        pct = (alcanzado_val / meta_socio * 100) if meta_socio > 0 else 0.0

        filas_reporte.append({
            "Sector": sec,
            "Actividad": act_nombre,
            "Socio": socio_reporte,
            "Meta Proyecto": meta_proy,
            "Meta Socio": meta_socio,
            "Alcanzados": alcanzado_val,
            "% Avance Socio": round(pct, 1)
        })
    else:
        df_act = df_act_base[
            df_act_base["Actividad"].str.contains(act_nombre, regex=False, case=False, na=False) |
            df_act_base["Sector"].str.contains(sec, regex=False, case=False, na=False)
        ]
        alcanzado_val = df_act["ID_Unico"].nunique() if "ID_Unico" in df_act.columns else len(df_act)
        pct = (alcanzado_val / meta_proy * 100) if meta_proy > 0 else 0.0

        filas_reporte.append({
            "Sector": sec,
            "Actividad": act_nombre,
            "Socio": "TODOS (Consorcio)",
            "Meta Proyecto": meta_proy,
            "Meta Socio": meta_proy,
            "Alcanzados": alcanzado_val,
            "% Avance Socio": round(pct, 1)
        })

df_reporte_act = pd.DataFrame(filas_reporte)

if not df_reporte_act.empty:
    st.dataframe(
        df_reporte_act.style.format({
            "Meta Proyecto": "{:,}",
            "Meta Socio": "{:,}",
            "Alcanzados": "{:,}",
            "% Avance Socio": "{:.1f}%"
        }),
        width="stretch",
        hide_index=True
    )

    buffer_act = io.BytesIO()
    with pd.ExcelWriter(buffer_act, engine='openpyxl') as writer:
        df_reporte_act.to_excel(writer, index=False, sheet_name='Actividades')
    buffer_act.seek(0)

    st.download_button(
        label="📥 Descargar Seguimiento de Actividades en Excel",
        data=buffer_act,
        file_name="Seguimiento_Actividades_Consorcio_Integras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # GRÁFICO DE BARRAS HORIZONTAL: META (AZUL) Y % AVANCE + ALCANZADOS (MORADO)
    fig_act_bars = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Meta (Barra Azul Marino - Eje Primario)
    fig_act_bars.add_trace(
        go.Bar(
            y=df_reporte_act["Actividad"],
            x=df_reporte_act["Meta Socio"],
            name="Meta de la Actividad",
            text=df_reporte_act["Meta Socio"],
            textposition="auto",
            orientation="h",
            marker_color='#08327D'  # Azul Marino
        ),
        secondary_y=False
    )

    # 2. % Avance y Valor Absoluto Alcanzado (Barra Morado/Rosado AAP - Eje Secundario)
    etiquetas_moradas = df_reporte_act.apply(
        lambda r: f"{r['% Avance Socio']:.1f}% ({r['Alcanzados']:,})", axis=1
    )

    fig_act_bars.add_trace(
        go.Bar(
            y=df_reporte_act["Actividad"],
            x=df_reporte_act["% Avance Socio"],
            name="% Avance y Alcanzados",
            text=etiquetas_moradas,
            textposition="auto",
            orientation="h",
            marker_color=COLOR_ROSADO_AAP  # Morado / Rosado AAP (#D89FE3)
        ),
        secondary_y=True
    )

    fig_act_bars.update_layout(
        title="Resultados por Actividad (Meta en Azul | Alcanzados y % Avance en Morado)",
        barmode="group",
        yaxis_title="Actividad",
        font=font_layout,
        height=550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig_act_bars.update_xaxes(title_text="Meta (Servicios / Personas)")
    fig_act_bars.update_yaxes(title_text="Actividad", secondary_y=False)
    fig_act_bars.update_yaxes(title_text="% Avance", secondary_y=True, showgrid=False, ticksuffix="%")

    st.plotly_chart(fig_act_bars, width="stretch")
else:
    st.info("No se registraron actividades correspondientes a los filtros seleccionados.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. GRÁFICOS INTERACTIVOS (POR PARTICIPANTES ÚNICOS)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader("Desglose por Sexo y Rango Etario (Participantes Únicos)")
    if total_unicos > 0 and "Grupo_Demografico" in df_unicos.columns:
        df_demo = df_unicos.groupby("Grupo_Demografico").size().reset_index(name="Cantidad")
        
        fig_pie_demo = px.pie(
            df_demo, 
            values="Cantidad", 
            names="Grupo_Demografico",
            hole=0.4,
            title="Participantes Únicos por Rango Etario y Sexo",
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_pie_demo.update_traces(textinfo="label+value+percent")
        fig_pie_demo.update_layout(
            showlegend=True,
            font=font_layout,
            title_font=dict(family="Now, Montserrat", size=16)
        )
        st.plotly_chart(fig_pie_demo, width="stretch")

with g2:
    st.subheader("Participantes Únicos por Sector")
    if total_unicos > 0 and "Sector" in df_filtered.columns:
        df_sec_unicos = df_filtered.drop_duplicates(subset=["ID_Unico", "Sector"])
        df_sec_cnt = df_sec_unicos["Sector"].value_counts().reset_index()
        df_sec_cnt.columns = ["Sector", "Unicos"]
        
        df_sec_cnt["Porcentaje"] = (df_sec_cnt["Unicos"] / total_unicos) * 100
        df_sec_cnt["Etiqueta"] = df_sec_cnt.apply(lambda r: f"{r['Unicos']} ({r['Porcentaje']:.0f}%)", axis=1)
        
        fig_bar_sec = px.bar(
            df_sec_cnt, 
            x="Sector", 
            y="Unicos", 
            color="Sector",
            text="Etiqueta",
            title="Distribución por Sector de Implementación",
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_bar_sec.update_traces(textposition="outside")
        fig_bar_sec.update_layout(
            showlegend=False,
            font=font_layout,
            title_font=dict(family="Now, Montserrat", size=16)
        )
        st.plotly_chart(fig_bar_sec, width="stretch")

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
# 9. TABLA DESGLOSE DE INDICADORES DEL PROYECTO
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
        "Valor_Absoluto": "Valor Absoluto (Servicios)",
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
# 10. REPORTE AAP (RENDICIÓN DE CUENTAS / PQRS)
# -----------------------------------------------------------------------------
st.markdown("<h2 class='titulo-aap'>Reporte AAP (Rendición de Cuentas - PQRS)</h2>", unsafe_allow_html=True)
st.caption("Sistema de Peticiones, Quejas, Reclamos y Sugerencias del Consorcio Integras")

lista_socios_aap = ["TODOS"] + sorted(list(set(df_aap_raw["Socio"].unique()).union({"COOPI", "HIAS", "FLM", "PALUZ", "PLAFAM"})))
lista_poblacion_interes = ["TODOS", "Discapacidad", "Niñas", "Niños", "Comunidad Indígena", "LGBTIQ+", "Embarazadas / Lactantes"]

col_f_aap1, col_f_aap2, col_f_aap3 = st.columns([1.5, 1.5, 1])

with col_f_aap1:
    socio_aap_sel = st.selectbox("Filtrar Reporte AAP por Socio:", options=lista_socios_aap, index=0)

with col_f_aap2:
    poblacion_sel = st.selectbox("Población de Interés:", options=lista_poblacion_interes, index=0)

df_aap_filtered = df_aap_raw.copy()

if socio_aap_sel != "TODOS":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Socio"] == socio_aap_sel]
elif socio_sel != "Todos":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Socio"] == socio_sel]

if poblacion_sel == "Discapacidad":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Discapacidad"] == 1]
elif poblacion_sel == "Niñas":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Es_Nina"] == 1]
elif poblacion_sel == "Niños":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Es_Nino"] == 1]
elif poblacion_sel == "Comunidad Indígena":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Indigena"] == 1]
elif poblacion_sel == "LGBTIQ+":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["LGBTIQ"] == 1]
elif poblacion_sel == "Embarazadas / Lactantes":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Embarazada"] == 1]

if mes_sel != "Todos" and "Mes_Reporte" in df_aap_filtered.columns:
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Mes_Reporte"] == mes_sel]
if estado_sel != "Todos" and "Estado_Geo" in df_aap_filtered.columns:
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Estado_Geo"] == estado_sel]

total_pqrs = len(df_aap_filtered)
pct_meta_pqrs = (total_pqrs / META_PQRS_AAP) * 100

with col_f_aap3:
    st.metric(
        label="% Meta PQRS (10% de 32 mil pers.)",
        value=f"{pct_meta_pqrs:.2f}%",
        delta=f"{total_pqrs:,} / {int(META_PQRS_AAP):,} Meta"
    )

disc_pqrs = int(df_aap_filtered["Discapacidad"].sum()) if "Discapacidad" in df_aap_filtered.columns else 0
ninas_pqrs = int(df_aap_filtered["Es_Nina"].sum()) if "Es_Nina" in df_aap_filtered.columns else 0
ninos_pqrs = int(df_aap_filtered["Es_Nino"].sum()) if "Es_Nino" in df_aap_filtered.columns else 0
indig_pqrs = int(df_aap_filtered["Indigena"].sum()) if "Indigena" in df_aap_filtered.columns else 0
lgbtiq_pqrs = int(df_aap_filtered["LGBTIQ"].sum()) if "LGBTIQ" in df_aap_filtered.columns else 0
emb_pqrs = int(df_aap_filtered["Embarazada"].sum()) if "Embarazada" in df_aap_filtered.columns else 0

st.markdown("<br>", unsafe_allow_html=True)

m_col1, m_col2, m_col3, m_col4, m_col5, m_col6, m_col7 = st.columns(7)
m_col1.metric("Total PQRS", f"{total_pqrs:,}")
m_col2.metric("Discapacidad", f"{disc_pqrs:,}")
m_col3.metric("Niñas", f"{ninas_pqrs:,}")
m_col4.metric("Niños", f"{ninos_pqrs:,}")
m_col5.metric("Com. Indígena", f"{indig_pqrs:,}")
m_col6.metric("LGBTIQ+", f"{lgbtiq_pqrs:,}")
m_col7.metric("Embarazadas", f"{emb_pqrs:,}")

st.markdown("<br>", unsafe_allow_html=True)

aap_c1, aap_c2 = st.columns(2)

with aap_c1:
    st.markdown("### Canal más utilizado por los participantes")
    if total_pqrs > 0 and "Canal" in df_aap_filtered.columns:
        df_canal = df_aap_filtered["Canal"].value_counts().reset_index()
        df_canal.columns = ["Canal", "Cantidad"]
        df_canal = df_canal.sort_values(by="Cantidad", ascending=True)
        
        df_canal["Porcentaje"] = (df_canal["Cantidad"] / total_pqrs) * 100
        df_canal["Etiqueta"] = df_canal.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.0f}%)", axis=1)
        
        fig_canal = px.bar(
            df_canal,
            y="Canal",
            x="Cantidad",
            orientation="h",
            text="Etiqueta",
            color_discrete_sequence=[COLOR_AGUAMARINA]
        )
        fig_canal.update_traces(textposition="outside")
        fig_canal.update_layout(
            xaxis_title="Número de PQRS",
            yaxis_title="",
            font=font_layout,
            height=320
        )
        st.plotly_chart(fig_canal, width="stretch")
    else:
        st.info("No hay datos de canales registrados.")

with aap_c2:
    st.markdown("### Tipos de PQRS Recibidos")
    if total_pqrs > 0 and "Tipo_PQRS" in df_aap_filtered.columns:
        df_tipo = df_aap_filtered["Tipo_PQRS"].value_counts().reset_index()
        df_tipo.columns = ["Tipo", "Cantidad"]
        
        fig_tipo = px.pie(
            df_tipo,
            names="Tipo",
            values="Cantidad",
            hole=0.4,
            color_discrete_sequence=PALETA_INTEGRAS
        )
        fig_tipo.update_traces(textinfo="label+value+percent")
        fig_tipo.update_layout(
            showlegend=True,
            font=font_layout,
            height=320
        )
        st.plotly_chart(fig_tipo, width="stretch")
    else:
        st.info("No hay datos de tipos de PQRS.")

st.markdown("<br>", unsafe_allow_html=True)

aap_c3, aap_c4 = st.columns(2)

with aap_c3:
    st.markdown("### Participantes Atendidos por Mes")
    if total_pqrs > 0 and "Mes_Reporte" in df_aap_filtered.columns:
        df_mes_aap = df_aap_filtered.groupby("Mes_Reporte", sort=False).size().reset_index(name="Atendidos")
        df_mes_aap["Porcentaje"] = (df_mes_aap["Atendidos"] / total_pqrs) * 100
        df_mes_aap["Etiqueta"] = df_mes_aap.apply(lambda r: f"{r['Atendidos']} ({r['Porcentaje']:.0f}%)", axis=1)
        
        fig_mes_aap = px.area(
            df_mes_aap,
            x="Mes_Reporte",
            y="Atendidos",
            text="Etiqueta",
            color_discrete_sequence=['#08327D']
        )
        fig_mes_aap.update_traces(textposition="top center")
        fig_mes_aap.update_layout(
            xaxis_title="Mes",
            yaxis_title="PQRS Recibidos",
            font=font_layout,
            height=320
        )
        st.plotly_chart(fig_mes_aap, width="stretch")
    else:
        st.info("No hay datos de temporalidad.")

with aap_c4:
    st.markdown("### Seguimiento a los Casos")
    if total_pqrs > 0 and "Estado_Caso" in df_aap_filtered.columns:
        df_est_aap = df_aap_filtered["Estado_Caso"].value_counts().reset_index()
        df_est_aap.columns = ["Estado", "Cantidad"]
        
        df_est_aap = df_est_aap[df_est_aap["Estado"].str.lower() != "recibido"]
        
        df_est_aap["Porcentaje"] = (df_est_aap["Cantidad"] / total_pqrs) * 100
        df_est_aap["Etiqueta"] = df_est_aap.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.0f}%)", axis=1)
        
        MAPA_COLORES_ESTADO = {
            "Abierto": COLOR_VERDE_ABIERTO,
            "En Proceso": COLOR_VERDE_ABIERTO,
            "Pendiente": COLOR_VERDE_ABIERTO,
            "Cerrado": '#08327D',
            "Atendido": COLOR_AGUAMARINA
        }
        
        fig_est_aap = px.bar(
            df_est_aap,
            x="Estado",
            y="Cantidad",
            text="Etiqueta",
            color="Estado",
            color_discrete_map=MAPA_COLORES_ESTADO
        )
        fig_est_aap.update_traces(textposition="outside")
        fig_est_aap.update_layout(
            xaxis_title="Estado de Resolución",
            yaxis_title="Casos",
            showlegend=False,
            font=font_layout,
            height=320
        )
        st.plotly_chart(fig_est_aap, width="stretch")
    else:
        st.info("No hay datos de seguimiento de casos.")
