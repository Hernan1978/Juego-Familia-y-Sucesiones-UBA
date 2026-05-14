import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

if 'u' not in st.session_state: st.session_state.u = None
if 'audio_ok' not in st.session_state: st.session_state.audio_ok = False

# --- 2. FUNCIONES DE APOYO ---
def registrar_asistencia(nombre):
    with open("asistencia.csv", "a") as f:
        if not os.path.exists("asistencia.csv") or os.stat("asistencia.csv").st_size == 0: 
            f.write("Nombre,Hora\n")
        f.write(f"{nombre},{time.strftime('%H:%M:%S')}\n")

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# --- 3. ESTILOS ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .main .block-container { background: rgba(0, 0, 0, 0.93) !important; backdrop-filter: blur(15px); padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: 20px auto !important; text-align: center !important; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; margin-bottom: 20px; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; }
    .caja-admin { background: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 15px; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. PANEL DEL JUEZ (ADMIN) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Ingrese Clave:", type="password")
    
    if clave == "derecho2024":
        # Bloque de control administrativo
        if os.path.exists("asistencia.csv"):
            df_asist = pd.read_csv("asistencia.csv")
            nombres = df_asist['Nombre'].unique()
            st.markdown(f'<div class="caja-admin"><h3>📋 Alumnos presentes: {len(nombres)}</h3><p>{", ".join(nombres)}</p></div>', unsafe_allow_html=True)
            st.download_button("📥 Descargar Presentes", df_asist.to_csv(index=False), "presentes.csv", "text/csv")
        
        if st.button("⚠️ REINICIAR"):
            for f in ["d.csv", "f.txt", "asistencia.csv"]:
                if os.path.exists(f): os.remove(f)
            st.rerun()
    st.stop() # Esto detiene el resto del código para que el admin solo vea esto

# --- 5. ACCESO ALUMNOS ---
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    n_in = st.text_input("Ingrese su Nombre y Apellido:")
    if st.button("INGRESAR") and n_in:
        registrar_asistencia(n_in)
        st.session_state.u = {"a": n_in}
        st.rerun()
    st.stop()

# --- 6. JUEGO ---
st.write(f"### Bienvenido Dr/a. {st.session_state.u['a']}")
