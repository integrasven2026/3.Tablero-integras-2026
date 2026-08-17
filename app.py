with aap_c4:
    st.markdown("### Seguimiento a los Casos")
    if total_pqrs > 0 and "Estado_Caso" in df_aap_filtered.columns:
        df_est_aap = df_aap_filtered["Estado_Caso"].value_counts().reset_index()
        df_est_aap.columns = ["Estado", "Cantidad"]
        
        # Excluir la categoría "Recibido" de la visualización
        df_est_aap = df_est_aap[df_est_aap["Estado"].str.lower() != "recibido"]
        
        # Recalcular Porcentaje respecto al total de PQRS activos/visibles o general
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
