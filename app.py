import io
import os
import re
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL CONSORCIO INTEGRAS
# -----------------------------------------------------------------------------
COLOR_AGUAMARINA = '#17C3B2'  # Verde / Azul Agua Marina oficial
COLOR_ROSADO_AAP = '#D89FE3'  # Morado / Rosado Orquídea para Reporte AAP
COLOR_VERDE_ABIERTO = '#28A745'  # Verde para Casos Abiertos / En Proceso
COLOR_AMARILLO_MOSTAZA = '#E5B130'  # Amarillo Mostaza para Indicadores AAP

PALETA_INTEGRAS = [
    COLOR_AGUAMARINA,
    COLOR_ROSADO_AAP,
    COLOR_AMARILLO_MOSTAZA,
    '#08327D',
    '#0072CE',
]

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y FUENTES PERSONALIZADAS (CSS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title='Tablero Consorcio Integras | COOPI',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
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

    .titulo-indicadores-aap {
        font-family: 'Now', 'Montserrat', sans-serif !important;
        color: #E5B130 !important;
        margin-top: 25px !important;
        margin-bottom: 10px !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ENCABEZADO Y LOGO
# -----------------------------------------------------------------------------
col_header_title, col_header_logo = st.columns([3, 1])

with col_header_title:
    st.markdown(
        "<h1 class='titulo-principal'>Tablero de Monitoreo - Consorcio"
        " Integras</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '**Socio Prime / Líder:** COOPI | **Colíder:** HIAS | **Socios'
        ' Implementadores:** FLM, PLAFAM, PALUZ'
    )

with col_header_logo:
    posibles_nombres = [
        'integras.jpg',
        'Integras.jpg',
        'Integras_logo.jpg',
        'integras_logo.jpg',
        'Integras_logo.png',
        'integras_logo.png',
    ]
    logo_path = None

    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            logo_path = nombre
            break

    URL_LOGO_GITHUB = 'https://raw.githubusercontent.com/integrasven2026/3.Tablero-integras-2026/main/integras.jpg'

    if logo_path:
        try:
            st.image(logo_path, width='stretch')
        except TypeError:
            st.image(logo_path, width='stretch')
    else:
        try:
            st.image(URL_LOGO_GITHUB, width='stretch')
        except Exception:
            st.warning("⚠️ No se pudo cargar el logo 'integras.jpg'.")

st.markdown('---')

# METAS DEL PROYECTO
META_PARTICIPANTES_UNICOS = 46122
META_BENEFICIARIOS_PROYECTO = 32000
META_5_PORCIENTO = META_BENEFICIARIOS_PROYECTO * 0.05  # 1,600 pers.

MESES_ES = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}

MAPA_ESTADOS = {
    'VE01': 'Distrito Capital',
    'VE07': 'Bolívar',
    'VE10': 'Delta Amacuro',
    'VE15': 'Miranda',
    'VE19': 'Sucre',
    'VE24': 'La Guaira',
}

MAPA_MUNICIPIOS = {
    'VE0101': 'Libertador',
    'VE0701': 'Caroní',
    'VE0707': 'Angostura',
    'VE1003': 'Pedernales',
    'VE1004': 'Tucupita',
    'VE1515': 'Paz Castillo',
    'VE1519': 'Sucre (Miranda)',
    'VE1520': 'Urdaneta',
    'VE1903': 'Arismendi',
    'VE1905': 'Bermúdez',
    'VE1908': 'Cruz Salmerón Acosta',
    'VE1914': 'Sucre (Sucre)',
    'VE2401': 'Vargas',
}

COORDENADAS_MUNICIPIOS = {
    'Libertador': [10.5000, -66.9167],
    'Caroní': [8.2833, -62.7167],
    'Angostura': [7.5333, -63.8833],
    'Pedernales': [9.9667, -62.2500],
    'Tucupita': [9.0622, -62.0531],
    'Paz Castillo': [10.2167, -66.6667],
    'Sucre (Miranda)': [10.4833, -66.8167],
    'Urdaneta': [10.1500, -66.8833],
    'Arismendi': [10.7167, -62.5167],
    'Bermúdez': [10.6333, -63.2500],
    'Cruz Salmerón Acosta': [10.6167, -64.2000],
    'Sucre (Sucre)': [10.2833, -63.8833],
    'Vargas': [10.6000, -66.9333],
}

MAPA_INDICADORES = {
    'R1I2': (
        'R1I2: Porcentaje de niños y cuidadores cuyas necesidades/riesgos'
        ' urgentes de protección infantil se han abordado a través del proceso'
        ' de gestión de casos.'
    ),
    'R1I3': (
        'R1I3: Número de personas que accedieron a asistencia jurídica gratuita.'
    ),
    'R1I4': (
        'R1I4: Porcentaje de aumento del conocimiento entre los participantes'
        ' sobre el tema de protección en cuestión.'
    ),
    'R1I5': (
        'R1I5: Porcentaje de las personas que reciben apoyo psicosocial'
        ' adecuado informan de una mejoría en su salud mental y bienestar'
        ' psicosocial O en su capacidad para afrontar las dificultades.'
    ),
    'R1I6': (
        'R1I6: Porcentaje de casos de alto riesgo de violencia de género'
        ' supervisados. (KRI)'
    ),
    'R1SI': 'R1SI: Sin indicador',
    'R2I1': 'R2I1: Número total de consultas de atención primaria de salud',
    'R2I2': (
        'R2I2: Porcentaje de partos atendidos por personal sanitario'
        ' cualificado (médicos, enfermeras, matronas)'
    ),
    'R2I3': 'R2I3: Número de consultas por staff al día',
    'R2I4': 'R2I4: Tasa de abandono ANC4/ANC1',
    'R2I5': (
        'R2I5: Número de centros sanitarios que implementan la segregación de'
        ' residuos y siguen las normas de gestión y tratamiento recomendadas.'
    ),
    'R2SI': 'R2SI: Sin indicador',
    'R3I1': (
        'R3I1: Número de niños menores de 5 años ingresados para el tratamiento'
        ' de la desnutrición aguda grave o moderada'
    ),
    'R3I2': (
        'R3I2: Número de mujeres embarazadas y/o lactantes ingresadas para'
        ' tratamiento por desnutrición aguda moderada grave o de alto riesgo.'
    ),
    'R3SI': 'R3SI: Sin indicador',
    'R4I1': (
        'R4I1: Número de personas beneficiarias que tienen acceso a agua'
        ' suficiente y segura para uso doméstico.'
    ),
    'R4I2': (
        'R4I2: Número de personas que tienen acceso regular y adecuado al jabón'
        ' para satisfacer sus necesidades higiénicas.'
    ),
    'R4I3': (
        'R4I3: Número de personas con acceso a instalaciones dignas, seguras,'
        ' limpias y funcionales para la eliminación de excretas.'
    ),
    'R4I4': (
        'R4I4: Porcentaje de la población objetivo que recibió asistencia y que'
        ' fue sensibilizada sobre prácticas seguras de gestión de residuos.'
    ),
    'R4SI': 'R4SI: Sin indicador',
    'R5I1': (
        'R5I1: Número de personas cubiertas por los planes de acción'
        ' temprana/contingencia.'
    ),
    'R5I2': 'R5I2: Número de alertas atendidas',
    'R5SI': 'R5SI: Sin indicador',
}

METAS_INDICADORES = {
    'R1I2': {'meta': 883.8, 'tipo': 'numero', 'etiqueta': '90% de 982 (884 pers.)'},
    'R1I3': {'meta': 910, 'tipo': 'numero', 'etiqueta': '910'},
    'R1I4': {
        'meta': 4635,
        'tipo': 'numero',
        'etiqueta': '75% de 6,180 (4,635 pers.)',
    },
    'R1I5': {
        'meta': 916.3,
        'tipo': 'numero',
        'etiqueta': '70% de 1,309 (916 pers.)',
    },
    'R1I6': {'meta': 0.90, 'tipo': 'porcentaje', 'etiqueta': '90%'},
    'R2I1': {'meta': 8622, 'tipo': 'numero', 'etiqueta': '8,622'},
    'R2I2': {'meta': 0.80, 'tipo': 'porcentaje', 'etiqueta': '80%'},
    'R2I3': {'meta': 20, 'tipo': 'numero', 'etiqueta': '20'},
    'R2I4': {'meta': 0.30, 'tipo': 'porcentaje', 'etiqueta': '30%'},
    'R2I5': {'meta': 5, 'tipo': 'numero', 'etiqueta': '5'},
    'R3I1': {'meta': 177, 'tipo': 'numero', 'etiqueta': '177'},
    'R3I2': {'meta': 34, 'tipo': 'numero', 'etiqueta': '34'},
    'R4I1': {'meta': 3200, 'tipo': 'numero', 'etiqueta': '3,200'},
    'R4I2': {'meta': 1200, 'tipo': 'numero', 'etiqueta': '1,200'},
    'R4I3': {'meta': 2800, 'tipo': 'numero', 'etiqueta': '2,800'},
    'R4I4': {'meta': 0.80, 'tipo': 'porcentaje', 'etiqueta': '80%'},
    'R5I1': {'meta': 800, 'tipo': 'numero', 'etiqueta': '800'},
    'R5I2': {'meta': 5100, 'tipo': 'numero', 'etiqueta': '5,100'},
}

font_layout = dict(family='Quicksand', size=13)


# -----------------------------------------------------------------------------
# CARGA DE DATOS DESDE EL EXCEL LOCAL (monitoring toll_integras_octubre.xlsx)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def cargar_datos_excel():
    archivo = 'monitoring toll_integras_octubre.xlsx'
    if not os.path.exists(archivo):
        st.error(
            f"⚠️ No se encontró el archivo '{archivo}' en el repositorio. Por"
            ' favor, asegúrate de que esté subido correctamente.'
        )
        return pd.DataFrame()

    try:
        df = pd.read_excel(archivo, sheet_name='beneficiarios')
        return df
    except Exception as e:
        st.error(
            f'Error al leer la hoja "beneficiarios" de {archivo}: {e}'
        )
        return pd.DataFrame()


df_raw = cargar_datos_excel()

if df_raw.empty:
    st.warning('El DataFrame está vacío o no se pudo cargar la hoja correctamente.')
    st.stop()


# Normalización de columnas y estandarización para asegurar compatibilidad
def procesar_dataframe_excel(df):
    # Asegurar nombres de columnas clave estándar
    cols = {c.lower(): c for c in df.columns}

    # Mapeo flexible de columnas comunes
    if 'ong' not in cols and 'socio' in cols:
        df['ONG'] = df[cols['socio']]
    elif 'ong' in cols:
        df['ONG'] = df[cols['ong']]
    else:
        df['ONG'] = 'COOPI'

    if 'estado' in cols:
        df['Estado'] = df[cols['estado']].map(MAPA_ESTADOS).fillna(df[cols['estado']])
    else:
        df['Estado'] = 'Sin Especificar'

    if 'municipio' in cols:
        df['Municipio'] = df[cols['municipio']].map(MAPA_MUNICIPIOS).fillna(df[cols['municipio']])
    else:
        df['Municipio'] = 'Sin Especificar'

    if 'sector' in cols:
        df['Sector'] = df[cols['sector']]
    else:
        df['Sector'] = 'Protección'

    if 'actividad' in cols:
        df['Actividad'] = df[cols['actividad']]
    else:
        df['Actividad'] = 'General'

    if 'sexo' in cols:
        df['Sexo'] = df[cols['sexo']].astype(str).str.capitalize()
    else:
        df['Sexo'] = 'Otro'

    if 'edad' in cols:
        df['Edad'] = pd.to_numeric(df[cols['edad']], errors='coerce').fillna(0)
    else:
        df['Edad'] = 0

    # Grupo demográfico
    def calcular_grupo_demo(row):
        edad = row.get('Edad', 0)
        sexo = row.get('Sexo', 'Otro')
        if edad < 18:
            return 'Niña' if sexo in ['Femenino', 'Mujer'] else 'Niño'
        else:
            return 'Mujer' if sexo in ['Femenino', 'Mujer'] else 'Hombre'

    if 'Grupo_Demografico' not in df.columns:
        df['Grupo_Demografico'] = df.apply(calcular_grupo_demo, axis=1)

    if 'id_unico' in cols:
        df['ID_Unico'] = df[cols['id_unico']]
    elif 'codigoid' in cols:
        df['ID_Unico'] = df[cols['codigoid']]
    else:
        df['ID_Unico'] = [f'ROW_{i}' for i in range(len(df))]

    if 'fecha' in cols:
        df['Fecha_DT'] = pd.to_datetime(df[cols['fecha']], errors='coerce')
        df['Mes_Reporte'] = df['Fecha_DT'].apply(
            lambda x: f"{x.year} - {MESES_ES.get(x.month, '')}" if pd.notnull(x) else 'Sin Fecha'
        )
    else:
        df['Mes_Reporte'] = 'Sin Fecha'

    # Indicadores códigos
    if 'indicadores_resultados' in cols:
        df['Indicadores_Codigos'] = df[cols['indicadores_resultados']].astype(str).apply(lambda x: x.split())
    else:
        df['Indicadores_Codigos'] = [[] for _ in range(len(df))]

    # Banderas de necesidad específica
    for col_necesidad, clave in [
        ('Es_Discapacidad', 'discapacidad'),
        ('Es_Indigena', 'indigena'),
        ('Es_Embarazada_Lactante', 'embarazada'),
        ('Es_LGBTIQ', 'lgbtiq'),
    ]:
        if clave in cols:
            df[col_necesidad] = pd.to_numeric(df[cols[clave]], errors='coerce').fillna(0).astype(int)
        else:
            df[col_necesidad] = 0

    return df


df_raw = procesar_dataframe_excel(df_raw)

# Simulación de datos AAP y evaluaciones AAP si no están en el Excel principal
df_aap_raw = df_raw.copy()
df_eval_aap = df_raw.copy()


# -----------------------------------------------------------------------------
# 3. FILTROS LATERALES
# -----------------------------------------------------------------------------
st.sidebar.header('Sincronización en Tiempo Real')

if st.sidebar.button('🔄 Actualizar Datos', width='stretch'):
    st.cache_data.clear()
    st.rerun()

if 'f_mes' not in st.session_state:
    st.session_state.f_mes = 'Todos'
if 'f_socio' not in st.session_state:
    st.session_state.f_socio = 'Todos'
if 'f_estado' not in st.session_state:
    st.session_state.f_estado = 'Todos'
if 'f_muni' not in st.session_state:
    st.session_state.f_muni = 'Todos'
if 'f_sector' not in st.session_state:
    st.session_state.f_sector = 'Todos'
if 'f_sexo' not in st.session_state:
    st.session_state.f_sexo = 'Todos'
if 'f_grupo_demo' not in st.session_state:
    st.session_state.f_grupo_demo = 'Todos'
if 'f_necesidad_esp' not in st.session_state:
    st.session_state.f_necesidad_esp = 'Todos'


def borrar_filtros():
    st.session_state.f_mes = 'Todos'
    st.session_state.f_socio = 'Todos'
    st.session_state.f_estado = 'Todos'
    st.session_state.f_muni = 'Todos'
    st.session_state.f_sector = 'Todos'
    st.session_state.f_sexo = 'Todos'
    st.session_state.f_grupo_demo = 'Todos'
    st.session_state.f_necesidad_esp = 'Todos'


st.sidebar.button('🧹 Limpiar Filtros', on_click=borrar_filtros, width='stretch')

st.sidebar.markdown('---')
st.sidebar.header('Filtros de Consulta General')

meses_ordenados = sorted(
    [m for m in df_raw['Mes_Reporte'].unique() if m != 'Sin Fecha']
)
if 'Sin Fecha' in df_raw['Mes_Reporte'].values:
    meses_ordenados.append('Sin Fecha')
meses_disp = ['Todos'] + meses_ordenados
mes_sel = st.sidebar.selectbox('Mes del Reporte:', meses_disp, key='f_mes')

socios_disp = ['Todos'] + sorted(
    [str(x) for x in df_raw['ONG'].dropna().unique() if x]
)
socio_sel = st.sidebar.selectbox('Socio / ONG:', socios_disp, key='f_socio')

estados_disp = ['Todos'] + sorted(
    [str(x) for x in df_raw['Estado'].dropna().unique() if x]
)
estado_sel = st.sidebar.selectbox('Estado:', estados_disp, key='f_estado')

df_temp = (
    df_raw if estado_sel == 'Todos' else df_raw[df_raw['Estado'] == estado_sel]
)
munis_disp = ['Todos'] + sorted(
    [str(x) for x in df_temp['Municipio'].dropna().unique() if x]
)
muni_sel = st.sidebar.selectbox('Municipio:', munis_disp, key='f_muni')

sectores_disp = ['Todos'] + sorted(
    [str(x) for x in df_raw['Sector'].dropna().unique() if x]
)
sector_sel = st.sidebar.selectbox(
    'Sector de Implementación:', sectores_disp, key='f_sector'
)

sexo_disp = ['Todos', 'Hombre', 'Mujer', 'Femenino', 'Masculino', 'Otro']
sexo_sel = st.sidebar.selectbox(
    'Sexo del Participante:', sexo_disp, key='f_sexo'
)

grupo_demo_disp = ['Todos', 'Mujer', 'Hombre', 'Niña', 'Niño']
grupo_demo_sel = st.sidebar.selectbox(
    'Grupo Demográfico:', grupo_demo_disp, key='f_grupo_demo'
)

necesidad_esp_disp = [
    'Todos',
    'Personas con Discapacidad',
    'Comunidad Indígena',
    'Embarazada / Lactante',
    'Población LGBTIQ+',
]
necesidad_esp_sel = st.sidebar.selectbox(
    'Necesidad Específica:', necesidad_esp_disp, key='f_necesidad_esp'
)

# Aplicar Filtros Generales
df_filtered = df_raw.copy()
if mes_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Mes_Reporte'] == mes_sel]
if socio_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['ONG'] == socio_sel]
if estado_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Estado'] == estado_sel]
if muni_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Municipio'] == muni_sel]
if sector_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Sector'] == sector_sel]
if sexo_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_sel]
if grupo_demo_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Grupo_Demografico'] == grupo_demo_sel]

