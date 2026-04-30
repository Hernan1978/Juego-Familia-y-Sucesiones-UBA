import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
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
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; margin-top: 40px !important; 
            border-radius: 20px !important; border: 1px solid rgba(212, 175, 55, 0.4);
        }}
        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        .stButton>button {{ background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; height: 3.5rem; }}
        .reloj-juez {{ position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 4.5rem; border: 4px solid #D4AF37; z-index: 9999; }}
        .oro {{ color: #FFD700 !important; font-size: 5rem !important; text-transform: uppercase; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE ARCHIVOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if os.path.exists("d.csv"): 
        try: return pd.read_csv("d.csv", on_bad_lines='skip')
        except: return pd.DataFrame(columns=["E","A","F","P"])
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR (EL MONITOR) ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ MONITOR DE AUDIENCIA EN VIVO")
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("ACTUALIZAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Segundos:", 5, 60, 20)
            if st.button("LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()

        # EL MONITOR EN TIEMPO REAL
        if 0 < fase < 10:
            st.write("---")
            st.subheader(f"🗳️ Control de Votos: Ronda {fase}")
            if not df_global.empty:
                alumnos_total = df_global[df_global["F"] == 0]["A"].unique()
                votos_ronda = df_global[df_global["F"] == fase]["A"].unique()
                faltan = [a for a in alumnos_total if a not in votos_ronda]
                
                m1, m2 = st.columns(2)
                m1.success(f"**VOTARON ({len(votos_ronda)}):**\n" + "\n".join([f"✅ {x}" for x in votos_ronda]))
                m2.warning(f"**FALTAN ({len(faltan)}):**\n" + "\n".join([f"⏳ {x}" for x in faltan]))
    st.write("---")

# --- 4. ACCESO ALUMNO ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.title("🏛️ LEXPLAY UBA")
    mail = st.text_input("Email Institucional:")
    nombre = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR"):
        if mail and nombre:
            pd.DataFrame([[mail, nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": mail, "a": nombre}
            st.rerun()
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
    st.info(f"Dr/a. {st.session_state.u['a']}, aguarde a que el Juez inicie el debate.")

elif fase == 10:
    st.header("📊 POSICIONES ACTUALES")
    if not df_global.empty:
        # Sumamos todos los puntos acumulados hasta ahora
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA")
    st.balloons(); play_audio(SOUNDS["ganador"])
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        res = total.index.tolist()
        if len(res) >= 1: st.markdown(f"<div style='text-align:center;'><p class='oro'>🥇 {res[0].upper()}</p></div>", unsafe_allow_html=True)
        # Plata y Bronce sutiles debajo
        c1, c2 = st.columns(2)
        if len(res) >= 2: c1.markdown(f"<p style='text-align:center; color:#C0C0C0; font-size:2rem;'>🥈 {res[1]}</p>", unsafe_allow_html=True)
        if len(res) >= 3: c2.markdown(f"<p style='text-align:center; color:#CD7F32; font-size:2rem;'>🥉 {res[2]}</p>", unsafe_allow_html=True)

else:
    st.header(f"RONDA N° {fase}")
    if voto_ok:
        st.success("⚖️ Veredicto enviado. Aguarde a que el Juez cierre el acta para ver resultados.")
    elif not reloj_on:
        st.warning("⏳ Esperando que el Juez habilite el cronómetro para recibir su dictamen...")
    
    banco = {
        1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Válido testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=not puede_votar)
    
    if st.button("DICTAMINAR", disabled=not puede_votar):
        t_restante = int(t_limite - ahora)
        # Cálculo de puntos: 100 base + bono de velocidad
        puntos = (100 + (t_restante * 2)) if rta == banco[fase]['k'] else 0
        
        pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, puntos]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        play_audio(SOUNDS["exito"] if puntos > 0 else SOUNDS["error"])
        st.rerun()

time.sleep(1); st.rerun()
