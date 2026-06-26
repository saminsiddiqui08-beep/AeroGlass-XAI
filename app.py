from utils.theme import load_aerospace_theme
from utils.data_loader import load_fleet_summary, _load_raw_shap_array
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AeroGlass XAI - Predictive Maintenance",
                   page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

load_aerospace_theme()

# Pre-loading heavy data matrices into the cache exactly once to prevent UI flickering
if 'warmed_up' not in st.session_state:
    with st.spinner("Loading pre-computed inference matrices into cache..."):
        load_fleet_summary()
        _load_raw_shap_array()
        st.session_state['warmed_up'] = True


def sidebar_navigation():
    with st.sidebar:
        st.title("AeroGlass XAI")
        st.caption("CMAPSS FD004 Engine Telemetry & Safety Audit")
        st.markdown("---")

        # Constructing the interactive sidebar using Bootstrap vector icons
        selected_page = option_menu(
            menu_title="System Navigation",
            options=[
                "Fleet Overview",
                "Interactive Telemetry Simulation",
                "Pre-Flight Risk Briefing",
                "XAI Safety Audit",
                "Operational ROI Calculator"
            ],
            icons=[
                "globe",
                "activity",
                "shield-check",
                "cpu",
                "graph-up-arrow"
            ],
            menu_icon="radar",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00E5FF", "font-size": "16px"},
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "5px 0px",
                    "--hover-color": "rgba(0, 229, 255, 0.05)",
                    "font-family": "'Rajdhani', sans-serif",
                    "color": "#E0E6ED"
                },
                "nav-link-selected": {
                    "background-color": "rgba(0, 229, 255, 0.1)",
                    "color": "#00E5FF",
                    "border-left": "3px solid #00E5FF",
                    "font-weight": "700"
                },
            }
        )

        st.markdown("---")

        st.markdown(
            """
            <div style='font-family: "Space Mono", monospace; font-size: 0.85rem; color: #7f8c8d;'>
                <span style='color: #00E5FF;'>●</span> SYSTEM ONLINE<br><br>
                MODEL: BiLSTM<br>
                ENGINE: CMAPSS FD004<br>
                XAI: Temporal Attention + Sensor-Level SHAP
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_page


def main():
    current_view = sidebar_navigation()

    # Routing the application state to the correct module based on user selection
    if current_view == "Fleet Overview":
        from views import fleet_overview
        fleet_overview.render()

    elif current_view == "Interactive Telemetry Simulation":
        from views import telemetry_simulation
        telemetry_simulation.render()

    elif current_view == "Pre-Flight Risk Briefing":
        from views import risk_briefing
        risk_briefing.render()

    elif current_view == "XAI Safety Audit":
        from views import xai_audit
        xai_audit.render()

    elif current_view == "Operational ROI Calculator":
        from views import cost_calculator
        cost_calculator.render()


if __name__ == "__main__":
    main()