if necesidad_esp_sel == 'Personas con Discapacidad':
    df_filtered = df_filtered[df_filtered['Es_Discapacidad'] == 1]
elif necesidad_esp_sel == 'Comunidad Indígena':
    df_filtered = df_filtered[df_filtered['Es_Indigena'] == 1]
elif necesidad_esp_sel == 'Embarazada / Lactante':
    df_filtered = df_filtered[df_filtered['Es_Embarazada_Lactante'] == 1]
elif necesidad_esp_sel == 'Población LGBTIQ+':
    df_filtered = df_filtered[df_filtered['Es_LGBTIQ'] == 1]

# -----------------------------------------------------------------------------
# 4. MÉTRICAS CLAVE
# -----------------------------------------------------------------------------
total_impactados = len(df_filtered)
df_unicos = df_filtered.drop_duplicates(subset=['ID_Unico'])
total_unicos = len(df_unicos)

pct_meta = (total_unicos / META_PARTICIPANTES_UNICOS) * 100

col1, col2, col3 = st.columns(3)
col1.metric('Total de Servicios a Participantes', f'{total_impactados:,}')
col2.metric('Total Participantes Únicos', f'{total_unicos:,}')
col3.metric('% Alcance de la Meta (46.122 pers.)', f'{pct_meta:.2f}%')

