import streamlit as st
import pandas as pd
import time
from utils.data_loader import load_fleet_summary, load_shap_values


def render():
    st.header("🛡️ Pre-Flight Risk Briefing")
    st.markdown(
        "### Generate a structured GO / NO-GO safety report for specific aircraft engine pairings.")
    st.markdown("---")

    df_fleet = load_fleet_summary()

    if df_fleet is not None:
        # Setting up the aircraft configuration form to capture engine telemetry IDs
        with st.form("preflight_form"):
            st.subheader("Aircraft Configuration Setup")
            st.markdown(
                "Select the telemetry IDs for the engines currently mounted to the airframe.")

            col_l, col_r = st.columns(2)

            with col_l:
                left_engine = st.selectbox(
                    "Left Engine (Port) ID:", options=list(range(1, 249)), index=11)

            with col_r:
                right_engine = st.selectbox(
                    "Right Engine (Starboard) ID:", options=list(range(1, 249)), index=57)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "GENERATE SAFETY BRIEFING", type="primary")

        if submitted:
            st.markdown("---")

            with st.status("Running pre-flight safety diagnostics...", expanded=True) as status:
                st.write("Initializing telemetry handshake...")
                time.sleep(0.4)

                # Extracting telemetry rows for the selected port and starboard engines
                left_rows = df_fleet[df_fleet['Engine ID'] == left_engine]
                right_rows = df_fleet[df_fleet['Engine ID'] == right_engine]

                if left_rows.empty or right_rows.empty:
                    status.update(label="Diagnostics Failed.",
                                  state="error", expanded=True)
                    st.error(
                        "Engine telemetry not found in active fleet database. Verify sensor connections.", icon="⚠️")
                    return

                st.write("Extracting RUL projections...")
                left_data = left_rows.iloc[0]
                right_data = right_rows.iloc[0]

                left_rul = left_data['Predicted Remaining Cycles (RUL)']
                right_rul = right_data['Predicted Remaining Cycles (RUL)']

                st.write("Cross-referencing SHAP stressor matrices...")
                time.sleep(0.4)

                st.write("Evaluating GO / NO-GO thresholds...")

                status.update(label="Diagnostics Complete.",
                              state="complete", expanded=False)

            # Evaluating the weakest link; overall aircraft safety depends on the lowest RUL
            min_rul = min(left_rul, right_rul)

            if min_rul < 30:
                engine_status = "NO-GO (GROUNDED)"
                color = "#FF1744"
                msg = "CRITICAL RISK: One or both engines are operating past safe margins. Immediate physical triage required."
            elif min_rul < 75:
                engine_status = "CONDITIONAL GO"
                color = "#F39C12"
                msg = "WARNING: Aircraft is cleared for short-haul operations only. Preventative maintenance required upon return."
            else:
                engine_status = "CLEARED FOR TAKEOFF (GO)"
                color = "#00E5FF"
                msg = "SYSTEM NOMINAL: Both engines are operating within optimal safety parameters."

            st.markdown(f"""
            <div style="background-color: {color}15; border: 2px solid {color}; padding: 25px; border-radius: 8px; text-align: center; box-shadow: 0 0 20px {color}40;">
                <h1 style="color: {color}; margin: 0; font-family: 'Space Mono', monospace; letter-spacing: 2px; text-shadow: 0 0 10px {color};">{engine_status}</h1>
                <p style="color: #E0E6ED; margin-top: 10px; font-size: 1.2rem; font-weight: 600;">{msg}</p>
            </div>
            <br>
            """, unsafe_allow_html=True)

            col_det_l, col_det_r = st.columns(2)

            def display_engine_details(col, side, engine_id, rul, cycle):
                with col:
                    st.subheader(f"🛩️ [ {side} ] Engine ID: {engine_id}")
                    st.metric("AeroGlass XAI RUL", f"{rul:.1f} Cycles")

                    st.markdown("##### 🔬 Top 3 Thermodynamic Stressors")

                    # Loading SHAP matrices and isolating the top 3 features driving the degradation
                    shap_dict = load_shap_values(engine_id, int(cycle))
                    if shap_dict:
                        df_shap = pd.DataFrame(list(shap_dict.items()), columns=[
                                               'Sensor', 'Impact'])
                        df_shap['AbsImpact'] = df_shap['Impact'].abs()
                        top_3 = df_shap.sort_values(
                            by='AbsImpact', ascending=False).head(3)

                        for idx, row in top_3.iterrows():
                            direction = "[-] Accelerating Failure" if row['Impact'] < 0 else "[+] Extending Life"
                            st.markdown(f"**{row['Sensor']}**")
                            st.caption(
                                f"{direction} (SHAP Value: {row['Impact']:.2f})")
                            st.markdown(
                                "<hr style='margin: 5px 0px 15px 0px; opacity: 0.2;'>", unsafe_allow_html=True)
                    else:
                        st.caption(
                            "SHAP Data unavailable for this specific flight cycle.")

            display_engine_details(
                col_det_l, "PORT", left_engine, left_rul, left_data['Current Flight Cycles'])
            display_engine_details(
                col_det_r, "STARBOARD", right_engine, right_rul, right_data['Current Flight Cycles'])
