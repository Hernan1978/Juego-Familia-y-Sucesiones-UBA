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
        
        /* BOTÓN DE REINICIO (Rojo para advertir) */
        div.stButton > button:first-child[aria-label="⚠️ REINICIAR TODO EL JUEGO"] {{
            background-color: #C0392B !important;
            color: white !important;
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
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            sel = st.selectbox("Fase Actual:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados", "Podio Final"])
            if st.button("ACTUALIZAR FASE"):
                mapa = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados":10, "Podio Final":99}
                escribir_f(mapa[sel], 0); st.rerun()
        with col2:
            dur = st.number_input("Segundos:", 5, 60, 15)
            if st.button("LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with col3:
            st.write("") # Espaciador
            if st.button("⚠️ REINICIAR TODO EL JUEGO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        st.write("---")
        st.write("**👤 INTEGRANTES CONECTADOS:**")
        if not df_global.empty:
            # Mostramos a los que están en Fase 0 (los que se registraron)
            participantes = df_global[df_global["F"] == 0]["A"].unique()
            if len(participantes) > 0:
                for p in participantes:
                    st.caption(f"✅ {p}")
            else:
                st.write("Esperando ingresos...")
    st.write("---")

# --- 4. LÓGICA DE USUARIO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ INGRESO AL TRIBUNAL")
    nombre = st.text_input("Nombre y Apellido:")
    if st.button("CONECTAR"):
        if nombre:
            # Guardamos el registro con Fase 0
            pd.DataFrame([["-", nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"a": nombre}; st.rerun()
    st.stop()

ahora = time.time()
# Verificar si el usuario ya votó en esta fase
voto_realizado = not df_global[(df_global["A"] == st.session_state.u["a"]) & (df_global["F"] == fase)].empty if not df_global.empty else False

# --- 5. PANTALLAS ---

# RELOJ
if (0 < fase < 10) and (t_limite > ahora) and not voto_realizado:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# FASE 0: ESPERA
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Dr/a. **{st.session_state.u['a']}**, su presencia ha sido registrada. Aguarde el inicio de la audiencia.")

# FASE 10: RESULTADOS INTERMEDIOS
elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        # Sumamos puntos de todas las fases de preguntas (>0 y <10)
        puntos = df_global[df_global["F"] < 10].groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(puntos)
    st.write("Prepárense para la siguiente ronda...")

# FASE 99: PODIO FINAL
elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA")
    st.balloons()
    if not df_global.empty:
        total_puntos = df_global.groupby("A")["P"].sum()
        ganador = total_puntos.idxmax()
        puntos_ganador = total_puntos.max()
        st.markdown(f"<h1 style='text-align: center; font-size: 5rem; color: #D4AF37;'>🥇 {ganador}</h1>", unsafe_allow_html=True)
        st.write(f"<p style='text-align: center; font-size: 1.5rem;'>DICTAMEN: Excelencia Académica con {puntos_ganador} puntos.</p>", unsafe_allow_html=True)

# FASES DE PREGUNTA
else:
    st.header(f"RONDA N° {fase}")
    if voto_realizado:
        st.success("⚖️ Voto registrado. El reloj se ha detenido para usted. Aguarde los resultados.")
    elif t_limite < ahora and t_limite != 0:
        st.error("⌛ Tiempo agotado para esta ronda.")
    else:
        banco = {
            1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
            2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento por sobre cerrado?", "o": ["Sí", "No"], "k": "Sí"}
        }
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Su decisión legal:", banco[fase]['o'])
        if st.button("ENVIAR VOTO"):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([["-", st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

time.sleep(1); st.rerun()