st.markdown('---')

# -----------------------------------------------------------------------------
# 6. SEGUIMIENTO DE ACTIVIDADES POR SOCIO, SECTOR Y LOCALIDAD
# -----------------------------------------------------------------------------
st.subheader('Seguimiento de Actividades por Socio, Sector y Localidad')

METAS_ACTIVIDADES = {
    'General Protection Case Management': {
        'Sector': 'Protección',
        'Meta_Proyecto': 2108,
        'Metas_Socios': {'COOPI': 1000, 'FLM': 608, 'HIAS': 500},
    },
    'Child-Friendly Spaces (CFS)': {
        'Sector': 'Protección',
        'Meta_Proyecto': 3526,
        'Metas_Socios': {'HIAS': 1500, 'FLM': 1100, 'COOPI': 926},
    },
    'Legal Aid & Documentation': {
        'Sector': 'Protección',
        'Meta_Proyecto': 1047,
        'Metas_Socios': {'COOPI': 400, 'HIAS': 350, 'FLM': 297},
    },
    'Individual Protection Assistance (IPA)': {
        'Sector': 'Protección',
        'Meta_Proyecto': 3194,
        'Metas_Socios': {'COOPI': 1200, 'HIAS': 1000, 'FLM': 994},
    },
    'Legal Aid on HLP': {
        'Sector': 'Protección',
        'Meta_Proyecto': 62,
        'Metas_Socios': {'COOPI': 25, 'HIAS': 20, 'FLM': 17},
    },
    'IPC Equipment & Bio-safety': {
        'Sector': 'WASH',
        'Meta_Proyecto': 2752,
        'Metas_Socios': {'COOPI': 2000, 'PALUZ': 752},
    },
    'Essential Health & Medicines': {
        'Sector': 'Salud',
        'Meta_Proyecto': 752,
        'Metas_Socios': {'PALUZ': 752},
    },
    'Health Staff Capacity Building': {
        'Sector': 'Salud',
        'Meta_Proyecto': 90,
        'Metas_Socios': {'PALUZ': 90},
    },
    'Sexual & Reproductive Health (SRH)': {
        'Sector': 'Salud',
        'Meta_Proyecto': 1144,
        'Metas_Socios': {'PLAFAM': 750, 'PALUZ': 394},
    },
    'Clinical Waste Management': {
        'Sector': 'WASH',
        'Meta_Proyecto': 30,
        'Metas_Socios': {'COOPI': 30},
    },
}

