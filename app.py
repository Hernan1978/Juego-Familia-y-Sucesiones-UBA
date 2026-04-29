import streamlit as st
import pd
import os
import time

# --- 1. ESTÉTICA ---
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
            backdrop-filter: blur(10px); padding: 3rem !important; margin-top: 40px !important; border-radius: 15px !important;
        }}
        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold !important;
        }}
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 900 !important; border: none !important; width: 100%;
        }}
        /* Estilo para botón deshabilitado */
        .stButton>button:disabled {{
            background-color: #444444 !important; color: #888888 !important;
        }}
        .reloj-juez {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 20px 40px; border-radius: 15px;
            z-index: 99999; font-size: 4rem; font-family: 'Courier New', monospace;
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
    if os.path.exists("d.csv"): return pd.read_csv("d.csv")
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ MANDO DEL JUEZ")
    clave = st.text_input("Contraseña:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados", "Podio Final"])
            if st.button("ACTUALIZAR FASE"):
                mapa = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados":10, "Podio Final":99}
                escribir_f(mapa[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Segundos:", 5, 60, 15)
            if st.button("LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        if not df_global.empty:
            participantes = df_global[df_global["F"] == 0]["A"].unique()
            st.write(f"**👤 INTEGRANTES ({len(participantes)}):** " + ", ".join(participantes))
    st.write("---")

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ INGRESO AL TRIBUNAL")
    nombre = st.text_input("Nombre y Apellido:")
    if st.button("CONECTAR"):
        if nombre:
            pd.DataFrame([["-", nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"a": nombre}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE VOTACIÓN ---
voto_realizado = not df_global[(df_global["A"] == st.session_state.u["a"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
# EL BOTÓN SOLO SE HABILITA SI: La fase es de pregunta (1-9) Y el reloj está corriendo (t_limite > ahora) Y el usuario no votó.
reloj_activo = (t_limite > ahora)
habilita_voto = (0 < fase < 10) and reloj_activo and not voto_realizado

# --- 6. PANTALLAS ---
if habilita_voto:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Dr/a. **{st.session_state.u['a']}**, aguarde el inicio de la audiencia.")

elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        puntos = df_global[df_global["F"] < 10].groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(puntos)

elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA")
    st.balloons()
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum()
        ganador = total.idxmax()
        st.markdown(f"<h1 style='text-align: center; font-size: 5rem; color: #D4AF37;'>🥇 {ganador}</h1>", unsafe_allow_html=True)

else:
    st.header(f"RONDA N° {fase}")
    if voto_realizado:
        st.success("⚖️ Veredicto enviado. Aguarde resultados.")
    elif not reloj_activo:
        st.warning("⏳ Esperando que el Juez inicie el cronómetro...")
    
    banco = {
        1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento por sobre cerrado?", "o": ["Sí", "No"], "k": "Sí"}
    }
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Su decisión legal:", banco[fase]['o'], disabled=not habilita_voto)
    
    # EL BOTÓN VINCULADO AL RELOJ
    if st.button("ENVIAR VOTO", disabled=not habilita_voto):
        pts = 100 if rta == banco[fase]['k'] else 0
        pd.DataFrame([["-", st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        st.rerun()

time.sleep(1); st.rerun()
