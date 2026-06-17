import streamlit as st


def load_aerospace_theme():
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Space+Mono:wght@400;700&display=swap');

    /* Global Font Override */
    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
    }

    .stApp {
        background-color: #050810;
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.02) 1px, transparent 1px),
            radial-gradient(circle at 50% 0%, #121b2b 0%, #050810 70%);
        background-size: 30px 30px, 30px 30px, 100% 100%;
        background-position: center center;
    }

    [data-testid="stMetric"] {
        background: rgba(15, 22, 35, 0.6);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 8px;
        padding: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border: 1px solid rgba(0, 229, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 229, 255, 0.1);
    }

    [data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace !important;
        color: #00E5FF;
        font-size: 2.2rem;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }

    .stButton > button {
        background: linear-gradient(135deg, #00E5FF 0%, #0082FF 100%);
        color: #050810 !important;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: none;
        border-radius: 4px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        background: linear-gradient(135deg, #33EBFF 0%, #0099FF 100%);
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0a0e17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    div[data-testid="stAlert"] {
        border-radius: 4px;
        border-left: 4px solid;
    }
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
