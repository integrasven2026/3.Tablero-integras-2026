# -----------------------------------------------------------------------------
# 10. REPORTE AAP (RENDICIÓN DE CUENTAS / PQRS)
# -----------------------------------------------------------------------------
st.markdown("<h2 class='titulo-aap'>Reporte AAP (Rendición de Cuentas - PQRS)</h2>", unsafe_allow_html=True)
st.caption("Sistema de Peticiones, Quejas, Reclamos y Sugerencias del Consorcio Integras")

# FILTRO PROPIO POR SOCIO PARA AAP
lista_socios_aap = ["TODOS"] + sorted(list(set(df_aap_raw["Socio"].unique()).union({"COOPI", "HIAS", "FLM", "PALUZ", "PLAFAM"})))

col_f_aap1, col_f_aap2 = st.columns([1, 3])
with col_f_aap1:
    socio_aap_sel = st.selectbox("Filtrar Reporte AAP por Socio:", options=lista_socios_aap, index=0)

df_aap_filtered = df_aap_raw.copy()

# Aplicación de Filtros al reporte AAP
if socio_aap_sel != "TODOS":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Socio"] == socio_aap_sel]
elif socio_sel != "Todos":
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Socio"] == socio_sel]

if mes_sel != "Todos" and "Mes_Reporte" in df_aap_filtered.columns:
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Mes_Reporte"] == mes_sel]
if estado_sel != "Todos" and "Estado_Geo" in df_aap_filtered.columns:
    df_aap_filtered = df_aap_filtered[df_aap_filtered["Estado_Geo"] == estado_sel]

# MÉTRICAS AAP EXPANDIDAS
total_pqrs = len(df_aap_filtered)
disc_pqrs = int(df_aap_filtered["Discapacidad"].sum()) if "Discapacidad" in df_aap_filtered.columns else 0
ninas_pqrs = int(df_aap_filtered["Es_Nina"].sum()) if "Es_Nina" in df_aap_filtered.columns else 0
ninos_pqrs = int(df_aap_filtered["Es_Nino"].sum()) if "Es_Nino" in df_aap_filtered.columns else 0
indig_pqrs = int(df_aap_filtered["Indigena"].sum()) if "Indigena" in df_aap_filtered.columns else 0
lgbtiq_pqrs = int(df_aap_filtered["LGBTIQ"].sum()) if "LGBTIQ" in df_aap_filtered.columns else 0

st.markdown("<br>", unsafe_allow_html=True)

# Tarjetas Métricas
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
m_col1.metric("Total PQRS", f"{total_pqrs:,}")
m_col2.metric("Discapacidad", f"{disc_pqrs:,}")
m_col3.metric("Niñas", f"{ninas_pqrs:,}")
m_col4.metric("Niños", f"{ninos_pqrs:,}")
m_col5.metric("Com. Indígena", f"{indig_pqrs:,}")
m_col6.metric("LGBTIQ+", f"{lgbtiq_pqrs:,}")

st.markdown("<br>", unsafe_allow_html=True)

# Gráficos principales AAP
aap_c1, aap_c2 = st.columns(2)

with aap_c1:
    st.markdown("### Canal más utilizado por los participantes")
    if total_pqrs > 0 and "Canal" in df_aap_filtered.columns:
        df_canal = df_aap_filtered["Canal"].value_counts().reset_index()
        df_canal.columns = ["Canal", "Cantidad"]
        df_canal = df_canal.sort_values(by="Cantidad", ascending=True)
        
        # Cálculo de Porcentaje + Formato de Etiqueta Combinada
        df_canal["Porcentaje"] = (df_canal["Cantidad"] / total_pqrs) * 100
        df_canal["Etiqueta"] = df_canal.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.1f}%)", axis=1)
        
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

# Atendidos por mes y Seguimiento a casos AAP
aap_c3, aap_c4 = st.columns(2)

with aap_c3:
    st.markdown("### Participantes Atendidos por Mes")
    if total_pqrs > 0 and "Mes_Reporte" in df_aap_filtered.columns:
        df_mes_aap = df_aap_filtered.groupby("Mes_Reporte").size().reset_index(name="Atendidos")
        df_mes_aap["Porcentaje"] = (df_mes_aap["Atendidos"] / total_pqrs) * 100
        df_mes_aap["Etiqueta"] = df_mes_aap.apply(lambda r: f"{r['Atendidos']} ({r['Porcentaje']:.1f}%)", axis=1)
        
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
        df_est_aap["Porcentaje"] = (df_est_aap["Cantidad"] / total_pqrs) * 100
        df_est_aap["Etiqueta"] = df_est_aap.apply(lambda r: f"{r['Cantidad']} ({r['Porcentaje']:.1f}%)", axis=1)
        
        fig_est_aap = px.bar(
            df_est_aap,
            x="Estado",
            y="Cantidad",
            text="Etiqueta",
            color_discrete_sequence=['#F3A738']
        )
        fig_est_aap.update_traces(textposition="outside")
        fig_est_aap.update_layout(
            xaxis_title="Estado de Resolución",
            yaxis_title="Casos",
            font=font_layout,
            height=320
        )
        st.plotly_chart(fig_est_aap, width="stretch")
    else:
        st.info("No hay datos de seguimiento de casos.")
