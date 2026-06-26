import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_fleet_summary


def render():
    st.header("🌐 [SYSTEM] Fleet Health Overview")
    st.markdown(
        "### High-level aggregation of engine degradation across the active fleet.")
    st.markdown("---")

    df_fleet = load_fleet_summary()

    if df_fleet is not None:

        # Calculating aggregate fleet health metrics to establish a baseline operational capacity
        total_engines = len(df_fleet)
        avg_rul = df_fleet['Predicted Remaining Cycles (RUL)'].mean()

        healthy_engines = len(df_fleet[df_fleet['Status'] == 'HEALTHY'])
        critical_engines = len(df_fleet[df_fleet['Status'] == 'CRITICAL'])
        health_index = (healthy_engines / total_engines) * 100

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Active Engines", total_engines,
                    delta="Fleet Capacity", delta_color="off")
        col2.metric("Fleet Average RUL", f"{avg_rul:.1f} cycles",
                    delta="Nominal Health", delta_color="off")
        col3.metric("Critical Engines (< 30 Cycles)", critical_engines,
                    delta="Immediate Grounding Required", delta_color="inverse")

        st.markdown("---")

        col_chart, col_table = st.columns([3, 2])

        with col_chart:
            st.subheader("📊 Fleet Remaining Useful Life Distribution")

            # Rendering the distribution of Remaining Useful Life across the active fleet
            fig = px.histogram(
                df_fleet,
                x='Predicted Remaining Cycles (RUL)',
                nbins=30,
                color_discrete_sequence=["#00E5FF"],
                hover_data=['Engine ID', 'Status']
            )

            fig.update_traces(marker_line_color='white', marker_line_width=0.5)

            fig.add_vline(x=30, line_dash="dash", line_color="#FF1744",
                          annotation_text="Critical Threshold",
                          annotation_position="top right",
                          annotation_font_color="#FF1744")

            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Predicted RUL (Cycles)",
                yaxis_title="Number of Engines in Fleet",
                height=400,
                bargap=0.05,
                margin=dict(l=0, r=20, t=30, b=0),
                hoverlabel=dict(
                    bgcolor="#050810",
                    bordercolor="#00E5FF",
                    font_size=13,
                    font_family="Rajdhani"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        with col_table:

            # Constructing the top-level KPI gauge to display the aggregate fleet health index
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health_index,
                number={"suffix": "%", "font": {"size": 40,
                                                "color": "#00E5FF", "family": "Space Mono"}},
                title={"text": "Overall Fleet Health Index",
                       "font": {"size": 16, "color": "#E0E6ED"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
                    "bar": {"color": "#00E5FF"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 2,
                    "bordercolor": "rgba(255,255,255,0.1)",
                    "steps": [
                        {"range": [0, 50], "color": "rgba(255, 23, 68, 0.2)"},
                        {"range": [50, 80],
                            "color": "rgba(243, 156, 18, 0.2)"},
                        {"range": [80, 100],
                            "color": "rgba(0, 229, 255, 0.05)"}
                    ]
                }
            ))

            fig_gauge.update_layout(height=220, margin=dict(
                l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Rajdhani"})
            st.plotly_chart(fig_gauge, use_container_width=True)

            st.subheader("[!] Priority Triage List")
            st.markdown("Engines requiring immediate physical inspection.")

            # Filtering and sorting the cached fleet DataFrame to isolate engines requiring immediate mechanical triage
            df_triage = df_fleet[df_fleet['Status'].isin(
                ['CRITICAL', 'WARNING'])].copy()
            df_triage = df_triage.sort_values(
                'Predicted Remaining Cycles (RUL)').head(8)
            df_triage = df_triage[['Engine ID',
                                   'Predicted Remaining Cycles (RUL)', 'Status']]

            def highlight_status(val):
                if val == 'CRITICAL':
                    return 'color: #FF1744; font-weight: bold'
                elif val == 'WARNING':
                    return 'color: #F39C12; font-weight: bold'
                return ''

            st.dataframe(
                df_triage.style.map(highlight_status, subset=['Status']),
                hide_index=True,
                use_container_width=True
            )
