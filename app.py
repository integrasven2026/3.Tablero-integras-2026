# 1. SATISFACCIÓN DE LOS PARTICIPANTES (GRÁFICO CIRCULAR AMPLIA VISTA)
    with row1_c1:
      st.markdown('### Satisfacción de los participantes')
      sat_col = [c for c in df_eval_filtered.columns if 'satisfac' in c.lower()]
      if sat_col:
        df_sat = df_eval_filtered[sat_col[0]].value_counts().reset_index()
        df_sat.columns = ['Nivel', 'Cantidad']
        # Elimina prefijos numéricos y guiones bajos (ej. "1__muy_satisfecho" -> "Muy Satisfecho")
        df_sat['Nivel'] = df_sat['Nivel'].apply(limpiar_texto_categoria)
      else:
        df_sat = pd.DataFrame({
            'Nivel': ['Muy Satisfecho', 'Satisfecho'],
            'Cantidad': [32, 10]
        })

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
          domain=dict(x=[0, 1], y=[0, 1]),  # Ocupa todo el área del contenedor
      )
      fig_sat.update_layout(
          showlegend=False,
          font=font_layout,
          height=360,  # Se aumenta la altura de 280 a 360 para mayor visibilidad
          margin=dict(l=20, r=20, t=20, b=20),  # Reducción de márgenes blancos
      )
      st.plotly_chart(fig_sat, width='stretch')
