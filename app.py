import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ background-color: rgba(0, 0, 0, 0.85); padding: 3rem; border-radius: 20px; border: 2px solid #D4AF37; }}
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; font-size: 1.4rem !important; font-weight: bold !important; }}
        .stButton>button {{ background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; width: 100%; height: 3.5rem; }}
        .reloj-text {{ font-size: 4rem !important; color: #FF4B4B !important; text-align: center; font-family: 'Courier New', monospace; }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; min-width: 300px !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo escrito a máquina?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"}
}

# --- 3. PERSISTENCIA DE DATOS (Fase y Tiempo) ---
def leer_archivo(nombre, default="0"):
    if not os.path.exists(nombre): return default
    with open(nombre, "r") as f: return f.read().strip()

def escribir_archivo(nombre, valor):
    with open(nombre, "w") as f: f.write(str(valor))

# --- 4. PANEL DOCENTE (?admin=true) ---
params = st.query_params
es_admin = params.get("admin") == "true"

if es_admin:
    with st.sidebar:
        st.title("🛂 MANDO DEL JUEZ")
        clave = st.text_input("Contraseña:", type="password")
        if clave == "derecho2024":
            fase_sel = st.selectbox("Cambiar fase:", ["Sala de Espera"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio Final"])
            if st.button("LANZAR FASE"):
                if "Sala" in fase_sel: escribir_archivo("fase.txt", 0)
                elif "Podio" in fase_sel: escribir_archivo("fase.txt", 99)
                else: escribir_archivo("fase.txt", fase_sel.split(" ")[1])
                escribir_archivo("tiempo.txt", "OFF") # Resetear tiempo al cambiar fase
                st.rerun()
            
            st.write("---")
            segundos = st.slider("Segundos de reloj:", 15, 30, 20)
            if st.button("⏱️ INICIAR CUENTA REGRESIVA"):
                final = time.time() + segundos
                escribir_archivo("tiempo.txt", final)
                st.rerun()
else:
    st.markdown("<style>[data-testid='collapsedControl'] {display: none;}</style>", unsafe_allow_html=True)

# --- 5. LÓGICA DE USUARIO ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["Email", "Alias", "Puntos"]).to_csv("data.csv", index=False)
            pd.DataFrame([[m, a, 0]], columns=["Email", "Alias", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
    st.stop()

# --- 6. JUEGO Y RELOJ ---
fase = int(leer_archivo("fase.txt"))
tiempo_final_raw = leer_archivo("tiempo.txt", "OFF")

if fase == 0:
    st.header("🏛️ Sala de Audiencias")
    st.info("Esperando inicio...")
    time.sleep(3)
    st.rerun()

elif fase in banco:
    p = banco[fase]
    st.header(f"Ronda {fase}")
    
    # Manejo del Reloj
    if tiempo_final_raw != "OFF":
        restante = int(float(tiempo_final_raw) - time.time())
        if restante > 0:
            st.markdown(f'<p class="reloj-text">⏳ {restante}s</p>', unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        else:
            st.markdown('<p class="reloj-text">🚫 ¡TIEMPO AGOTADO!</p>', unsafe_allow_html=True)
            st.stop()
    
    st.write(f"### {p['q']}")
    rta = st.radio("Seleccione respuesta:", p['op'], key=f"r{fase}")
    if st.button("ENVIAR"):
        pts = 100 if rta == p['ok'] else 0
        pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], pts]], 
                     columns=["Email", "Alias", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
        st.success("¡Veredicto enviado!")

elif fase == 99:
    st.balloons()
    st.header("🏆 SENTENCIA FINAL")
    if os.path.exists("data.csv"):
        datos = pd.read_csv("data.csv")
        st.table(datos.groupby("Alias")["Puntos"].sum().sort_values(ascending=False))
