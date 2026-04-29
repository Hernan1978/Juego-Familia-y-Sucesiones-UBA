import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN VISUAL (TEXTO BLANCO / INPUTS NEGROS) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* 1. ELIMINAR BARRAS Y DECORACIONES DE STREAMLIT */
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {{ border: none !important; }}
        [data-testid="stVerticalBlock"] > div > div:nth-child(1) > div::before {{ display: none !important; content: none !important; }}
        hr {{ display: none !important; }}
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}

        /* 2. FONDO DE PANTALLA */
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
        }}

        /* 3. CONTENEDOR CENTRAL (VIDRIO OSCURO) */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(10px);
            padding: 3rem !important; 
            margin-top: 40px !important;
            border-radius: 15px !important;
            border: none !important;
        }}

        /* --- 4. TÍTULOS Y TEXTOS EN BLANCO --- */
        h1, h2, h3, h4, h5, h6, 
        p, label, span, 
        [data-testid="stWidgetLabel"] p, 
        .stMarkdown p {{ 
            color: #FFFFFF !important; 
            font-weight: 700 !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}

        /* --- 5. INPUTS (FONDO BLANCO, LETRA NEGRA) --- */
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 5px !important;
        }}
        
        /* Asegurar que el texto tipeado sea negro */
        input[type="text"], input[type="password"], input[type="number"] {{
            color: #000000 !important;
        }}

        /* BOTONES (DORADO / LETRA NEGRA) */
        .stButton>button {{ 
            background-color: #D4AF37 !important; 
            color: #000000 !important; 
            font-weight: 900 !important;
            border: none !important;
            text-transform: uppercase;
        }}

        /* RELOJ ROJO */
        .reloj-pantalla {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 15px 30px; border-radius: 10px;
            z-index: 99999; font-size: 3rem; font-weight: 900;
        }}
        </style>
        """, unsafe_allow_html=True)