socios_disponibles = sorted(
    list(
        set(
            df_filtered['ONG'].unique().tolist()
            if 'ONG' in df_filtered.columns
            else ['COOPI']
        ).union({'COOPI', 'HIAS', 'FLM', 'PALUZ', 'PLAFAM'})
    )
)

col_act1, col_act2, col_act3 = st.columns(3)

with col_act1:
    socio_reporte = st.selectbox(
        'Filtrar Reporte por Socio:',
        options=['TODOS'] + socios_disponibles,
        index=0,
        key='act_socio_sel',
    )

with col_act2:
    sectores_act_list = ['TODOS'] + sorted(
        list(set(d['Sector'] for d in METAS_ACTIVIDADES.values()))
    )
    sector_reporte = st.selectbox(
        'Filtrar por Sector:',
        options=sectores_act_list,
        index=0,
        key='act_sector_sel',
    )

with col_act3:
    localidades_list = ['TODOS'] + sorted(
        [str(x) for x in df_filtered['Estado'].dropna().unique() if x]
    )
    localidad_reporte = st.selectbox(
        'Filtrar por Localidad (Estado):',
        options=localidades_list,
        index=0,
        key='act_localidad_sel',
    )

df_act_base = df_filtered.copy()
if localidad_reporte != 'TODOS':
    df_act_base = df_act_base[df_act_base['Estado'] == localidad_reporte]

