import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_fleet_summary


def render():
    st.header("📈 [FINANCE] Operational ROI Calculator")
    st.markdown("### Translating predictive accuracy into financial impact.")
    st.markdown("---")

    df_fleet = load_fleet_summary()

    if df_fleet is not None:
        fleet_size = len(df_fleet)
        critical_engines = len(df_fleet[df_fleet['Status'] == 'CRITICAL'])

        st.markdown("### Interactive Financial Parameters")
        st.info("[SYSTEM GUIDE]: Adjust the costs below to match your airline's actual operating expenses. Crucially, use the AI False Negative Rate slider to stress-test the model. This slider simulates what happens if the AI's accuracy drops and it accidentally clears a failing engine for flight.")

        col_param1, col_param2, col_param3 = st.columns(3)

        with col_param1:
            cost_routine = st.number_input(
                "Routine Maintenance ($)",
                min_value=50000, max_value=500000, value=150000, step=10000
            )

        with col_param2:
            cost_aog = st.number_input(
                "Catastrophic Failure / AOG ($)",
                min_value=1000000, max_value=10000000, value=3500000, step=100000
            )

        with col_param3:
            ai_error_rate = st.slider(
                "AI False Negative Rate (%)",
                min_value=0.0, max_value=5.0, value=1.0, step=0.1
            )

        # Simulating financial outcomes by applying the AI false negative rate against catastrophic failure costs
        reactive_failures = int(fleet_size * 0.15)
        cost_reactive = reactive_failures * cost_aog
        cost_preventative = fleet_size * cost_routine
        false_negatives = fleet_size * (ai_error_rate / 100.0)

        cost_predictive = (critical_engines * cost_routine) + \
            (false_negatives * cost_aog)
        total_savings = cost_preventative - cost_predictive

        st.markdown("---")
        st.markdown("### Projected Annual Maintenance Expenditure")

        c1, c2, c3 = st.columns(3)

        c1.metric("Run-to-Failure (No AI)",
                  f"${cost_reactive / 1000000:.1f}M",
                  f"+${(cost_reactive - cost_preventative) / 1000000:.1f}M vs Baseline", delta_color="inverse")

        c2.metric("Fixed Schedule (Baseline)",
                  f"${cost_preventative / 1000000:.1f}M",
                  "Standard Airline Policy", delta_color="off")

        if total_savings >= 0:
            c3.metric("AeroGlass XAI", f"${cost_predictive / 1000000:.1f}M",
                      f"-${total_savings / 1000000:.1f}M Saved", delta_color="normal")
        else:
            c3.metric("AeroGlass XAI", f"${cost_predictive / 1000000:.1f}M",
                      f"+${abs(total_savings) / 1000000:.1f}M Lost", delta_color="inverse")

        st.markdown("---")

        col_bar, col_line = st.columns(2)

        with col_bar:
            st.subheader("Financial Strategy Comparison")
            cost_data = pd.DataFrame({
                "Strategy": ["Reactive", "Preventative", "AeroGlass XAI"],
                "Cost (Millions)": [cost_reactive / 1000000, cost_preventative / 1000000, cost_predictive / 1000000]
            })

            xai_color = '#00E5FF' if total_savings >= 0 else '#FF1744'
            bar_colors = ['#FF1744', '#7f8c8d', xai_color]

            # Generating a comparative horizontal bar chart to visualize total expenditure across maintenance strategies
            fig_bar = px.bar(
                cost_data, y="Strategy", x="Cost (Millions)", orientation='h', text="Cost (Millions)",
                color="Strategy", color_discrete_sequence=bar_colors, hover_data={"Strategy": False}
            )

            fig_bar.update_traces(
                texttemplate='$%{text:.1f}M', textposition='outside',
                hovertemplate='<b>%{y}</b><br>Total Cost: $%{x:.1f}M<extra></extra>',
                marker_line_color='white', marker_line_width=1.2, cliponaxis=False
            )

            fig_bar.update_layout(
                template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Total Cost (Millions USD)", yaxis_title="", showlegend=False,
                height=300, margin=dict(l=0, r=60, t=10, b=0),
                hoverlabel=dict(bgcolor="#050810", bordercolor="#00E5FF",
                                font_size=13, font_family="Rajdhani")
            )
            fig_bar.update_xaxes(range=[0, cost_data["Cost (Millions)"].max(
            ) * 1.25], showgrid=True, gridcolor="rgba(255,255,255,0.1)")
            fig_bar.update_yaxes(showgrid=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_line:
            st.subheader("📉 Break-Even Risk Analysis")

            error_rates = np.linspace(0, 5, 50)
            costs_curve = [((critical_engines * cost_routine) + (fleet_size *
                            (er / 100.0) * cost_aog)) / 1000000 for er in error_rates]

            df_curve = pd.DataFrame(
                {"AI Error Rate (%)": error_rates, "Cost (Millions USD)": costs_curve})

            # Plotting the break-even curve to determine the maximum tolerable AI error rate before financial loss
            fig_line = px.line(df_curve, x="AI Error Rate (%)",
                               y="Cost (Millions USD)")

            fig_line.add_hline(y=cost_preventative/1000000, line_dash="dash", line_color="#7f8c8d",
                               annotation_text="Baseline Fixed-Schedule Cost", annotation_position="bottom right", annotation_font_color="#7f8c8d")

            fig_line.add_vline(x=ai_error_rate, line_color=xai_color, line_dash="dot",
                               annotation_text="Current Simulation", annotation_position="top left", annotation_font_color=xai_color)

            fig_line.update_traces(line_color="#00E5FF", line_width=3)
            fig_line.update_layout(
                template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(l=0, r=0, t=10, b=0),
                hoverlabel=dict(bgcolor="#050810", bordercolor="#00E5FF",
                                font_size=13, font_family="Rajdhani")
            )
            fig_line.update_xaxes(
                showgrid=True, gridcolor="rgba(255,255,255,0.1)")
            fig_line.update_yaxes(
                showgrid=True, gridcolor="rgba(255,255,255,0.1)")

            st.plotly_chart(fig_line, use_container_width=True)

        if total_savings >= 0:
            st.success(
                f"**[BUSINESS IMPACT]:** AeroGlass XAI is projected to save the airline **${total_savings / 1000000:.1f} Million USD** annually.")
        else:
            st.error(
                f"**[BUSINESS IMPACT]:** At this high AI Error Rate, the predictive model is costing the airline **${abs(total_savings) / 1000000:.1f} Million USD** more than standard scheduling.")

        st.markdown("---")

        # Compiling the financial simulation parameters into a downloadable CSV report for executive review
        report_df = pd.DataFrame({
            "Metric": ["Total Fleet Size", "Critical Engines", "Assumed Routine Cost", "Assumed Failure Cost", "AI False Negative Rate", "Projected Annual Savings"],
            "Value": [fleet_size, critical_engines, f"${cost_routine}", f"${cost_aog}", f"{ai_error_rate}%", f"${total_savings}"]
        })

        csv_data = report_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="DOWNLOAD FINANCIAL PROJECTION (CSV)",
            data=csv_data,
            file_name="AeroGlass_Financial_Report.csv",
            mime="text/csv",
            type="primary"
        )
