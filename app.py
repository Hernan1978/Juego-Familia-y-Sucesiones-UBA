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
                md = f"""
                    <audio id="{audio_id}" autoplay="true" style="display:none;">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    <script>
                        var audio = document.getElementById("{audio_id}");
                        audio.volume = 0.1; 
                    </script>
                """
                st.markdown(md, unsafe_allow_html=True)
                st.session_state.last_audio_time = ahora

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

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

def registrar_asistencia(nombre):
    with open("asistencia.csv", "a") as f:
        if not os.path.exists("asistencia.csv") or os.stat("asistencia.csv").st_size == 0: 
            f.write("Nombre,Hora\n")
        f.write(f"{nombre},{time.strftime('%H:%M:%S')}\n")

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

# --- 4. ESTILOS ---
def aplicar_estilo():
    st.markdown("""
        <style>
        header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
        .main .block-container { background: rgba(0, 0, 0, 0.93) !important; backdrop-filter: blur(15px); padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: 20px auto !important; text-align: center !important; }
        h1, h2, h3, h4, p, label, span, .stMarkdown { color: #FFFFFF !important; font-weight: 800 !important; text-align: center !important; }
        .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; margin-bottom: 20px; }
        .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; }
        .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }
        .usuario-badge { background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; margin-bottom: 25px; display: inline-block; width: 100%; }
        </style>
        """, unsafe_html=True)
aplicar_estilo()

# --- 5. PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        if os.path.exists("asistencia.csv"):
            df_asist = pd.read_csv("asistencia.csv")
            st.write(f"### 📋 Alumnos presentes: {len(df_asist['Nombre'].unique())}")
            st.download_button("📥 Descargar Lista de Presentes", df_asist.to_csv(index=False), "presentes.csv", "text/csv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + t_set); st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR"):
                for f in ["d.csv", "f.txt", "asistencia.csv"]:
                    if os.path.exists(f): os.remove(f)
                st.rerun()
    st.stop()

# --- 6. ACCESO ALUMNOS ---
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_html=True)
    if not st.session_state.audio_ok:
        if st.button("⚖️ ENTRAR AL TRIBUNAL"): st.session_state.audio_ok = True; st.rerun()
    else:
        play_audio("bienvenida.mp3") 
        m_in = st.text_input("Email Académico:")
        n_in = st.text_input("Nombre y Apellido:")
        if st.button("INGRESAR") and m_in and n_in:
            e_l, n_l = m_in.strip().lower(), n_in.strip().replace(',', '')
            registrar_asistencia(n_l)
            if not os.path.exists("d.csv"): with open("d.csv", "w") as f: f.write("E,A,F,P\n")
            with open("d.csv", "a") as f: f.write(f"{e_l},{n_l},0,0\n")
            st.session_state.u = {"e": e_l, "a": n_l}; st.rerun()
    st.stop()

# --- 7. JUEGO ---
st.markdown(f"<div class='usuario-badge'>👤 Dr/a. <b>{st.session_state.u['a']}</b></div>", unsafe_html=True)
ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)

# ... [Lógica de preguntas y podio se mantiene igual] ...
if fase == 99:
    total = df_global.groupby("A")["P"].sum().sort_values(ascending=False)
    idx = total.index.tolist()
    if st.session_state.u['a'] in idx and idx.index(st.session_state.u['a']) < 3: st.balloons()
    st.write("### 🏆 Fin de la competencia")
elif fase > 0:
    st.write("### Pregunta en curso...")
    if st.button("RESPONDER"): pass 
st.stop()