filas_reporte = []

for act_nombre, datos in METAS_ACTIVIDADES.items():
    sec = datos['Sector']
    meta_proy = datos['Meta_Proyecto']
    metas_socios = datos['Metas_Socios']

    if sector_reporte != 'TODOS' and sec != sector_reporte:
        continue

    if socio_reporte != 'TODOS':
        if socio_reporte not in metas_socios:
            continue
        meta_socio = metas_socios[socio_reporte]

        df_act = df_act_base[
            (df_act_base['ONG'] == socio_reporte)
            & (
                df_act_base['Actividad'].astype(str).str.contains(
                    act_nombre, regex=False, case=False, na=False
                )
                | df_act_base['Sector'].astype(str).str.contains(
                    sec, regex=False, case=False, na=False
                )
            )
        ]
        alcanzado_val = (
            df_act['ID_Unico'].nunique()
            if 'ID_Unico' in df_act.columns
            else len(df_act)
        )
        pct = (alcanzado_val / meta_socio * 100) if meta_socio > 0 else 0.0

        filas_reporte.append({
            'Sector': sec,
            'Actividad': act_nombre,
            'Socio': socio_reporte,
            'Meta Proyecto': meta_proy,
            'Meta Socio': meta_socio,
            'Alcanzados': alcanzado_val,
            '% Avance Socio': round(pct, 1),
        })
    else:
        df_act = df_act_base[
            df_act_base['Actividad'].astype(str).str.contains(
                act_nombre, regex=False, case=False, na=False
            )
            | df_act_base['Sector'].astype(str).str.contains(
                sec, regex=False, case=False, na=False
            )
        ]
        alcanzado_val = (
            df_act['ID_Unico'].nunique()
            if 'ID_Unico' in df_act.columns
            else len(df_act)
        )
        pct = (alcanzado_val / meta_proy * 100) if meta_proy > 0 else 0.0

        filas_reporte.append({
            'Sector': sec,
            'Actividad': act_nombre,
            'Socio': 'TODOS (Consorcio)',
            'Meta Proyecto': meta_proy,
            'Meta Socio': meta_proy,
            'Alcanzados': alcanzado_val,
            '% Avance Socio': round(pct, 1),
        })

