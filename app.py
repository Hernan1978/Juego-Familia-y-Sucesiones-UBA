import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA (RESTAURADA AL 100%) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden; display: none; }}
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85) !important; 
            padding: 3rem 3rem !important; border-radius: 20px !important; 
            border: 2px solid #D4AF37 !important; margin-top: 50px !important;
        }}

        /* RELOJ SUPERIOR DERECHA - ROJO Y ORO */
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 25px !important; border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; z-index: 999999 !important;
            font-family: 'Courier New', monospace !important; font-size: 2.2rem !important;
            font-weight: bold !important; box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
            animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}

        /* TEXTOS BLANCOS CON SOMBRA */
        h1, h2, h3, p, label, span, .stMarkdown, .stRadio label {{ 
            color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000 !important; 
            font-size: 1.3rem !important; 
        }}
        h1 {{ font-size: 3rem !important; }}

        /* BOTONES ROJOS UBA */
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            font-size: 1.5rem !important; height: 3.5rem !important; 
            width: 100% !important; border: 1px solid #D4AF37 !important;
        }}
        
        .stButton>button:disabled {{
            background-color: #444444 !important; color: #888888 !important;
            border: 1px solid #222222 !important; cursor: not-allowed !important;
        }}

        /* MONITOR DE PARTICIPANTES ABAJO */
        .monitor-caja {{
            background-color: rgba(212, 175, 55, 0.1) !important;
            padding: 20px !important; border-radius: 15px !important;
            border: 1px solid #D4AF37 !important; margin-top: 50px !important;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

def leer(n, d="0"): return open(n, "r").read().strip() if os.path.exists(n) else d
def escribir(n, v): open(n, "w").write(str(v))

# --- 2. ESTADO ---
fase_actual = int(leer("fase.txt"))
tiempo_limite = leer("tiempo.txt", "OFF")

# --- 3. PANEL DOCENTE ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO DEL JUEZ")
        if st.text_input("Contraseña:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir("fase.txt", "0"); escribir("tiempo.txt", "OFF")
                st.session_state.clear(); st.rerun()
            st.write("---")
            f_sel = st.selectbox("Fase:", ["Sala de Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"], index=fase_actual if fase_actual != 99 else 4)
            if st.button("LANZAR FASE"):
                nv = 0 if "Sala" in f_sel else (99 if "Podio" in f_sel else int(f_sel.split(" ")[1]))
                escribir("fase.txt", nv); escribir("tiempo.txt", "OFF"); st.rerun()
            if 0 < fase_actual < 99:
                seg = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR TIEMPO"):
