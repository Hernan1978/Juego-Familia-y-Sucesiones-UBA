import streamlit as st
import pandas as pd
import sqlite3
import time
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def reproducir_audio(url):
    audio_html = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# GESTIÓN DE BASE DE DATOS SQLITE
def init_db():
    conn = sqlite3.connect('lexplay.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sistema (id INTEGER PRIMARY KEY, fase INTEGER, tiempo REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alumnos (email TEXT PRIMARY KEY, nombre TEXT, puntos REAL, titulo TEXT)''')
    c.execute('''INSERT OR IGNORE INTO sistema (id, fase, tiempo) VALUES (1, 0, 0.0)''')
    conn.commit()
    return conn

db_conn = init_db()

def leer_sistema():
    c = db_conn.cursor()
    c.execute('SELECT fase, tiempo FROM sistema WHERE id=1')
    return c.fetchone()

def escribir_sistema(f, t):
    c = db_conn.cursor()
    c.execute('UPDATE sistema SET fase=?, tiempo=? WHERE id=1', (f, t))
    db_conn.commit()

def cargar_alumnos():
    return pd.read_sql('SELECT titulo as G, nombre as A, puntos as P, email as E FROM alumnos ORDER BY puntos DESC', db_conn)

def guardar_alumno(e, a, g):
    c = db_conn.cursor()
    c.execute('INSERT OR IGNORE INTO alumnos (email, nombre, puntos, titulo) VALUES (?, ?, 0.0, ?)', (e, a, g))
    db_conn.commit()