df_reporte_act = pd.DataFrame(filas_reporte)

if not df_reporte_act.empty:
    st.dataframe(
        df_reporte_act.style.format({
            'Meta Proyecto': '{:,}',
            'Meta Socio': '{:,}',
            'Alcanzados': '{:,}',
            '% Avance Socio': '{:.1f}%',
        }),
        width='stretch',
        hide_index=True,
    )

    buffer_act = io.BytesIO()
    with pd.ExcelWriter(buffer_act, engine='openpyxl') as writer:
        df_reporte_act.to_excel(writer, index=False, sheet_name='Actividades')
    buffer_act.seek(0)

    st.download_button(
        label='📥 Descargar Seguimiento de Actividades en Excel',
        data=buffer_act,
        file_name='Seguimiento_Actividades_Consorcio_Integras.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

    st.markdown('<br>', unsafe_allow_html=True)

    fig_act_bars = make_subplots(specs=[[{'secondary_y': True}]])

    fig_act_bars.add_trace(
        go.Bar(
            y=df_reporte_act['Actividad'],
            x=df_reporte_act['Meta Socio'],
            name='Meta de la Actividad',
            text=df_reporte_act['Meta Socio'],
            textposition='auto',
            orientation='h',
            marker_color='#08327D',
        ),
        secondary_y=False,
    )

    etiquetas_moradas = df_reporte_act.apply(
        lambda r: f"{r['% Avance Socio']:.1f}% ({r['Alcanzados']:,})", axis=1
    )

    fig_act_bars.add_trace(
        go.Bar(
            y=df_reporte_act['Actividad'],
            x=df_reporte_act['% Avance Socio'],
            name='% Avance y Alcanzados',
            text=etiquetas_moradas,
            textposition='auto',
            orientation='h',
            marker_color=COLOR_ROSADO_AAP,
        ),
        secondary_y=True,
    )

    fig_act_bars.update_layout(
        title='Resultados por Actividad',
        barmode='group',
        yaxis_title='Actividad',
        font=font_layout,
        height=550,
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1
        ),
    )

    fig_act_bars.update_xaxes(title_text='Meta (Servicios / Personas)')
    fig_act_bars.update_yaxes(title_text='Actividad', secondary_y=False)
    fig_act_bars.update_yaxes(title=None, showticklabels=False, secondary_y=True)

    st.plotly_chart(fig_act_bars, width='stretch')
