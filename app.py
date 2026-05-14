import streamlit as st
import pandas as pd
import os
import time
import base64
import requests

# --- 1. FUNCIÓN DE AUDIO ---
def play_audio(file_path):
    if os.path.exists(file_path):
        ahora = time.time()
        if 'last_audio_time' not in st.session_state: st.session_state.last_audio_time = 0
        if ahora - st.session_state.last_audio_time > 0.8:
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                audio_id = f"audio_{int(ahora)}"
                md = f'''<audio id="{audio_id}" autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                         <script>var audio = document.getElementById("{audio_id}"); audio.volume = 0.15;</script>'''
                st.markdown(md, unsafe_allow_html=True)
                st.session_state.last_audio_time = ahora

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbw2lL020VODloofb-og7k7ERWXBYo5oa3axf5fRkX_e3JgA7lLs9PObfxHWw-T88lg_/exec"

if 'u' not in st.session_state: st.session_state.u = None
if 'audio_ok' not in st.session_state: st.session_state.audio_ok = False

# --- 3. GESTIÓN DE DATOS ---
def cargar_datos():
    cols = ["E", "A", "F", "P"]
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=cols)
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=cols)

def leer_f():
    if os.path.exists("f.txt"): return open("f.txt", "r").read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# --- 4. PREGUNTAS Y ESTILOS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; }
    .main .block-container { background: rgba(0, 0, 0, 0.93) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; text-align: center; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

df_global = cargar_datos()
fase, t_limite = leer_f()
fase = int(fase)

# --- 5. PANEL DEL JUEZ (ACCESO CON CLAVE) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        if not df_global.empty:
            st.write(f"### 👥 Participantes: {', '.join(df_global['A'].unique())}")
            st.download_button("📥 Descargar Excel de Asistencia", df_global.to_csv(index=False), "asistencia.csv")
        
        # Controles originales
        col1, col2, col3 = st.columns(3)
        if col1.button("CAMBIAR FASE"): escribir_f(1, 0); st.rerun()
        if col2.button("⚠️ REINICIAR"): 
            if os.path.exists("d.csv"): os.remove("d.csv")
            st.rerun()
    st.stop()

# --- 6. ACCESO ALUMNOS ---
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m_in = st.text_input("Email Académico:")
    n_in = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and "@" in m_in and n_in:
        with open("d.csv", "a") as f: f.write(f"{m_in},{n_in},0,0\n")
        st.session_state.u = {"e": m_in, "a": n_in}; st.rerun()
    st.stop()

# --- 7. JUEGO ---
st.write(f"👤 Dr/a. {st.session_state.u['a']}")
st.write(f"👥 Participantes conectados: {', '.join(df_global['A'].unique())}")

if fase in banco:
    p = banco[fase]
    st.subheader(p["q"])
    rta = st.radio("Veredicto:", p["o"])
    if st.button("RESPONDER"):
        if rta == p["k"]: st.success("✅ Correcto")
        else: st.error("❌ Incorrecto")
elif fase == 99:
    st.balloons()
    st.success("🏆 ¡SENTENCIA FINAL!")