def sumar_puntos(e, pts):
    c = db_conn.cursor()
    c.execute('UPDATE alumnos SET puntos = puntos + ? WHERE email = ?', (pts, e))
    db_conn.commit()

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, span { font-family: 'Poppins', sans-serif; text-align: center; }
    h2, .stMarkdown h2 { color: #FFFFFF !important; font-size: 2.5rem !important; font-weight: 800 !important; text-shadow: 3px 3px 10px #000000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000 !important; }
    .titulo-oro { color: #FFFFFF !important; font-size: 3.8rem !important; font-weight: 800; text-transform: uppercase; text-shadow: 0 0 10px #D4AF37, 0 0 20px #D4AF37, 3px 3px 5px #000 !important; }
    label, [data-testid="stWidgetLabel"] p, .stSelectbox label, .stNumberInput label, .stRadio label, [data-testid="stMarkdownContainer"] p { color: #CCFF00 !important; font-weight: 800 !important; font-size: 1.2rem !important; text-shadow: 2px 2px 4px #000 !important; }
    .reloj-container { background-color: rgba(0, 0, 0, 0.8); color: #FF4B4B; font-size: 4rem; font-weight: 800; padding: 10px 30px; border-radius: 15px; border: 4px solid #FF4B4B; display: inline-block; margin: 20px 0; text-shadow: 0 0 10px #FF4B4B; }
    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] b { color: #FFFFFF !important; font-weight: 600 !important; text-shadow: 1px 1px 2px #000000 !important; }
    [data-testid="stTable"], .stTable, [data-testid="stExpander"] { background-color: rgba(0, 0, 0, 0.6) !important; border-radius: 10px; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 800 !important; border: 2px solid #000 !important; width: 100%; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #FFF !important; padding: 25px; border-radius: 15px; width: 85%; font-size: 2.5rem; font-weight: 800; border: 4px solid #FFF; text-shadow: 2px 2px 5px #000 !important; margin: auto; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #FFF !important; padding: 15px; border-radius: 12px; width: 75%; font-size: 1.8rem; font-weight: 700; margin: auto; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #FFF !important; padding: 12px; border-radius: 10px; width: 65%; font-size: 1.5rem; font-weight: 700; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BANCO ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. ACCESO ---
if 'user' not in st.session_state: st.session_state.user = None
if 'f_voto' not in st.session_state: st.session_state.f_voto = -1

if st.session_state.user is None:
    reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/bienvenida.mp3")
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email de Acceso (Alumnos) o Clave (Docente):")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m == "derecho2024": 
            st.session_state.user = {"tipo": "juez"}
            st.rerun()
        elif "@" in m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            guardar_alumno(m, n, g)
            st.rerun()
        else: st.error("Ingresa un Email válido y tu Nombre.")
    st.stop()

# --- 5. LÓGICA ---
fase_serv, t_limite = leer_sistema()
df_global = cargar_alumnos()
ahora = time.time()
fases_nombres = {0: "Inicio", 1: "P1", 2: "P2", 3: "P3", 4: "P4", 88: "Parcial", 99: "FINAL"}

if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    with st.expander("📚 VER PREGUNTAS Y AUDIENCIA", expanded=False):
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("<b>Banco:</b>", unsafe_allow_html=True)
            for k,v in banco.items(): st.write(f"**{k}.** {v['q']}")
        with c_p2:
            st.markdown("<b>Alumnos en Sala:</b>", unsafe_allow_html=True)
            st.table(df_global[['G', 'A']])

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_fase = st.selectbox("Cambiar Pregunta:", options=list(fases_nombres.keys()), format_func=lambda x: fases_nombres[x], key="sel_fase")
        if st.button("📢 ACTUALIZAR FASE"):
            escribir_sistema(op_fase, 0.0)
            st.rerun()
    with c2:
        t_set = st.number_input("Segundos:", 5, 60, 25)
        if st.button("⏱️ INICIAR RELOJ"):
            escribir_sistema(fase_serv, time.time() + t_set)
            st.rerun()
    with c3:
        if st.button("🔄 REFRESCAR"): st.rerun()
    with c4:
        if st.button("⚠️ RESET"):
            c = db_conn.cursor()
            c.execute('DELETE FROM alumnos')
            db_conn.commit()
            escribir_sistema(0, 0.0)
            st.rerun()
    
    st.table(df_global[['G', 'A', 'P']].sort_values(by='P', ascending=False))

else:
    # --- PANTALLA ALUMNO ---
    if fase_serv == 99:
        reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3")
        st.balloons(); st.snow()
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            genero_ganador = podio[0][0]
            img_file = "alumna_festejo_uba.png" if genero_ganador == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro'>🏆 {podio[0][0]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][2])} PTS)</div><br>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]}</div><br>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]}</div>", unsafe_allow_html=True)
            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.user = None
                st.rerun()
    elif fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora
        ya_envio = st.session_state.get('enviado', False)
        if st.session_state.f_voto != fase_serv: st.session_state.enviado = False
        
        st.markdown(f"## {p['q']}")
        
        # CONTENEDOR PARA EL RELOJ (EVITA TITILEO)
        reloj_placeholder = st.empty()
        
        if t_limite == 0:
            st.warning("⚖️ El Tribunal aún no ha habilitado la votación. Espere...")
            voto_bloqueado = True
        elif reloj_on and not ya_envio:
            voto_bloqueado = False
        elif not ya_envio and not reloj_on:
            reloj_placeholder.markdown("<div style='text-align:center;'><div class='reloj-container' style='color:gray; border-color:gray;'>⌛ TIEMPO AGOTADO</div></div>", unsafe_allow_html=True)
            voto_bloqueado = True
        else:
            voto_bloqueado = True

        # LAS OPCIONES SE QUEDAN QUIETAS
        opcion = st.radio("Dictamen:", p["o"], disabled=voto_bloqueado or ya_envio)
        
        if st.button("ENVIAR SENTENCIA", disabled=voto_bloqueado or ya_envio):
            if opcion == p["k"]:
                reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/exito.mp3")
                pts = 10 + min(int(t_limite - ahora), 10)
                sumar_puntos(st.session_state.user['e'], pts)
                st.success("✅ REGISTRADO")
            else:
                reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/error.mp3")
                st.error("❌ INCORRECTO")
            st.session_state.enviado = True
            st.session_state.f_voto = fase_serv
            st.rerun()
        
        if ya_envio:
            st.info("✅ Sentencia enviada correctamente.")

        # SOLO EL RELOJ SE ACTUALIZA CADA SEGUNDO
        if reloj_on and not ya_envio:
            while time.time() < t_limite:
                secs = int(t_limite - time.time())
                reloj_placeholder.markdown(f"<div style='text-align:center;'><div class='reloj-container'>⏱️ {secs}s</div></div>", unsafe_allow_html=True)
                time.sleep(1)
            st.rerun()
            
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        time.sleep(3)
        st.rerun()
