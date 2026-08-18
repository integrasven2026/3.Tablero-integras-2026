# -----------------------------------------------------------------------------
# 11. SECCIÓN: INDICADORES AAP (FORMULARIO KOBO IND)
# -----------------------------------------------------------------------------
st.markdown(
    "<h2 class='titulo-indicadores-aap'>4. Indicadores AAP</h2>",
    unsafe_allow_html=True,
)
st.caption('Evaluación de Satisfacción y Conocimiento sobre Servicios AAP')

if not df_eval_aap.empty:
  # Filtros superiores + Métricas principales alineadas
  col_ind_soc, col_ind_pob, col_ind_tot, col_ind_meta = st.columns([1.5, 1.5, 1, 1.2])

  with col_ind_soc:
    socio_eval_sel = st.selectbox(
        'Filtrar Indicadores AAP por Socio:',
        options=lista_socios_aap,
        index=0,
        key='ind_socio_sel',
    )

  with col_ind_pob:
    poblacion_eval_sel = st.selectbox(
        'Población de Interés (Indicadores):',
        options=lista_poblacion_interes,
        index=0,
        key='ind_poblacion_sel',
    )

  df_eval_filtered = df_eval_aap.copy()

  # BÚSQUEDA ROBUSTA DE SOCIO SIN ERRORES DE APLY/JOIN
  if socio_eval_sel != 'TODOS':
    socio_col = [c for c in df_eval_filtered.columns if any(p in c.lower() for p in ['socio', 'ong', 'organizacion'])]
    if socio_col:
      col_target = socio_col[0]
      df_eval_filtered = df_eval_filtered[
          df_eval_filtered[col_target].astype(str).str.upper().str.strip() == socio_eval_sel.upper().strip()
      ]
    else:
      # Filtrado alternativo seguro vectorizado sin usar lambda axis=1
      mask = df_eval_filtered.astype(str).apply(lambda col: col.str.upper().str.contains(socio_eval_sel.upper(), na=False, regex=False)).any(axis=1)
      df_eval_filtered = df_eval_filtered[mask]

  # BÚSQUEDA ROBUSTA DE POBLACIÓN DE INTERÉS
  if poblacion_eval_sel == 'Personas con Discapacidad':
    disc_col = [c for c in df_eval_filtered.columns if any(p in c.lower() for p in ['discapacidad', 'pcd', 'discapaz'])]
    if disc_col:
      col_d = disc_col[0]
      df_eval_filtered = df_eval_filtered[
          df_eval_filtered[col_d].apply(lambda x: extraer_valor_booleano({col_d: x}, [col_d])) == 1
      ]
  elif poblacion_eval_sel == 'Niñas':
    mask_nina = df_eval_filtered.astype(str).apply(lambda col: col.str.lower().str.contains('niña', na=False, regex=False)).any(axis=1)
    df_eval_filtered = df_eval_filtered[mask_nina]
  elif poblacion_eval_sel == 'Niños':
    mask_nino = df_eval_filtered.astype(str).apply(lambda col: col.str.lower().str.contains('niño', na=False, regex=False)).any(axis=1)
    df_eval_filtered = df_eval_filtered[mask_nino]
  elif poblacion_eval_sel == 'Comunidad Indígena':
    ind_col = [c for c in df_eval_filtered.columns if any(p in c.lower() for p in ['indigena', 'etnia'])]
    if ind_col:
      col_i = ind_col[0]
      df_eval_filtered = df_eval_filtered[
          df_eval_filtered[col_i].apply(lambda x: extraer_valor_booleano({col_i: x}, [col_i])) == 1
      ]
  elif poblacion_eval_sel == 'LGBTIQ+':
    lgb_col = [c for c in df_eval_filtered.columns if any(p in c.lower() for p in ['lgbt', 'lgbtiq'])]
    if lgb_col:
      col_l = lgb_col[0]
      df_eval_filtered = df_eval_filtered[
          df_eval_filtered[col_l].apply(lambda x: extraer_valor_booleano({col_l: x}, [col_l])) == 1
      ]
  elif poblacion_eval_sel == 'Embarazadas / Lactantes':
    emb_col = [c for c in df_eval_filtered.columns if any(p in c.lower() for p in ['embarazada', 'lactante'])]
    if emb_col:
      col_e = emb_col[0]
      df_eval_filtered = df_eval_filtered[
          df_eval_filtered[col_e].apply(lambda x: extraer_valor_booleano({col_e: x}, [col_e])) == 1
      ]

  tot_part_eval = len(df_eval_filtered)
  pct_meta_eval = (tot_part_eval / META_5_PORCIENTO) * 100

  with col_ind_tot:
    st.metric('Total Participantes', f'{tot_part_eval:,}')

  with col_ind_meta:
    st.metric(
        label='% Meta (5% de 32 mil pers.)',
        value=f'{pct_meta_eval:.2f}%',
        delta=f'{tot_part_eval:,} / {int(META_5_PORCIENTO):,} Meta',
    )

  st.markdown('<br>', unsafe_allow_html=True)

  # GRÁFICOS 2x2
  row1_c1, row1_c2 = st.columns(2)

  # 1. SATISFACCIÓN DE LOS PARTICIPANTES
  with row1_c1:
    st.markdown('### Satisfacción de los participantes')
    sat_col = [c for c in df_eval_filtered.columns if 'satisfac' in c.lower()]
    
    if sat_col and not df_eval_filtered.empty:
      df_sat = df_eval_filtered[sat_col[0]].value_counts().reset_index()
      df_sat.columns = ['Nivel', 'Cantidad']
      df_sat['Nivel'] = df_sat['Nivel'].apply(limpiar_texto_categoria)
    else:
      df_sat = pd.DataFrame({'Nivel': [], 'Cantidad': []})

    if not df_sat.empty and df_sat['Cantidad'].sum() > 0:
      fig_sat = px.pie(
          df_sat,
          names='Nivel',
          values='Cantidad',
          hole=0.4,
          color_discrete_sequence=['#08327D', '#0072CE', COLOR_AGUAMARINA, COLOR_ROSADO_AAP],
      )
      fig_sat.update_traces(
          textinfo='label+value+percent',
          texttemplate='%{label}<br>%{value} (%{percent})',
          textposition='outside',
          domain=dict(x=[0, 1], y=[0, 1]),
      )
      fig_sat.update_layout(
          showlegend=False,
          font=font_layout,
          height=360,
          margin=dict(l=20, r=20, t=20, b=20),
      )
      st.plotly_chart(fig_sat, width='stretch')
    else:
      st.info('No hay registros de satisfacción para los filtros seleccionados.')

  # 2. CONOCIMIENTO DEL COMPORTAMIENTO ESPERADO
  with row1_c2:
    st.markdown('### Conocimiento del comportamiento esperado')
    comp_col = [c for c in df_eval_filtered.columns if 'comportamiento' in c.lower() or 'esperado' in c.lower()]
    
    if comp_col and not df_eval_filtered.empty:
      df_comp = df_eval_filtered[comp_col[0]].value_counts().reset_index()
      df_comp.columns = ['Respuesta', 'Cantidad']
      df_comp['Respuesta'] = df_comp['Respuesta'].apply(limpiar_texto_categoria)
    else:
      df_comp = pd.DataFrame({'Respuesta': [], 'Cantidad': []})

    if not df_comp.empty and df_comp['Cantidad'].sum() > 0:
      total_comp = df_comp['Cantidad'].sum()
      df_comp['Etiqueta'] = df_comp['Cantidad'].apply(
          lambda x: f"{x} ({(x / total_comp * 100):.1f}%)" if total_comp > 0 else f"{x}"
      )

      fig_comp = px.bar(
          df_comp,
          x='Respuesta',
          y='Cantidad',
          text='Etiqueta',
          color='Respuesta',
          color_discrete_map={
              'Sí': COLOR_AGUAMARINA,
              'Si': COLOR_AGUAMARINA,
              'No': COLOR_ROSADO_AAP,
          },
      )
      fig_comp.update_traces(textposition='outside')
      fig_comp.update_layout(
          showlegend=False,
          font=font_layout,
          height=360,
          yaxis_title='Cantidad',
          xaxis_title='Respuesta',
          margin=dict(l=20, r=20, t=20, b=20),
      )
      st.plotly_chart(fig_comp, width='stretch')
    else:
      st.info('No hay registros de comportamiento para los filtros seleccionados.')

  row2_c1, row2_c2 = st.columns(2)

  # 3. CONOCIMIENTO DEL CONSORCIO Y SERVICIOS
  with row2_c1:
    st.markdown('### Conocimiento del Consorcio y Servicios')
    cons_col = [c for c in df_eval_filtered.columns if 'consorcio' in c.lower() or 'servicio' in c.lower()]
    
    if cons_col and not df_eval_filtered.empty:
      df_cons = df_eval_filtered[cons_col[0]].value_counts().reset_index()
      df_cons.columns = ['Respuesta', 'Cantidad']
      df_cons['Respuesta'] = df_cons['Respuesta'].apply(limpiar_texto_categoria)
    else:
      df_cons = pd.DataFrame({'Respuesta': [], 'Cantidad': []})

    if not df_cons.empty and df_cons['Cantidad'].sum() > 0:
      total_cons = df_cons['Cantidad'].sum()
      df_cons['Etiqueta'] = df_cons['Cantidad'].apply(
          lambda x: f"{x} ({(x / total_cons * 100):.1f}%)" if total_cons > 0 else f"{x}"
      )

      fig_cons = px.bar(
          df_cons,
          y='Respuesta',
          x='Cantidad',
          orientation='h',
          text='Etiqueta',
          color='Respuesta',
          color_discrete_map={
              'Sí': COLOR_AMARILLO_MOSTAZA,
              'Si': COLOR_AMARILLO_MOSTAZA,
              'No': COLOR_AGUAMARINA,
          },
      )
      fig_cons.update_traces(textposition='outside')
      fig_cons.update_layout(
          showlegend=False,
          font=font_layout,
          height=320,
          xaxis_title='Cantidad',
          yaxis_title='Respuesta',
          margin=dict(l=20, r=20, t=20, b=20),
      )
      st.plotly_chart(fig_cons, width='stretch')
    else:
      st.info('No hay registros sobre el consorcio para los filtros seleccionados.')

  # 4. CONOCIMIENTOS DE LOS CANALES DE RETROALIMENTACIÓN
  with row2_c2:
    st.markdown('### Conocimientos de los canales de retroalimentación')
    ret_col = [c for c in df_eval_filtered.columns if 'canal' in c.lower() or 'retroalimentacion' in c.lower()]
    
    if ret_col and not df_eval_filtered.empty:
      df_ret = df_eval_filtered[ret_col[0]].value_counts().reset_index()
      df_ret.columns = ['Respuesta', 'Cantidad']
      df_ret['Respuesta'] = df_ret['Respuesta'].apply(limpiar_texto_categoria)
    else:
      df_ret = pd.DataFrame({'Respuesta': [], 'Cantidad': []})

    if not df_ret.empty and df_ret['Cantidad'].sum() > 0:
      total_ret = df_ret['Cantidad'].sum()
      df_ret['Etiqueta'] = df_ret['Cantidad'].apply(
          lambda x: f"{x} ({(x / total_ret * 100):.1f}%)" if total_ret > 0 else f"{x}"
      )

      fig_ret = px.bar(
          df_ret,
          x='Respuesta',
          y='Cantidad',
          text='Etiqueta',
          color='Respuesta',
          color_discrete_map={
              'Sí': COLOR_ROSADO_AAP,
              'Si': COLOR_ROSADO_AAP,
              'No': '#0072CE',
          },
      )
      fig_ret.update_traces(textposition='outside')
      fig_ret.update_layout(
          showlegend=False,
          font=font_layout,
          height=320,
          yaxis_title='Cantidad',
          xaxis_title='Respuesta',
          margin=dict(l=20, r=20, t=20, b=20),
      )
      st.plotly_chart(fig_ret, width='stretch')
    else:
      st.info('No hay registros de conocimiento de canales para los filtros seleccionados.')
else:
  st.info('Conexión establecida con KoboToolbox. Esperando registros del formulario de Indicadores AAP.')
