import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y SONIDOS ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

SOUNDS = {
    "reloj": "https://www.soundjay.com/clock/sounds/clock-ticking-2.mp3",
    "exito": "https://www.myinstants.com/media/sounds/correct-answer.mp3",
    "error": "https://www.myinstants.com/media/sounds/eso-tuvo-que-doler-oficina.mp3",
    "ganador": "https://www.myinstants.com/media/sounds/tada_6.mp3"
}

def play_audio(url):
    st.components.v1.html(f"<audio autoplay><source src='{url}' type='audio/mp3'></audio>", height=0)

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; margin-top: 40px !important; border-radius: 20px !important;
            border: 1px solid rgba(212, 175, 55, 0.3);
        }}
        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold !important;
        }}
        .stButton>button {{ background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; height: 3.5rem; }}
        .reloj-juez {{ position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 4.5rem; font-family: 'Courier New', monospace; border: 4px solid #D4AF37; z-index: 9999; }}
        .oro {{ color: #FFD700 !important; font-size: 5rem !important; text-transform: uppercase; }}
        .plata {{ color: #C0C0C0 !important; font-size: 3.5rem !important; }}
        .bronce {{ color: #CD7F32 !important; font-size: 2.5rem !important; }}
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
        try: return pd.read_csv("d.csv")
        except: return pd.DataFrame(columns=["E","A","F","P"])
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ PANEL DE MANDO: JUEZ")
    clave = st.text_input("Clave de Acceso:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Cambiar Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("ACTUALIZAR ESTADO"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Reloj (seg):", 5, 60, 20)
            if st.button("LARGAR CRONÓMETRO"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()
        
        # LISTADO DE ALUMNOS (Panel Admin)
        st.write("---")
        st.subheader("👥 Alumnos Registrados en la Audiencia")
        if not df_global.empty:
            # Filtramos solo los registros de entrada (Fase 0)
            lista_alumnos = df_global[df_global["F"] == 0][["E", "A"]].drop_duplicates()
            st.table(lista_alumnos.rename(columns={"E": "Email Institucional", "A": "Nombre y Apellido"}))
        else:
            st.info("Esperando que los alumnos se conecten...")
    st.write("---")

# --- 4. REGISTRO DE USUARIO ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.title("🏛️ LEXPLAY UBA")
    st.write("Complete sus datos institucionales para participar:")
    mail = st.text_input("Email Institucional (@derecho.uba.ar):")
    nombre = st.text_input("Nombre y Apellido completo:")
    
    if st.button("INGRESAR A LA AUDIENCIA"):
        if mail and nombre:
            pd.DataFrame([[mail, nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": mail, "a": nombre}
            st.rerun()
        else:
            st.warning("Por favor, complete ambos campos.")
    st.stop()

# --- 5. LÓGICA DE JUEGO ---
voto_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)
puede_votar = (0 < fase < 10) and reloj_on and not voto_ok

if puede_votar:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
    play_audio(SOUNDS["reloj"])

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.info(f"Bienvenido/a Dr/a. {st.session_state.u['a']}. Aguarde el inicio de la ronda.")

elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        top = df_global[df_global["F"] < 10].groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA")
    st.balloons()
    play_audio(SOUNDS["ganador"])
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        res = total.index.tolist()
        if len(res) >= 1: st.markdown(f"<div style='text-align:center;'><p class='oro'>🥇 {res[0].upper()}</p></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if len(res) >= 2: c1.markdown(f"<div style='text-align:center;'><p class='plata'>🥈 {res[1]}</p></div>", unsafe_allow_html=True)
        if len(res) >= 3: c2.markdown(f"<div style='text-align:center;'><p class='bronce'>🥉 {res[2]}</p></div>", unsafe_allow_html=True)

else:
    st.header(f"RONDA N° {fase}")
    if voto_ok:
        st.success("✅ Dictamen registrado. Aguarde a que el Juez cierre la ronda.")
    elif not reloj_on:
        st.warning("⏳ Esperando que el Juez habilite el cronómetro...")
    
    banco = {
        1: {"q": "¿Cuál es la legítima de los descendientes en el CCCN?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿El testamento ológrafo puede ser escrito a máquina si se firma a mano?", "o": ["No", "Sí"], "k": "No"}
    }
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=not puede_votar)
    
    if st.button("ENVIAR VOTO", disabled=not puede_votar):
        pts = 100 if rta == banco[fase]['k'] else 0
        pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        if pts > 0: play_audio(SOUNDS["exito"])
        else: play_audio(SOUNDS["error"])
        st.rerun()

time.sleep(1)
st.rerun()
