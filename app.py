import streamlit as st
import pandas as pd
import time
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# ID DE SU PLANILLA INTEGRADO AUTOMÁTICAMENTE
GSHEET_ID = "1ZcXOkFeMgHZFchQfDKxPWaH516b7sO9LIiO9MibvP5Q"

# OPCIÓN A (Lectura directa por CSV público)
URL_LECTURA_DIRECTA = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:csv"

# OPCIÓN B (Para escribir y guardar puntos usando Apps Script sin usar tarjetas ni cuentas de servicio)
# Coloque aquí la URL que le dará Google tras seguir los pasos del final del mensaje:
URL_SCRIPT_GOOGLE = "https://script.google.com/macros/s/https://script.google.com/macros/s/AKfycbxP-nlxZgdHlDLwD1wZkoAzOYZtvO9e41F4-AiCCxpsy0EH5H8tdGeMZS2jx8roDkZewA/exec/exec"

def reproducir_audio(url):
    audio_html = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

def gestionar_datos(accion="leer", fase=None, tiempo=None, nuevo_usuario=None):
    # Intentamos primero interactuar con el Apps Script para sincronizar el Sheets real en vivo
    if URL_SCRIPT_GOOGLE and "ACA_VA_SU_ENLACE" not in URL_SCRIPT_GOOGLE:
        try:
            if accion == "leer":
                res = requests.get(URL_SCRIPT_GOOGLE, timeout=5)
                df = pd.DataFrame(res.json())
            else:
                payload = {"accion": accion, "fase": fase, "tiempo": tiempo, "usuario": nuevo_usuario}
                res = requests.post(URL_SCRIPT_GOOGLE, json=payload, timeout=5)
                df = pd.DataFrame(res.json())
            st.session_state.db_local = df
            return df
        except:
            pass # Si falla el script de Google, cae en el respaldo local interactivo automático

    # RESPALDO LOCAL INTERACTIVO: Esto hace que todos los botones de la app anden AL INSTANTE 
    # aunque Google Workspace tenga bloqueos en la red del aula.
    if "db_local" not in st.session_state:
        try:
            # Intenta leer la planilla real por HTTP público como base inicial
            df = pd.read_csv(URL_LECTURA_DIRECTA)
        except:
            # Estructura de contingencia si no hay internet en el aula al iniciar
            df = pd.DataFrame(columns=["E", "A", "F", "P", "G"])
        st.session_state.db_local = df

    df = st.session_state.db_local

    # Limpiar y normalizar columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    for col in ["E", "A", "F", "P", "G"]:
        if col not in df.columns: df[col] = ""
    df["E_STR"] = df["E"].astype(str).str.strip().str.upper()

    # Asegurar fila de control de SISTEMA
    if "SISTEMA" not in df["E_STR"].values:
        nuevo_sys = pd.DataFrame([["SISTEMA", "CONTROL", 0, 0.0, "0"]], columns=["E", "A", "F", "P", "G"])
        df = pd.concat([df, nuevo_sys], ignore_index=True)
        df["E_STR"] = df["E"].astype(str).str.strip().str.upper()

    # Procesar acciones de los botones interactivamente
    if accion == "escribir_sistema":
        df.loc[df["E_STR"] == "SISTEMA", "F"] = int(fase)
        df.loc[df["E_STR"] == "SISTEMA", "P"] = float(tiempo)
    elif accion == "nuevo_usuario":
        if nuevo_usuario["E"].strip().upper() not in df["E_STR"].values:
            df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    elif accion == "sumar_puntos":
        mask = df["E_STR"] == str(nuevo_usuario["e"]).strip().upper()
        df.loc[mask, "P"] = pd.to_numeric(df.loc[mask, "P"], errors='coerce').fillna(0) + float(nuevo_usuario["pts"])

    st.session_state.db_local = df.drop(columns=["E_STR"]) if "E_STR" in df.columns else df
    return st.session_state.db_local

# --- 2. ESTILOS DE VISIBILIDAD DE ALTA DEFINICIÓN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { 
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
        background-size: cover; 
        background-attachment: fixed; 
    }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, span { 
        font-family: 'Poppins', sans-serif; 
        text-align: center; 
    }
    
    h2, .stMarkdown h2 { 
        color: #FFFFFF !important; 
        font-size: 2.5rem !important; 
        font-weight: 800 !important; 
        text-shadow: 3px 3px 10px #000000 !important; 
    }
    
    .titulo-oro { 
        color: #FFFFFF !important; 
        font-size: 3.8rem !important; 
        font-weight: 800; 
        text-transform: uppercase; 
        text-shadow: 0 0 10px #D4AF37, 0 0 20px #D4AF37, 3px 3px 5px #000 !important; 
    }
    
    label, [data-testid="stWidgetLabel"] p, .stRadio label { 
        color: #FFFFFF !important; 
        font-weight: 800 !important; 
        font-size: 1.25rem !important; 
        text-shadow: 2px 2px 5px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important; 
    }
    
    .stSelectbox div[data-baseweb="select"], .stNumberInput input, div[data-testid="stSelectbox"] span {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        text-shadow: none !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stSelectbox"] p, div[data-testid="stNumberInput"] p {
        color: #000000 !important;
        text-shadow: none !important;
        font-weight: 700 !important;
    }

    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] b { 
        color: #000000 !important; 
        font-weight: 700 !important; 
        text-shadow: none !important; 
    }
    [data-testid="stTable"], .stTable, [data-testid="stExpander"], [data-testid="stDataFrame"] { 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        border-radius: 10px; 
    }
    
    .reloj-container { background-color: rgba(0, 0, 0, 0.8); color: #FF4B4B; font-size: 4rem; font-weight: 800; padding: 10px 30px; border-radius: 15px; border: 4px solid #FF4B4B; display: inline-block; margin: 20px 0; text-shadow: 0 0 10px #FF4B4B; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 800 !important; border: 2px solid #000 !important; width: 100%; text-shadow: none !important; }
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

df_global = gestionar_datos("leer")

try:
    info_sistema = df_global[df_global["E"].astype(str).str.strip().str.upper() == "SISTEMA"].iloc[0]
    fase_serv = int(info_sistema["F"])
    t_limite = float(info_sistema["P"])
except:
    fase_serv = 0
    t_limite = 0.0

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
            st.session_state.clear()
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
            time.sleep(3); st.rerun()
        elif reloj_on and not ya_envio:
            secs_restantes = int(t_limite - ahora)
            st.markdown(f"<div style='text-align:center;'><div class='reloj-container'>⏱️ {secs_restantes}s</div></div>", unsafe_allow_html=True)
            voto_bloqueado = False
            time.sleep(1); st.rerun()
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
        
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        st.table(df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))
            
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        st.table(df_global[df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))
        time.sleep(4); st.rerun()
