import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def reproducir_audio(url):
    audio_html = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

def gestionar_datos(accion="leer", fase=None, tiempo=None, nuevo_usuario=None):
    try:
        # Leer las 3 pestañas
        df_sis = conn.read(worksheet="SISTEMA", ttl=0)
        df_pre = conn.read(worksheet="PREGUNTAS", ttl=0)
        df_alu = conn.read(worksheet="ALUMNOS", ttl=0)
        
        if accion == "escribir_sistema":
            df_sis.loc[0, "FASE"] = int(fase)
            df_sis.loc[0, "TIEMPO"] = float(tiempo)
            conn.update(worksheet="SISTEMA", data=df_sis)
            return df_sis, df_pre, df_alu
        
        if accion == "nuevo_usuario":
            if nuevo_usuario["EMAIL"] not in df_alu["EMAIL"].astype(str).values:
                nuevo_df = pd.DataFrame([nuevo_usuario])
                df_alu = pd.concat([df_alu, nuevo_df], ignore_index=True)
                conn.update(worksheet="ALUMNOS", data=df_alu)
            return df_sis, df_pre, df_alu

        if accion == "sumar_puntos":
            mask = df_alu["EMAIL"].astype(str) == str(nuevo_usuario["e"])
            df_alu.loc[mask, "PUNTOS"] = df_alu.loc[mask, "PUNTOS"].astype(float) + float(nuevo_usuario["pts"])
            conn.update(worksheet="ALUMNOS", data=df_alu)
            return df_sis, df_pre, df_alu

        return df_sis, df_pre, df_alu
    except Exception as e:
        st.error(f"Error de conexión con las pestañas: {e}. Asegúrate de tener las pestañas SISTEMA, PREGUNTAS y ALUMNOS.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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

# --- 4. ACCESO ---
if 'user' not in st.session_state: st.session_state.user = None
if 'f_voto' not in st.session_state: st.session_state.f_voto = -1

df_sis, df_pre, df_alu = gestionar_datos()
if df_sis.empty:
    st.warning("⏳ Conectando con las pestañas del Excel...")
    st.stop()

fase_serv = int(df_sis.loc[0, "FASE"])
t_limite = float(df_sis.loc[0, "TIEMPO"])

if st.session_state.user is None:
    reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/bienvenida.mp3")
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email de Acceso (Alumnos) o Clave (Docente):")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m == "derecho2024": st.session_state.user = {"tipo": "juez"}
        elif "@" in m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            gestionar_datos("nuevo_usuario", nuevo_usuario={"EMAIL": m, "NOMBRE": n, "PUNTOS": 0.0, "TITULO": g})
        else: st.error("Ingresa un Email válido.")
        st.rerun()
    st.stop()

# --- 5. LÓGICA ---
ahora = time.time()
banco = {row["ID"]: {"q": row["PREGUNTA"], "o": str(row["OPCIONES"]).split(", "), "k": str(row["CORRECTA"])} for _, row in df_pre.iterrows()}
fases_nombres = {0: "Inicio", **{int(k): f"P{k}" for k in banco.keys()}, 88: "Parcial", 99: "FINAL"}

if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_fase = st.selectbox("Cambiar Pregunta:", options=list(fases_nombres.keys()), format_func=lambda x: fases_nombres[x], key="sel_fase")
        if st.button("📢 ACTUALIZAR FASE"):
            gestionar_datos("escribir_sistema", fase=op_fase, tiempo=0.0)
            st.rerun()
    with c2:
        t_set = st.number_input("Segundos:", 5, 60, 25)
        if st.button("⏱️ INICIAR RELOJ"):
            gestionar_datos("escribir_sistema", fase=fase_serv, tiempo=time.time() + t_set)
            st.rerun()
    with c3:
        if st.button("🔄 REFRESCAR"): st.rerun()
    with c4:
        if st.button("⚠️ RESET"):
            df_alu_reset = pd.DataFrame(columns=["EMAIL", "NOMBRE", "PUNTOS", "TITULO"])
            conn.update(worksheet="ALUMNOS", data=df_alu_reset)
            gestionar_datos("escribir_sistema", fase=0, tiempo=0.0)
            st.rerun()
    
    st.table(df_alu[['TITULO', 'NOMBRE', 'PUNTOS']].sort_values(by='PUNTOS', ascending=False))

else:
    # --- PANTALLA ALUMNO ---
    if fase_serv == 99:
        reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3")
        st.balloons(); st.snow()
        podio = df_alu.sort_values(by="PUNTOS", ascending=False).head(3).values.tolist()
        if podio:
            img_file = "alumna_festejo_uba.png" if podio[0][3] == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro'>🏆 {podio[0][3]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
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
        
        if t_limite == 0:
            st.warning("⚖️ El Tribunal aún no ha habilitado la votación. Espere...")
            voto_bloqueado = True
        elif reloj_on and not ya_envio:
            secs_restantes = int(t_limite - ahora)
            st.markdown(f"<div style='text-align:center;'><div class='reloj-container'>⏱️ {secs_restantes}s</div></div>", unsafe_allow_html=True)
            voto_bloqueado = False
            time.sleep(1)
            st.rerun()
        elif not ya_envio and not reloj_on:
            st.markdown("<div style='text-align:center;'><div class='reloj-container' style='color:gray; border-color:gray;'>⌛ TIEMPO AGOTADO</div></div>", unsafe_allow_html=True)
            voto_bloqueado = True
        else:
            voto_bloqueado = True

        opcion = st.radio("Dictamen:", p["o"], disabled=voto_bloqueado or ya_envio)
        
        if st.button("ENVIAR SENTENCIA", disabled=voto_bloqueado or ya_envio):
            if opcion == p["k"]:
                reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/exito.mp3")
                pts = 10 + min(int(t_limite - ahora), 10)
                gestionar_datos("sumar_puntos", nuevo_usuario={"e": st.session_state.user['e'], "pts": pts})
                st.success("✅ REGISTRADO")
            else:
                reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/error.mp3")
                st.error("❌ INCORRECTO")
            st.session_state.enviado = True
            st.session_state.f_voto = fase_serv
            st.rerun()
        
        # TABLA DE PARTICIPANTES PARA ALUMNOS
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        st.table(df_alu[['TITULO', 'NOMBRE', 'PUNTOS']].sort_values(by='PUNTOS', ascending=False))
        time.sleep(3)
        st.rerun()
            
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        st.table(df_alu[['TITULO', 'NOMBRE', 'PUNTOS']].sort_values(by='PUNTOS', ascending=False))
        time.sleep(3)
        st.rerun()
