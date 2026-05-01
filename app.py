import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

SOUNDS = {
    "exito": "https://www.myinstants.com/media/sounds/correct-answer.mp3",
    "error": "https://www.myinstants.com/media/sounds/eso-tuvo-que-doler-oficina.mp3",
    "ganador": "https://www.myinstants.com/media/sounds/tada_6.mp3"
}

def play_audio(url):
    st.components.v1.html(f"<audio autoplay><source src='{url}' type='audio/mp3'></audio>", height=0)

def aplicar_estilo():
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        .stApp {{ background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.94) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; border-radius: 20px !important; border: 2px solid #D4AF37;
        }}
        h1, h2, h3, h4, p, label, span, .stMarkdown {{ 
            color: #FFFFFF !important; font-weight: 800 !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        .titulo-oro {{ color: #D4AF37 !important; font-size: 3rem !important; text-align: center; text-transform: uppercase; margin-bottom: 20px; }}
        .stButton>button {{ background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; }}
        .reloj-juez {{ position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }}
        .usuario-badge {{ background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: right; margin-bottom: 20px; }}
        .oro {{ color: #FFD700 !important; font-size: 4rem !important; }}
        .plata {{ color: #C0C0C0 !important; font-size: 2.5rem !important; }}
        .bronce {{ color: #CD7F32 !important; font-size: 2rem !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE DATOS DE ALTA VELOCIDAD ---
COLUMNAS = ["E", "A", "F", "P"]

def leer_f():
    if os.path.exists("f.txt"):
        try:
            with open("f.txt", "r") as x: return x.read().strip().split(",")
        except: return ["0", "0"]
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=COLUMNAS)
    try:
        # on_bad_lines='skip' es vital aquí por si dos escrituras chocan un milisegundo
        df = pd.read_csv("d.csv", on_bad_lines='skip', engine='c')
        return df if all(col in df.columns for col in COLUMNAS) else pd.DataFrame(columns=COLUMNAS)
    except:
        return pd.DataFrame(columns=COLUMNAS)

# --- ESTADO INMEDIATO ---
f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ JUEZ - CONTROL DE SALA</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                escribir_f({"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}[sel], 0)
                st.rerun()
        with c2:
            dur = st.number_input("Tiempo (seg):", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        # Monitor Masivo de Inscriptos
        st.write("---")
        inscriptos_list = df_global[df_global["F"] == 0]["A"].unique() if not df_global.empty else []
        st.subheader(f"👥 Alumnos Presentes: {len(inscriptos_list)}")
        
        if 0 < fase < 10:
            votaron = df_global[df_global["F"] == fase]["A"].unique() if not df_global.empty else []
            faltan = [a for a in inscriptos_list if a not in votaron]
            m1, m2 = st.columns(2)
            m1.success(f"VOTARON ({len(votaron)})")
            m1.write(", ".join(votaron))
            m2.warning(f"FALTAN ({len(faltan)})")
            m2.write(", ".join(faltan))
        else:
            st.info(", ".join(inscriptos_list))
    st.write("---")

# --- 4. ACCESO ALUMNO ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m_in = st.text_input("Email:")
    n_in = st.text_input("Nombre:")
    if st.button("INGRESAR"):
        if m_in and n_in:
            # Escritura veloz para el ingreso
            headers = not os.path.exists("d.csv")
            with open("d.csv", "a") as f:
                if headers: f.write("E,A,F,P\n")
                f.write(f"{m_in.replace(',','')},{n_in.replace(',','')},0,0\n")
            st.session_state.u = {"e": m_in, "a": n_in}
            st.rerun()
    st.stop()

# --- 5. INTERFAZ ---
st.markdown(f"<div class='usuario-badge'>👤 Dr/a. <b>{st.session_state.u['a']}</b></div>", unsafe_allow_html=True)

ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write("Aguarde a que el Juez inicie la ronda.")

elif fase == 10:
    st.header("📊 POSICIONES ACTUALES")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(15)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    st.balloons(); play_audio(SOUNDS["ganador"])
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        idx = total.index.tolist()
        if len(idx) >= 1: st.markdown(f"<p class='oro' style='text-align:center;'>🥇 {idx[0].upper()}</p>", unsafe_allow_html=True)
        if len(idx) >= 2: st.markdown(f"<p class='plata' style='text-align:center;'>🥈 {idx[1]}</p>", unsafe_allow_html=True)
        if len(idx) >= 3: st.markdown(f"<p class='bronce' style='text-align:center;'>🥉 {idx[2]}</p>", unsafe_allow_html=True)

else:
    if reloj_on and not ya_voto:
        st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

    banco = {
        1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Cuál es el plazo para aceptar la herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=ya_voto or not reloj_on, key=f"r{fase}")
    
    if ya_voto:
        st.success("✅ Veredicto registrado. Aguarde...")
    else:
        # El botón solo se habilita si el reloj está activo.
        if st.button("RESPONDER", disabled=not reloj_on):
            t_rest = int(t_limite - ahora)
            pts = (100 + (max(0, t_rest) * 2)) if rta == banco[fase]['k'] else 0
            
            # ESCRITURA ATÓMICA: La más rápida de Python. 
            # 60 alumnos pueden hacer esto casi en simultáneo sin bloquearse.
            with open("d.csv", "a") as f:
                f.write(f"{st.session_state.u['e']},{st.session_state.u['a']},{fase},{pts}\n")
            
            play_audio(SOUNDS["exito"] if pts > 0 else SOUNDS["error"])
            st.rerun()

# Sincronización cada 1 segundo
time.sleep(1); st.rerun()
