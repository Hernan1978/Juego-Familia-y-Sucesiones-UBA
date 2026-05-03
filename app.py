import streamlit as st
import pandas as pd
import os
import time
import base64
import requests

# --- 1. FUNCIÓN DE AUDIO ---
def play_audio(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN Y URL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbw2lL020VODloofb-og7k7ERWXBYo5oa3axf5fRkX_e3JgA7lLs9PObfxHWw-T88lg_/exec"

if 'u' not in st.session_state: st.session_state.u = None
if 'audio_ok' not in st.session_state: st.session_state.audio_ok = False

# --- 3. GESTIÓN DE DATOS ---
def cargar_datos():
    cols = ["E", "A", "F", "P"]
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv("d.csv", on_bad_lines='skip', engine='c')
        for c in cols:
            if c not in df.columns: df[c] = None
        return df
    except: return pd.DataFrame(columns=cols)

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

def aplicar_estilo():
    st.markdown("""
        <style>
        /* ELIMINAR BARRA BLANCA Y ELEMENTOS DE STREAMLIT */
        header, [data-testid="stHeader"], .st-emotion-cache-18ni7ve, [data-testid="stToolbar"] {
            visibility: hidden !important;
            display: none !important;
        }
        
        .stApp { 
            background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
            background-size: cover; 
            background-attachment: fixed; 
        }
        
        .main .block-container { 
            background: rgba(0, 0, 0, 0.92) !important; 
            backdrop-filter: blur(15px); 
            padding: 3rem !important; 
            border-radius: 20px !important; 
            border: 2px solid #D4AF37; 
            margin-top: 20px;
        }

        h1, h2, h3, h4, p, label, span, .stMarkdown { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; }
        .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-align: center; text-transform: uppercase; }
        .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; width: 100% !important; }
        
        /* PODIO FULL CENTER */
        .podio-final-full-center {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 60vh;
            width: 100%;
        }
        .sentencia-final-titulo { color: #D4AF37 !important; font-size: 5rem !important; text-transform: uppercase; font-weight: 900 !important; margin-bottom: 40px; }
        .oro-podio { color: #FFD700 !important; font-size: 6rem !important; text-shadow: 0 0 30px gold; font-weight: 900 !important; }
        .plata-podio { color: #C0C0C0 !important; font-size: 4.5rem !important; text-shadow: 0 0 15px silver; margin: 20px 0; }
        .bronce-podio { color: #CD7F32 !important; font-size: 3.5rem !important; }
        
        .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }
        .usuario-badge { background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: right; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 4. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        inscriptos_list = df_global["A"].unique() if not df_global.empty else []
        st.write(f"### 👥 Alumnos en sala: {len(inscriptos_list)}")
        col1, col2, col3 = st.columns(3)
        with col1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + t
