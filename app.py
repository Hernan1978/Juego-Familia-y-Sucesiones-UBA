import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ background-color: rgba(0, 0, 0, 0.85); padding: 2rem 3rem; border-radius: 20px; border: 2px solid #D4AF37; margin-top: 20px; }}
        .reloj-container {{
            position: fixed; bottom: 30px; right: 30px; background-color: #C0392B; color: white;
            padding: 15px 25px; border-radius: 50px; border: 3px solid #D4AF37; z-index: 1000;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7); animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; font-size: 1.3rem !important; }}
        .cartel-exito {{ 
            background-color: rgba(46, 204, 113, 0.2); border: 2px solid #2ECC71; 
            padding: 40px; border-radius: 15px; text-align: center; margin-top: 50px;
        }}
        .stButton>button {{ background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; height: 3.5rem; }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo escrito a máquina?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"}
}

# --- 3. FUNCIONES DE APOYO ---
def leer_archivo(nombre, default="0"):
    if not os.path.exists(nombre): return default
    with open(nombre, "r") as f: return f.read().strip()

def escribir_archivo(nombre, valor):
    with open(nombre, "w") as f: f.write(str(valor))

def ya_voto(mail, fase):
    if not os.path.exists("data.csv"): return False
    df = pd.read_csv("data.csv")
    return not df[(df['Email'] == mail) & (df['Fase'] == fase)].empty

# Limpieza automática de CSV si es viejo
if os.path.exists("data.csv"):
    df_temp = pd.read_csv("data.csv")
    if "Fase" not in df_temp.columns: os.remove("data.csv")

# --- 4. PANEL DOCENTE (?admin=true) ---
params = st.query_params
if params.get("admin") == "true":
    with st.sidebar:
        st.title("🛂 MANDO DEL JUEZ")
        clave = st.text_input("Contraseña:", type="password")
        if clave == "derecho2024":
            f_act = int(leer_archivo("fase.txt"))
            f_sel = st.selectbox("Cambiar fase:", ["Sala de Espera"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio Final"])
            if st.button("LANZAR FASE"):
                nueva = 0 if "Sala" in f_sel else (99 if "Podio" in f_sel else int(f_sel.split(" ")[1]))
                escribir_archivo("fase.txt", nueva)
                escribir_archivo("tiempo.txt", "OFF")
                st.rerun()
            
            if 0 < f_act < 99:
                seg = st.slider("Segundos:", 10, 40, 20)
                if st.button("⏱️ INICIAR TIEMPO"):
                    escribir_archivo("tiempo.txt", time.time() + seg)
                    st.rerun()
                
                st.write("### 📊 Monitor de Votos:")
                if os.path.exists("data.csv"):
                    df = pd.read_csv("data.csv")
                    # Todos los que están en la sesión (Fase 0)
                    integrantes = df[df['Fase'] == 0]['Alias'].unique()
                    for alu in integrantes:
                        voto = not df[(df['Alias'] == alu) & (df['Fase'] == f_act)].empty
                        st.write(f"{'✅' if voto else '⏳'} {alu}")
else:
    st.markdown("<style>[data-testid='collapsedControl'] {display: none;}</style>", unsafe_allow_html=True)

# --- 5. LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", index=False)
            if not ya_voto(m, 0):
                pd.DataFrame([[m, a, 0, 0]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
    st.stop()

# --- 6. DINÁMICA DEL JUEGO ---
fase = int(leer_archivo("fase.txt"))
tiempo_raw = leer_archivo("tiempo.txt", "OFF")

if fase == 0:
    st.header("🏛️ Sala de Audiencias")
    st.write(f"Bienvenido, letrado **{st.session_state.usuario['alias']}**.")
    st.info("Aguarde a que el Juez inicie la sesión...")
    time.sleep(4); st.rerun()

elif fase in banco:
    # SI YA VOTÓ: Pantalla de confirmación limpia
    if ya_voto(st.session_state.usuario['mail'], fase):
        st.markdown(f"""
            <div class="cartel-exito">
                <h1 style="color: #2ECC71 !important;">✔️ RESPUESTA ENVIADA</h1>
                <p>Su veredicto ha sido registrado con éxito.</p>
                <p style="font-size: 1.1rem !important; opacity: 0.8;">Aguarde a que el Juez cierre la ronda.</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(5); st.rerun()
    
    # SI NO HA VOTADO: Mostrar pregunta y reloj
    else:
        # Lógica de Reloj
        if tiempo_raw != "OFF":
            restante = int(float(tiempo_raw) - time.time())
            if restante > 0:
                st.markdown(f'<div class="reloj-container">⌛ {restante}s</div>', unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else:
                st.markdown('<div class="reloj-container">🚫 FIN</div>', unsafe_allow_html=True)
                st.error("TIEMPO AGOTADO. No se aceptan más veredictos.")
                st.stop()

        # Pregunta
        p = banco[fase]
        st.header(f"RONDA {fase}")
        st.write(f"### {p['q']}")
        rta = st.radio("Seleccione su veredicto:", p['op'], key=f"r{fase}")
        if st.button("ENVIAR VOTACIÓN"):
            pts = 100 if rta == p['ok'] else 0
            pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], fase, pts]], 
                         columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.rerun()

elif fase == 99:
    st.balloons()
    st.header("🏆 SENTENCIA FINAL")
    if os.path.exists("data.csv"):
        datos = pd.read_csv("data.csv")
        ranking = datos[datos['Fase'] > 0].groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        st.table(ranking)
