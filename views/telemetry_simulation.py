import streamlit as st
import time
import pandas as pd
from utils.data_loader import load_engine_data


def render():
    st.header("📡 Interactive Telemetry & Model Showdown")
    st.markdown(
        "### Simulated thermodynamic feeds and the Accuracy vs. Interpretability Trade-off.")
    st.markdown("---")

    col_control, col_info = st.columns([1, 2])

    with col_control:
        engine_id_selected = st.selectbox(
            "Select Engine ID for Telemetry:", options=list(range(1, 249)), index=0)

        playback_speed = st.slider("⏱️ Playback Speed Multiplier",
                                   min_value=1, max_value=10, value=5,
                                   help="1 = Standard playback, 10 = Fast-forward")

    with col_info:
        st.info("**Dual-Simulation Mode:** Watch the Baseline BiLSTM and the AeroGlass XAI Attention BiLSTM visualize pre-computed Remaining Useful Life estimates simultaneously.")

    st.markdown("---")

    # Fetching the complete historical telemetry for the selected engine
    df_engine_telemetry = load_engine_data(engine_id_selected)

    if df_engine_telemetry is not None and not df_engine_telemetry.empty:

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            start_stream = st.button(
                "▶ START TELEMETRY SIMULATION", type="primary")
        with col_btn2:
            stop_stream = st.button("⏹ STOP SIMULATION", type="secondary")

        # Allocating empty layout blocks to dynamically overwrite during the render loop
        metric_container = st.empty()
        chart_container = st.empty()

        if start_stream:
            st.session_state[f'alerted_{engine_id_selected}'] = False

            sleep_duration = 0.25 / playback_speed

            # Pre-computing data arrays before the loop to eliminate iterrows() render lag
            cycles = df_engine_telemetry['time_cycles'].tolist()
            temps = df_engine_telemetry['s4'].tolist()
            speeds = df_engine_telemetry['s14'].tolist()
            ruls_xai = df_engine_telemetry['AeroGlass_XAI_RUL'].tolist()
            ruls_adv = df_engine_telemetry['Baseline_Advanced_RUL'].tolist()

            df_plot_base = pd.DataFrame({
                "Cycle": cycles,
                "AeroGlass XAI": ruls_xai,
                "Baseline Advanced Model": ruls_adv
            }).set_index("Cycle")

            for i in range(len(cycles)):

                # Handling user interruption
                if stop_stream:
                    st.warning(
                        "Simulation interrupted by operator.", icon="⚠️")
                    break

                current_cycle = cycles[i]
                current_temp = temps[i]
                current_speed = speeds[i]
                current_rul_xai = ruls_xai[i]
                current_rul_adv = ruls_adv[i]

                # Rapidly slicing and rendering the pre-built dataframe to simulate sequential telemetry playback
                with metric_container.container():
                    st.subheader(f"Flight Cycle: {current_cycle}")

                    m1, m2, m3, m4 = st.columns(4)

                    if pd.isna(current_rul_xai):
                        m1.metric("AeroGlass XAI RUL", "Buffering...",
                                  delta="Initializing", delta_color="off")
                        m2.metric("Baseline Advanced RUL", "Buffering...",
                                  delta="Initializing", delta_color="off")
                    else:
                        m1.metric(
                            "AeroGlass XAI RUL", f"{current_rul_xai:.1f}", delta="Cyan Line", delta_color="normal")
                        m2.metric(
                            "Baseline Advanced RUL", f"{current_rul_adv:.1f}", delta="Magenta Line", delta_color="off")

                    m3.metric(
                        "S4 (LPT Temp) °R", f"{current_temp:.2f}", delta="Thermodynamic", delta_color="off")
                    m4.metric(
                        "S14 (Core Speed) rpm", f"{current_speed:.2f}", delta="Mechanical", delta_color="off")

                    # Triggering dual-alerts (toast + persistent UI block) when the engine enters the critical zone
                    if not pd.isna(current_rul_xai) and current_rul_xai < 30:

                        st.error(
                            f"CRITICAL ALERT: AeroGlass XAI predicts imminent engine failure in {current_rul_xai:.1f} cycles. Immediate physical triage required.", icon="🚨")

                        if not st.session_state.get(f'alerted_{engine_id_selected}'):
                            st.toast(
                                f"CRITICAL ALERT: Engine {engine_id_selected} approaching failure.", icon="🚨")
                            st.session_state[f'alerted_{engine_id_selected}'] = True

                with chart_container.container():
                    current_df = df_plot_base.iloc[:i+1]
                    st.line_chart(current_df, color=[
                                  "#00E5FF", "#FF2A6D"], height=250)

                time.sleep(sleep_duration)

            st.success("🏁 SESSION COMPLETE: Engine End-of-Life Reached.")

    st.markdown("---")
    with st.expander("Architectural Comparison: Baseline Advanced vs. AeroGlass XAI", expanded=False):
        st.markdown("""
        ### The "Accuracy vs. Interpretability" Trade-off
        In safety-critical domains like aerospace, pure predictive accuracy is not enough. Human engineers must be able to trust and audit the AI. This dashboard runs two models side-by-side to visually demonstrate this real-world engineering trade-off:
        
        ---

        #### [BASELINE] Advanced Model (Magenta Line)
        * **Architecture:** Standard Dual-Layer BiLSTM.
        * **Test RMSE:** 16.71 cycles.
        * **Pros:** Highly accurate. Its unconstrained weights allow it to find hyper-complex, invisible patterns in the sensor noise.
        * **Cons:** Operates entirely as an uninterpretable "Black Box." 

        #### [AEROGLASS] XAI Model (Cyan Line)
        * **Architecture:** Temporal Attention BiLSTM + SHAP.
        * **Test RMSE:** 19.59 cycles.
        * **Pros:** Physically auditable. Unlocks cycle-level temporal attention matrices and feature attribution, allowing engineers to verify the physical logic behind predictions.
        * **Cons:** Trades a marginal 2.88 cycles of raw accuracy to maintain mathematical constraints for the explainer.

        ---
        
        **The Verdict:** While the Baseline Advanced model mathematically saves ~2.8 cycles on paper, the AeroGlass model is fundamentally superior for enterprise deployment. Sacrificing a microscopic fraction of raw accuracy in exchange for the ability to definitively tell a mechanic *why* an engine is failing aligns with best practices for safety-critical AI certification and supports human-in-the-loop verification.
        """)
