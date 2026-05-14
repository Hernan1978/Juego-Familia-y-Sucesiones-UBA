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
            st.markdown(f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P"])
    return pd.read_csv("d.csv")

def obtener_asistencia():
    if not os.path.exists("registro.txt"): return []
    with open("registro.txt", "r") as f:
        return [line.strip().split("|")[1] for line in f.readlines()]

# --- 3. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .main .block-container { background: rgba(0, 0, 0, 0.85) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: auto !important; text-align: center !important; }
    h1, h2, h3, p { color: #FFFFFF !important; font-weight: 800 !important; text-align: center !important; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; }
    .lista-asistentes { background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #D4AF37; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        asistentes = obtener_asistencia()
        st.write(f"### 👥 Alumnos en sala: {len(asistentes)}")
        st.markdown(f"<div class='lista-asistentes'>{', '.join(asistentes)}</div>", unsafe_allow_html=True)
        
        # Botón de Descarga Excel
        if os.path.exists("registro.txt"):
            df_asist = pd.read_csv("registro.txt", sep="|", names=["Email", "Nombre"])
            st.download_button("📥 Descargar Asistencia (Excel/CSV)", df_asist.to_csv(index=False), "asistencia.csv", "text/csv")
        
        if st.button("⚠️ REINICIAR TODO"):
            for f in ["d.csv", "registro.txt", "f.txt"]:
                if os.path.exists(f): os.remove(f)
            st.rerun()
    st.stop()

# --- 5. ACCESO ALUMNOS ---
if st.session_state.get('u') is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m_in = st.text_input("Email Académico:")
    n_in = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and "@" in m_in and n_in:
        with open("registro.txt", "a") as f: f.write(f"{m_in}|{n_in}\n")
        st.session_state.u = {"e": m_in, "a": n_in}
        st.rerun()
    
    # Mostrar lista de compañeros también en la pantalla de ingreso
    asistentes = obtener_asistencia()
    if asistentes:
        st.write("---")
        st.write(f"👥 **Ya conectados:** {', '.join(asistentes)}")
    st.stop()

# --- 6. JUEGO ---
st.markdown(f"👤 Dr/a. **{st.session_state.u['a']}**")
# [Tu lógica de juego original continúa aquí debajo...]
