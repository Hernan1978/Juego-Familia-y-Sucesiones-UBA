import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# --- 2. FUNCIONES DE DATOS ---
def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P"])
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=["E", "A", "F", "P"])

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x:
            cont = x.read().strip().split(",")
            if len(cont) == 2: return cont
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# --- 3. ESTILOS (CORRECCIÓN DE VISIBILIDAD) ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { 
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
        background-size: cover; 
        background-attachment: fixed; 
    }
    /* Forzar texto blanco en toda la app */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span, .stRadio div { 
        color: #FFFFFF !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px #000000 !important; 
    }
    /* Estilo para los Inputs (Email y Nombre) */
    .stTextInput input, .stNumberInput input {
        color: #000000 !important; /* Texto que escribe el usuario en negro para que se vea en el fondo blanco del input */
        font-weight: bold !important;
    }
    .main .block-container { 
        background: rgba(0, 0, 0, 0.7) !important; 
        padding: 2.5rem !important; 
        border-radius: 20px !important; 
        border: 2px solid #D4AF37; 
        max-width: 950px !important; 
        margin: auto;
    }
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; text-transform: uppercase; text-align: center; }
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: #000000 !important; 
        font-weight: 900 !important; 
        width: 100%;
        border: 1px solid #FFFFFF;
    }
    .reloj-juez { 
        position: fixed; top: 30px; right: 30px; 
        background: #C0392B; color: white !important; 
        padding: 20px; border-radius: 15px; 
        font-size: 4rem; border: 4px solid #D4AF37; z-index: 1000; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE ESTADO ---
df_global = cargar_datos()
f_data = leer_f()
fase, t_limite = int(f_data[0]), float(f_data[1])
ahora = time.time()

banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 5. PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave de Acceso:", type="password")
    
    if clave == "derecho2024":
        st.success("Acceso concedido")
        if not df_global.empty and 'A' in df_global.columns:
            st.write(f"### 👥 Alumnos: {', '.join(df_global['A'].unique())}")
            st.download_button("📥 Descargar Excel", df_global.to_csv(index=False), "asistencia.csv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            f_sel = st.selectbox("Seleccionar Fase:", [0, 1, 2, 3, 4, 99], index=0)
            if st.button("CAMBIAR FASE"):
                escribir_f(f_sel, 0)
                st.rerun()
        with col2:
            t_set = st.number_input("Segundos Reloj:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, ahora + t_set)
                st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
    st.stop()

# --- 6. ACCESO ALUMNOS ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email Académico:")
    n = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and m and n:
        if not os.path.exists("d.csv"):
            with open("d.csv", "w") as f: f.write("E,A,F,P\n")
        with open("d.csv", "a") as f: f.write(f"{m.strip()},{n.strip()},0,0\n")
        st.session_state.u = {"e": m, "a": n}
        st.rerun()
    st.stop()

# --- 7. JUEGO ---
st.write(f"👤 Dr/a. **{st.session_state.u['a']}**")

if t_limite > ahora:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
    time.sleep(1)
    st.rerun()

if fase in banco:
    p = banco[fase]
    st.markdown(f"## {p['q']}")
    rta = st.radio("Seleccione su veredicto:", p["o"], key=f"radio_{fase}")
    if st.button("ENVIAR RESPUESTA"):
        if rta == p["k"]: st.success("✅ ¡Correcto!")
        else: st.error("❌ Incorrecto.")
elif fase == 99:
    st.balloons()
    st.markdown("<h1 style='color: #D4AF37; font-size: 5rem;'>🚀 SENTENCIA FINAL 🚀</h1>", unsafe_allow_html=True)
    st.write("### ¡Felicidades Doctores!")
else:
    st.write("### ⚖️ Esperando que el Juez inicie la sesión...")
    time.sleep(2)
    st.rerun()
