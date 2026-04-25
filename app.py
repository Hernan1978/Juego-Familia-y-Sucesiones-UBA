import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA DE ALTA VISIBILIDAD ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    # Imagen de fondo: Biblioteca
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b0400da?q=80&w=2070" 
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85); 
            padding: 3rem; 
            border-radius: 20px; 
            border: 2px solid #D4AF37; 
        }}
        /* FUERZA LETRAS BLANCAS EN TODO EL SITIO */
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stMarkdownContainer"] p, .stRadio label {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px #000000 !important;
            font-size: 1.4rem !important;
            font-weight: bold !important;
        }}
        h1 {{ font-size: 3.5rem !important; }}
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            font-size: 1.5rem !important; 
            width: 100%; 
            height: 4rem;
            border-radius: 10px;
        }}
        /* Estilo para la barra lateral (Panel Docente) */
        [data-testid="stSidebar"] {{
            background-color: rgba(26, 58, 90, 0.9) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo escrito a máquina pero firmado?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"},
    4: {"q": "¿El cónyuge hereda sobre los gananciales con hijos?", "op": ["Sí", "No", "Solo la mitad"], "ok": "No"},
    5: {"q": "¿Es posible el pacto sobre herencia futura (Art. 1010)?", "op": ["Nunca", "Sí, excepcionalmente", "Siempre"], "ok": "Sí, excepcionalmente"},
    6: {"q": "¿La indignidad se purga con 3 años de posesión?", "op": ["Sí", "No", "Son 10 años"], "ok": "Sí"}
}

# --- 3. LÓGICA DE LOGIN (UNA SOLA VEZ) ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS - UBA")
    st.write("Complete sus datos para ingresar al recinto.")
    m = st.text_input("Email Institucional:")
    a = st.text_input("Alias para el Ranking:")
    if st.button("INGRESAR AL JUICIO"):
        if m and a and "@" in m:
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
        else:
            st.error("Datos incompletos o mail inválido.")
    st.stop()

# --- 4. PANEL DEL DOCENTE (LA BARRA LATERAL) ---
def set_fase(n):
    with open("fase.txt", "w") as f: f.write(str(n))

def get_fase():
    if not os.path.exists("fase.txt"): return 0
    with open("fase.txt", "r") as f:
        try: return int(f.read())
        except: return 0

with st.sidebar:
    st.header("🛂 MANDO DOCENTE")
    clave = st.text_input("Contraseña Maestro:", type="password")
    if clave == "derecho2024":
        opciones = ["Registro (Espera)"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio Final"]
        seleccion = st.selectbox("Cambiar fase a:", opciones)
        if st.button("LANZAR FASE"):
            if "Registro" in seleccion: set_fase(0)
            elif "Podio" in seleccion: set_fase(99)
            else: set_fase(int(seleccion.split(" ")[1]))
            st.rerun()
    else:
        st.info("Espacio reservado para el Juez de la causa.")

# --- 5. DINÁMICA DEL JUEGO ---
fase = get_fase()

if fase == 0:
    st.header(f"🏛️ Sala de Espera: {st.session_state.usuario['alias']}")
    st.write("El Tribunal está deliberando. Aguarde el inicio de la sesión.")
    time.sleep(4) # Espera 4 segundos y refresca solo
    st.rerun()

elif fase in banco:
    pregunta = banco[fase]
    st.header(f"Ronda {fase}")
    st.write(f"### {pregunta['q']}")
    
    # El key dinámico asegura que la pregunta cambie correctamente
    eleccion = st.radio("Seleccione su respuesta:", pregunta['op'], key=f"pregunta_{fase}")
    
    if st.button
