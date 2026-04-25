import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA (RESTAURADA) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header {{ visibility: hidden; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background-color: rgba(0,0,0,0.85) !important; 
            padding: 2rem !important; border-radius: 15px !important; 
            border: 2px solid #D4AF37 !important; margin-top: 30px !important;
        }}
        .reloj-pantalla {{
            position: fixed !important; top: 15px !important; right: 15px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 10px 20px !important; border-radius: 30px !important;
            border: 2px solid #D4AF37 !important; z-index: 99999 !important;
            font-family: monospace !important; font-size: 2rem !important;
        }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 1px 1px 2px black; }}
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            font-weight: bold !important; border: 1px solid #D4AF37 !important;
        }}
        .stButton>button:disabled {{ background-color: #444 !important; color: #888 !important; }}
        .caja-p {{
            background-color: rgba(212,175,55,0.1) !important;
            padding: 15px !important; border-radius: 10px !important;
            border: 1px solid #D4AF37 !important; margin-top: 20px !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES ---
def leer(n, d="0"):
    if os.path.exists(n):
        with open(n, "r") as f: return f.read().strip()
    return d

def escribir(n, v):
    with open(n, "w") as f: f.write(str(v))

# --- 3. ESTADO ---
fase = int(leer("fase.txt"))
limite = leer("tiempo.txt", "OFF")

# --- 4. PANEL JUEZ ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ JUEZ")
        pwd = st.text_input("Clave:", type="password")
        if pwd == "derecho2024":
            if st.button("🗑️ REINICIAR"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir("f
