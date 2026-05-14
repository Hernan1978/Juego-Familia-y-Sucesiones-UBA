import streamlit as st
import pandas as pd
import time
import os
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# --- 2. FUNCIONES DE REGISTRO ---
def validar_email(email):
    return re.match(r"[^@]+@.+\..+", email)

def registrar_participante(email, nombre):
    with open("asistencia.csv", "a") as f:
        f.write(f"{email}|{nombre}\n")

def obtener_participantes():
    if not os.path.exists("asistencia.csv"): return pd.DataFrame(columns=["Email", "Nombre"])
    return pd.read_csv("asistencia.csv", sep="|", names=["Email", "Nombre"])

# --- 3. ESTILOS (El diseño que ya tenías) ---
st.markdown("""
    <style>
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; }
    .main .block-container { background: rgba(0, 0, 0, 0.93); border: 2px solid #D4AF37; border-radius: 20px; padding: 2rem; }
    h1, h2, h3, .titulo-oro { color: #D4AF37 !important; text-align: center; text-transform: uppercase; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold; border: 2px solid #FFFFFF; }
    .usuario-badge { background: rgba(212, 175, 55, 0.2); border: 1px solid #D4AF37; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["Sí", "No"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 5. PANEL DEL JUEZ (ADMIN) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        df = obtener_participantes()
        st.write(f"### 👥 Participantes en sala: {len(df)}")
        st.table(df)
        st.download_button("📥 Descargar Asistencia", df.to_csv(index=False), "asistencia.csv")
        
        fase_juez = st.number_input("Configurar Fase:", 0, 4, 0)
        if st.button("ACTUALIZAR FASE"):
            with open("fase.txt", "w") as f: f.write(str(fase_juez))
            st.rerun()
    st.stop()

# --- 6. ACCESO ALUMNOS ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    mail = st.text_input("Email Institucional (debe incluir @):")
    nombre = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR"):
        if validar_email(mail) and nombre:
            registrar_participante(mail, nombre)
            st.session_state.u = {"n": nombre}
            st.rerun()
        else:
            st.error("Por favor, ingrese un mail válido con '@' y su nombre.")
    st.stop()

# --- 7. LÓGICA DE JUEGO ---
st.markdown(f"<div class='usuario-badge'>👤 Participante: <b>{st.session_state.u['n']}</b></div>", unsafe_allow_html=True)

# Leer fase del archivo
fase = int(open("fase.txt").read()) if os.path.exists("fase.txt") else 0

if fase == 0:
    st.info("Esperando instrucciones del Juez...")
elif fase in banco:
    p = banco[fase]
    st.subheader(f"Pregunta {fase}: {p['q']}")
    rta = st.radio("Responda:", p["o"])
    if st.button("ENVIAR RESPUESTA RÁPIDA"):
        if rta == p["k"]:
            st.success("✅ ¡Correcto!")
        else:
            st.error("❌ Incorrecto.")
elif fase == 99:
    st.balloons()
    st.success("🏆 ¡RESULTADOS FINALES Y PODIO!")
