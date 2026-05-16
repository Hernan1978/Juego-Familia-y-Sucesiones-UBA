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
        df = conn.read(ttl=0)
        df.columns = df.columns.str.strip().str.upper()
        
        # Asegurar que existan las columnas necesarias (Normalizadas a una letra)
        mapping = {"E": "E", "A": "A", "F": "F", "P": "P", "G": "G"}
        for col in mapping.keys():
            if col not in df.columns:
                df[col] = 0
        
        # Normalizar la columna E para buscar SISTEMA
        df["E_NORM"] = df["E"].astype(str).str.strip().str.upper()
        
        if accion == "escribir_sistema":
            if "SISTEMA" not in df["E_NORM"].values:
                nuevo_sys = pd.DataFrame([["SISTEMA", "CONTROL", int(fase), float(tiempo), "0"]], columns=["E", "A", "F", "P", "G"])
                df = pd.concat([df.drop(columns=["E_NORM"]), nuevo_sys], ignore_index=True)
            else:
                df.loc[df["E_NORM"] == "SISTEMA", "F"] = int(fase)
                df.loc[df["E_NORM"] == "SISTEMA", "P"] = float(tiempo)
                df = df.drop(columns=["E_NORM"])
            conn.update(data=df)
            return df
        
        if accion == "nuevo_usuario":
            if nuevo_usuario["E"] not in df["E"].astype(str).values:
                nuevo_df = pd.DataFrame([nuevo_usuario])
                df = pd.concat([df.drop(columns=["E_NORM"]), nuevo_df], ignore_index=True)
                conn.update(data=df)
            return df

        if accion == "sumar_puntos":
            df.loc[df["E_NORM"] == str(nuevo_usuario["e"]).upper(), "P"] = df.loc[df["E_NORM"] == str(nuevo_usuario["e"]).upper(), "P"].astype(float) + float(nuevo_usuario["pts"])
            df = df.drop(columns=["E_NORM"])
            conn.update(data=df)
            return df

        return df.drop(columns=["E_NORM"]) if "E_NORM" in df.columns else df
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return pd.DataFrame()

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

df_global = gestionar_datos()
if df_global.empty:
    st.warning("⏳ Conectando con la base de datos...")
    st.stop()

try:
    # Buscar SISTEMA sin importar mayúsculas/minúsculas
    info_sistema = df_global[df_global["E"].astype(str).str.strip().str.upper() == "SISTEMA"].iloc[0]
    fase_serv = int(info_sistema["F"])
    t_limite = float(info_sistema["P"])
except:
    st.error("❌ No se encontró la fila SISTEMA en la planilla. Agrégala manualmente en la Columna A.")
    st.stop()

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
            gestionar_datos("nuevo_usuario", nuevo_usuario={"E": m, "A": n, "F": 0, "P": 0.0, "G": g})
        else: st.error("Ingresa un Email válido.")
        st.rerun()
    st.stop()

# --- 5. LÓGICA ---
ahora = time.time()
fases_nombres = {0: "Inicio", 1: "P1", 2: "P2", 3: "P3", 4: "P4", 88: "Parcial", 99: "FINAL"}

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
            df_reset = df_global[df_global["E"].astype(str).str.strip().str.upper() == "SISTEMA"]
            conn.update(data=df_reset)
            st.rerun()
    
    st.table(df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))

else:
    # --- PANTALLA ALUMNO ---
    if fase_serv == 99:
        reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3")
        st.balloons(); st.snow()
        podio = df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"].sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            img_file = "alumna_festejo_uba.png" if podio[0][4] == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro'>🏆 {podio[0][4]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div><br>", unsafe_allow_html=True)
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
        st.table(df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))
        time.sleep(3)
        st.rerun()
            
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        st.table(df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))
        time.sleep(3)
        st.rerun()