else:
    st.info(
        'No se registraron actividades correspondientes a los filtros'
        ' seleccionados.'
    )

st.markdown('---')

# -----------------------------------------------------------------------------
# 7. GRÁFICOS INTERACTIVOS (POR PARTICIPANTES ÚNICOS)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader('Desglose por Sexo y Rango Etario (Participantes Únicos)')
    if total_unicos > 0 and 'Grupo_Demografico' in df_unicos.columns:
        df_demo = (
            df_unicos.groupby('Grupo_Demografico')
            .size()
            .reset_index(name='Cantidad')
        )

        fig_pie_demo = px.pie(
            df_demo,
            values='Cantidad',
            names='Grupo_Demografico',
            hole=0.4,
            title='Participantes Únicos por Rango Etario y Sexo',
            color_discrete_sequence=PALETA_INTEGRAS,
        )
        fig_pie_demo.update_traces(textinfo='label+value+percent')
        fig_pie_demo.update_layout(
            showlegend=True,
            font=font_layout,
            title_font=dict(family='Now, Montserrat', size=16),
        )
        st.plotly_chart(fig_pie_demo, width='stretch')

with g2:
    st.subheader('Participantes Únicos por Sector')
    if total_unicos > 0 and 'Sector' in df_filtered.columns:
        df_sec_unicos = df_filtered.drop_duplicates(subset=['ID_Unico', 'Sector'])
        df_sec_cnt = df_sec_unicos['Sector'].value_counts().reset_index()
        df_sec_cnt.columns = ['Sector', 'Unicos']

        df_sec_cnt['Porcentaje'] = (df_sec_cnt['Unicos'] / total_unicos) * 100
        df_sec_cnt['Etiqueta'] = df_sec_cnt.apply(
            lambda r: f"{r['Unicos']} ({r['Porcentaje']:.0f}%)", axis=1
        )

        fig_bar_sec = px.bar(
            df_sec_cnt,
            x='Sector',
            y='Unicos',
            color='Sector',
            text='Etiqueta',
            title='Distribución por Sector de Implementación',
            color_discrete_sequence=PALETA_INTEGRAS,
        )
        fig_bar_sec.update_traces(textposition='outside')
        fig_bar_sec.update_layout(
            showlegend=False,
            font=font_layout,
            title_font=dict(family='Now, Montserrat', size=16),
        )
        st.plotly_chart(fig_bar_sec, width='stretch')

