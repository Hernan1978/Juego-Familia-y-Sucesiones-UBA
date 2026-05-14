import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN Y FUNCIONES ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P"])
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=["E", "A", "F", "P"])

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# --- 2. ESTILOS ---
st.markdown("""<style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .main .block-container { background: rgba(0, 0, 0, 0.93) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; text-align: center; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; }
    .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white; padding: 20px; border-radius: 15px; font-size: 4rem; border: 4px solid #D4AF37; z-index: 1000; }
    </style>""", unsafe_allow_html=True)

# --- 3. DATOS Y PREGUNTAS ---
df_global = cargar_datos()
f_data = leer_f()
fase, t_limite = int(f_data[0]), float(f_data[1])
ahora = time.time()

banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. PANEL DEL JUEZ (ACCESO CON ?admin=true) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "derecho2024":
        if not df_global.empty and 'A' in df_global.columns:
            st.write(f"### 👥 Alumnos: {', '.join(df_global['A'].unique())}")
            st.download_button("📥 Descargar Excel", df_global.to_csv(index=False), "asistencia.csv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            f_sel = st.selectbox("Fase:", [0, 1, 2, 3, 4, 99])
            if st.button("CAMBIAR FASE"): escribir_f(f_sel, 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"): escribir_f(fase, ahora + t_set); st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                st.rerun()
    st.stop()

# --- 5. ACCESO ALUMNOS ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email:")
    n = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and "@" in m and n:
        if not os.path.exists("d.csv"):
            with open("d.csv", "w") as f: f.write("E,A,F,P\n")
        with open("d.csv", "a") as f: f.write(f"{m},{n},0,0\n")
        st.session_state.u = {"e": m, "a": n}; st.rerun()
    st.stop()

# --- 6. JUEGO ---
st.write(f"👤 Dr/a. {st.session_state.u['a']}")
if t_limite > ahora:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
    time.sleep(1); st.rerun()

if fase in banco:
    p = banco[fase]
    st.subheader(p["q"])
    rta = st.radio("Veredicto:", p["o"])
    if st.button("RESPONDER"):
        if rta == p["k"]: st.success("✅ ¡Correcto!")
        else: st.error("❌ Incorrecto.")

elif fase == 99:
    # EFECTO DE COHETES Y GLOBOS
    st.balloons()
    st.snow() # Este efecto simula partículas cayendo como ceniza de cohetes
    st.markdown("<h1 style='color: gold; font-size: 5rem;'>🚀🏆 SENTENCIA FINAL 🏆🚀</h1>", unsafe_allow_html=True)
    st.markdown("### ¡Felicidades a los Ganadores!")
