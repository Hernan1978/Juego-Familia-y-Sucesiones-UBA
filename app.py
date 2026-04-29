import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA Y SONIDOS ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {{ border: none !important; }}
        [data-testid="stVerticalBlock"] > div > div:nth-child(1) > div::before {{ display: none !important; content: none !important; }}
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(10px);
            padding: 3rem !important; margin-top: 40px !important; border-radius: 15px !important;
        }}

        /* TEXTOS EN BLANCO */
        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}

        /* INPUTS EN NEGRO/BLANCO */
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold !important;
        }}

        /* BOTONES */
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 900 !important; border: none !important; width: 100%;
        }}

        /* RELOJ IMPONENTE */
        .reloj-juez {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 20px 40px; border-radius: 15px;
            z-index: 99999; font-size: 4rem; font-family: 'Courier New', Courier, monospace;
            border: 4px solid #D4AF37;
        }}
        </style>
        """, unsafe_allow_html=True)

# Función para disparar audios
def play_audio(url):
    st.components.v1.html(f"""
        <audio autoplay><source src="{url}" type="audio/mp3"></audio>
    """, height=0)

aplicar_estilo()

# --- 2. GESTIÓN DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if os.path.exists("d.csv"):
        return pd.read_csv("d.csv")
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()

# --- 3. PANEL ADMINISTRADOR PRO ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ MANDO DEL JUEZ")
    clave = st.text_input("Contraseña:", type="password")
    if clave == "derecho2024":
        col1, col2 = st.columns(2)
        with col1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados", "Podio Final"])
            if st.button("CAMBIAR FASE / MOSTRAR GANADORES"):
                mapa = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados":10, "Podio Final":99}
                escribir_f(mapa[sel], 0); st.rerun()
        with col2:
            dur = st.number_input("Segundos:", 5, 60, 15)
            if st.button("LARGAR PREGUNTA"):
                escribir_f(fase, time.time() + dur); st.rerun()
        
        st.write("---")
        st.write("**👤 INTEGRANTES EN SALA:**")
        if not df_global.empty:
            participantes = df_global["A"].unique()
            st.write(", ".join(participantes))
    st.write("---")

# --- 4. LÓGICA DE USUARIO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ INGRESO AL TRIBUNAL")
    nombre = st.text_input("Nombre y Apellido:")
    if st.button("CONECTAR"):
        if nombre:
            pd.DataFrame([["-", nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"a": nombre}; st.rerun()
    st.stop()

ahora = time.time()
voto_realizado = not df_global[(df_global["A"] == st.session_state.u["a"]) & (df_global["F"] == fase)].empty if not df_global.empty else False

# --- 5. PANTALLAS ---

# RELOJ (Solo si la fase es pregunta y el usuario no votó)
if (0 < fase < 10) and (t_limite > ahora) and not voto_realizado:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
    # Sonido de tic-tac (opcional, poner link a mp3 corto)
    # play_audio("URL_TIC_TAC")

# FASE 0: ESPERA
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write("Aguarde a que el Juez abra el debate...")

# FASE 10: RESULTADOS INTERMEDIOS
elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        puntos = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(puntos)
    st.write("Prepárense para la siguiente ronda...")

# FASE 99: PODIO FINAL
elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA")
    st.balloons()
    if not df_global.empty:
        ganador = df_global.groupby("A")["P"].sum().idxmax()
        puntos_ganador = df_global.groupby("A")["P"].sum().max()
        st.markdown(f"<h1 style='text-align: center; font-size: 5rem; color: #D4AF37;'>🥇 {ganador}</h1>", unsafe_allow_html=True)
        st.write(f"Con un total de {puntos_ganador} puntos.")
        # play_audio("URL_FANFARRIA")

# FASES DE PREGUNTA
else:
    st.header(f"RONDA N° {fase}")
    if voto_realizado or (t_limite < ahora and t_limite != 0):
        st.success("⚖️ Veredicto cerrado. Esperando al Juez para ver resultados...")
    else:
        banco = {
            1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
            2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento por sobre cerrado?", "o": ["Sí", "No"], "k": "Sí"}
        }
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Su decisión:", banco[fase]['o'])
        if st.button("ENVIAR VOTO"):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([["-", st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            # play_audio("URL_CORRECTO" if pts > 0 else "URL_ERROR")
            st.rerun()

time.sleep(1); st.rerun()
