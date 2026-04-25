import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA (Letras Blancas / Fondo Oscuro) ---
st.set_page_config(page_title="LexPlay: UBA Derecho", layout="wide")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.75); 
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }}
        h1, h2, h3, label, .stMarkdown p {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        .stRadio label {{
            color: #FFFFFF !important;
            font-size: 1.2rem !important;
        }}
        .stButton>button {{
            background-color: #FF4B4B !important;
            color: white !important;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS (CARGALAS ACÁ) ---
# Podés agregar todas las que quieras siguiendo el formato
banco_preguntas = {
    1: {
        "q": "¿Cuál es la porción legítima de los descendientes en el CCyC?",
        "op": ["1/2", "2/3", "4/5"],
        "ok": "2/3"
    },
    2: {
        "q": "¿Qué plazo tiene el heredero para aceptar o renunciar a la herencia?",
        "op": ["5 años", "10 años", "20 años"],
        "ok": "10 años"
    },
    3: {
        "q": "¿Es válido el testamento ológrafo escrito a máquina pero firmado a mano?",
        "op": ["Sí, es válido", "No, debe ser íntegramente de puño y letra", "Sólo si hay testigos"],
        "ok": "No, debe ser íntegramente de puño y letra"
    }
}

# --- 3. FUNCIONES DE CONTROL ---
def set_estado(n):
    with open("estado.txt", "w") as f: f.write(str(n))

def get_estado():
    if not os.path.exists("estado.txt"): return 0
    with open("estado.txt", "r") as f: return int(f.read())

# --- 4. PANEL DEL PROFESOR (BARRA LATERAL) ---
with st.sidebar:
    st.header("🛂 Control Docente")
    pwd = st.text_input("Clave", type="password")
    if pwd == "derecho2024":
        # Dinámicamente creamos las opciones según tu banco de preguntas
        opciones_fase = ["Registro"] + [f"Pregunta {i}" for i in banco_preguntas.keys()] + ["Podio Final"]
        fase_sel = st.selectbox("Ir a:", opciones_fase)
        
        if st.button("CAMBIAR FASE PARA TODOS"):
            if "Registro" in fase_sel: set_estado(0)
            elif "Podio" in fase_sel: set_estado(99)
            else: set_estado(int(fase_sel.split(" ")[1]))
            st.rerun()

# --- 5. INTERFAZ DEL ALUMNO ---
st.title("⚖️ Desafío Familia y Sucesiones")

email = st.text_input("📧 Email:")
alias = st.text_input("🎭 Alias:")

if not email or not alias:
    st.warning("Ingresá tus datos para participar.")
    st.stop()

fase_actual = get_estado()

# FASE 0: ESPERA
if fase_actual == 0:
    st.info(f"¡Hola {alias}! Esperá a que el profesor inicie el juego...")
    time.sleep(2)
    st.rerun()

# FASES DE PREGUNTAS
elif fase_actual in banco_preguntas:
    p = banco_preguntas[fase_actual]
    st.header(f"Ronda {fase_actual}")
    st.subheader(p["q"])
    
    rta = st.radio("Elegí tu respuesta:", p["op"])
    
    if st.button("Enviar Respuesta"):
        puntos = 100 if rta == p["ok"] else 0
        df = pd.DataFrame([[email, alias, puntos]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Voto enviado! Esperá a la siguiente ronda.")

# FASE 99: PODIO
elif fase_actual == 99:
    st.balloons()
    st.header("🏆 Resultados Finales")
    if os.path.exists("data.csv"):
        ranking = pd.read_csv("data.csv").groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        st.table(ranking)
    else:
        st.write("No hay votos registrados.")
