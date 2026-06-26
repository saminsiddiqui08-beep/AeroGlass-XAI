import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_engine_data, load_shap_values


def render():
    st.header("[XAI] Safety Audit")
    st.markdown("### Sensor-level SHAP feature attribution.")
    st.markdown("---")

    col_engine, col_cycle = st.columns(2)

    with col_engine:
        engine_id_selected = st.selectbox(
            "Select Engine ID to Audit:",
            options=list(range(1, 249)),
            index=0
        )

    # Extracting the selected engine telemetry to establish the maximum flight cycle bounds
    df_engine_telemetry = load_engine_data(engine_id_selected)

    if df_engine_telemetry is not None and not df_engine_telemetry.empty:
        max_cycle = int(df_engine_telemetry['time_cycles'].max())

        with col_cycle:
            target_cycle = st.slider(
                "Select Specific Flight Cycle:",
                min_value=30,
                max_value=max_cycle,
                value=max_cycle
            )

        st.markdown("---")
        st.subheader(
            f"Thermodynamic Driver Analysis - Engine {engine_id_selected} at Cycle {target_cycle}")

        # Loading the sensor-level SHAP dictionary and isolating the top 10 impact drivers
        shap_dict = load_shap_values(engine_id_selected, target_cycle)

        if shap_dict:
            df_shap = pd.DataFrame(list(shap_dict.items()), columns=[
                                   'Sensor', 'SHAP Impact'])
            df_shap['Absolute Impact'] = df_shap['SHAP Impact'].abs()

            df_shap = df_shap.sort_values(
                by='Absolute Impact', ascending=True).tail(10)

            def categorize_sensor(label):
                if 'Setting' in label:
                    return 'Operational Settings'
                elif 'Speed' in label:
                    return 'Mechanical Sensors (Speed)'
                else:
                    return 'Thermodynamic Sensors'

            df_shap['Sensor Category'] = df_shap['Sensor'].apply(
                categorize_sensor)

            color_map = {
                'Thermodynamic Sensors': '#c0392b',
                'Mechanical Sensors (Speed)': '#2980b9',
                'Operational Settings': '#7f8c8d'
            }

            # Rendering the interactive Plotly bar chart for feature attribution
            fig = px.bar(
                df_shap,
                x='SHAP Impact',
                y='Sensor',
                orientation='h',
                color='Sensor Category',
                color_discrete_map=color_map,
                hover_data={'Sensor Category': False, 'Absolute Impact': False}
            )

            fig.add_vline(x=0, line_dash="dash",
                          line_color="white", opacity=0.5)

            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                title=dict(
                    text="Top 10 Sensors Driving RUL Prediction", font=dict(size=18)),
                xaxis_title="SHAP Value (Impact on Prediction vs Fleet Baseline)",
                yaxis_title="",
                legend=dict(orientation="h", yanchor="top", y=-
                            0.2, xanchor="center", x=0.5, title=""),
                height=450,
                margin=dict(l=0, r=0, t=50, b=0),
                hoverlabel=dict(bgcolor="#050810", bordercolor="#00E5FF",
                                font_size=14, font_family="Space Mono", font_color="white")
            )

            st.plotly_chart(fig, use_container_width=True)

            # Generating a natural language diagnostic based on the highest impact sensor
            top_feature = df_shap.iloc[-1]
            top_sensor = top_feature['Sensor']
            top_impact = top_feature['SHAP Impact']
            top_cat = top_feature['Sensor Category']

            direction_text = "reducing the engine's predicted life" if top_impact < 0 else "extending the engine's predicted life"

            if "Thermodynamic" in top_cat:
                actionable_insight = "Investigate thermal stress limits, bleed valves, or turbine cooling mechanisms."
            elif "Mechanical" in top_cat:
                actionable_insight = "Check rotational mechanics, shaft vibration, or bearing wear."
            else:
                actionable_insight = "Review operational altitude and throttle resolver settings."

            st.info(
                f"**[DIAGNOSTIC SUMMARY]:** **{top_sensor}** is the dominant factor for this cycle, {direction_text} by **{abs(top_impact):.2f} cycles**. {actionable_insight}",
                icon="🔬"
            )

        else:
            st.error(
                "SHAP data is unavailable for this specific flight cycle.", icon="⚠️")