st.markdown('---')

# -----------------------------------------------------------------------------
# 8. UBICACIÓN GEOGRÁFICA Y MAPA
# -----------------------------------------------------------------------------
st.subheader('Ubicación Geográfica por Municipio')

m1, m2 = st.columns([1, 1])

with m1:
    st.markdown('### Participantes Únicos por Municipio')
    if total_unicos > 0 and 'Municipio' in df_unicos.columns:
        df_muni = (
            df_unicos.groupby(['Estado', 'Municipio'])
            .size()
            .reset_index(name='Participantes_Unicos')
        )
        df_muni['Porcentaje'] = (
            df_muni['Participantes_Unicos'] / total_unicos
        ) * 100
        df_muni['Etiqueta'] = df_muni.apply(
            lambda r: f"{r['Participantes_Unicos']} ({r['Porcentaje']:.1f}%)",
            axis=1,
        )
        df_muni = df_muni.sort_values(by='Participantes_Unicos', ascending=True)

        fig_muni = px.bar(
            df_muni,
            y='Municipio',
            x='Participantes_Unicos',
            color='Estado',
            orientation='h',
            text='Etiqueta',
            height=400,
            color_discrete_sequence=PALETA_INTEGRAS,
        )
        fig_muni.update_traces(textposition='outside')
        fig_muni.update_layout(showlegend=False, font=font_layout)
        st.plotly_chart(fig_muni, width='stretch')

with m2:
    st.markdown('### Cobertura de la Intervención')

    mapa = folium.Map(
        location=[7.8, -65.5], zoom_start=6, tiles='CartoDB positron'
    )

    if total_unicos > 0:
        mapa_df = (
            df_filtered.drop_duplicates(subset=['ID_Unico', 'Sector'])
            .groupby(['Estado', 'Municipio', 'Sector'])
            .size()
            .reset_index(name='Cantidad')
        )
        muni_totales = (
            df_unicos.groupby(['Estado', 'Municipio'])
            .size()
            .reset_index(name='Total_Unicos')
        )

        for
