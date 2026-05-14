import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")
st.markdown("""
    <style>
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .main .block-container { background: rgba(0, 0, 0, 0.93) !important; backdrop-filter: blur(15px); padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: 20px auto !important; text-align: center !important; }
    h1, h2, h3, h4, p, label, span, .stMarkdown { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center !important; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; margin-bottom: 20px; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P"])
    return pd.read_csv("d.csv")

banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 3. PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        clave = st.text_input("Clave de acceso:", type="password")
        if st.button("DESBLOQUEAR"):
            if clave == "derecho2024": st.session_state.auth = True; st.rerun()
            else: st.error("Clave incorrecta")
    else:
        df = cargar_datos()
        st.write(f"### 👥 Participantes: {', '.join(df['A'].unique()) if not df.empty else 'Ninguno'}")
        st.download_button("📥 Descargar Excel", df.to_csv(index=False), "asistencia.csv")
        fase = st.number_input("Configurar Fase (0-4):", 0, 4, 0)
        if st.button("ACTUALIZAR FASE"): 
            with open("f.txt", "w") as f: f.write(str(fase))
            st.rerun()
        if st.button("⚠️ REINICIAR"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            st.session_state.auth = False; st.rerun()
    st.stop()

# --- 4. ACCESO ALUMNOS ---
if st.session_state.get('u') is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m_in = st.text_input("Email Institucional:")
    n_in = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and "@" in m_in and n_in:
        with open("d.csv", "a") as f: f.write(f"{m_in},{n_in},0,0\n")
        st.session_state.u = {"e": m_in, "a": n_in}; st.rerun()
    st.stop()

# --- 5. JUEGO ---
st.write(f"👤 Dr/a. {st.session_state.u['a']}")
fase = int(open("f.txt").read()) if os.path.exists("f.txt") else 0
if fase in banco:
    p = banco[fase]
    st.subheader(p["q"])
    rta = st.radio("Veredicto:", p["o"])
    if st.button("RESPONDER"):
        if rta == p["k"]: st.success("✅ ¡Correcto!")
        else: st.error("❌ Incorrecto.")
elif fase == 99:
    st.balloons()
    st.success("🏆 ¡SENTENCIA FINAL!")
