import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")
st.markdown("""
    <style>
    #MainMenu, header, footer { visibility: hidden !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; }
    .main .block-container { 
        background: rgba(0, 0, 0, 0.85) !important; 
        border-radius: 25px !important; 
        padding: 50px !important; 
        border: 3px solid #D4AF37 !important;
    }
    h1, h2, h3, p, label { color: #FFFFFF !important; text-align: center !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
if 'u' not in st.session_state: st.session_state.u = None
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["Sí", "No"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.title("⚖️ PANEL DEL JUEZ")
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        if os.path.exists("registro.txt"):
            df = pd.read_csv("registro.txt", sep="|", names=["Email", "Nombre"])
            st.write(f"### 👥 Participantes ({len(df)}):")
            st.table(df)
            st.download_button("📥 Descargar Lista", open("registro.txt", "rb"), "asistencia.csv")
        
        fase = st.number_input("Configurar Fase (0-4):", 0, 4, 0)
        if st.button("ACTUALIZAR FASE"):
            with open("fase.txt", "w") as f: f.write(str(fase))
            st.rerun()
    st.stop()

# --- ACCESO ALUMNOS ---
if st.session_state.u is None:
    st.title("🏛️ LEXPLAY UBA")
    m_in = st.text_input("Email Institucional (debe incluir @):")
    n_in = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR"):
        if "@" in m_in and n_in:
            with open("registro.txt", "a") as f: f.write(f"{m_in}|{n_in}\n")
            st.session_state.u = {"e": m_in, "a": n_in}
            st.rerun()
        else: st.error("Email inválido o nombre vacío.")
    st.stop()

# --- JUEGO ---
st.write(f"👤 Dr/a. {st.session_state.u['a']}")
fase = int(open("fase.txt").read()) if os.path.exists("fase.txt") else 0
if fase == 0: st.info("Esperando instrucciones...")
elif fase in banco:
    p = banco[fase]
    st.subheader(p["q"])
    rta = st.radio("Respuesta:", p["o"])
    if st.button("ENVIAR"):
        if rta == p["k"]: st.success("✅ ¡Correcto!")
        else: st.error("❌ Incorrecto.")
elif fase == 99:
    st.balloons()
    st.success("🏆 ¡RESULTADOS FINALES!")
