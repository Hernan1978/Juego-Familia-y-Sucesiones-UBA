import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTILO ORIGINAL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ background-color: rgba(0, 0, 0, 0.85); padding: 2rem 3rem; border-radius: 20px; border: 2px solid #D4AF37; margin-top: 20px; }}
        .reloj-container {{
            position: fixed; bottom: 30px; right: 30px; background-color: #C0392B; color: white;
            padding: 15px 25px; border-radius: 50px; border: 3px solid #D4AF37; z-index: 9999;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7); animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; font-size: 1.3rem !important; }}
        h1 {{ font-size: 3rem !important; }}
        .cartel-exito {{ 
            background-color: rgba(46, 204, 113, 0.2); border: 2px solid #2ECC71; 
            padding: 40px; border-radius: 15px; text-align: center; margin-top: 50px;
        }}
        .stButton>button {{ background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; height: 3.5rem; width: 100%; }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES DE PERSISTENCIA ---
def leer_archivo(nombre, default="0"):
    if not os.path.exists(nombre): return default
    with open(nombre, "r") as f: return f.read().strip()

def escribir_archivo(nombre, valor):
    with open(nombre, "w") as f: f.write(str(valor))

if 'ya_respondio' not in st.session_state:
    st.session_state.ya_respondio = False

# --- 3. PANEL DOCENTE ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("🛂 MANDO DEL JUEZ")
        clave = st.text_input("Contraseña:", type="password")
        if clave == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir_archivo("fase.txt", "0")
                escribir_archivo("tiempo.txt", "OFF")
                st.rerun()
            st.write("---")
            f_act = int(leer_archivo("fase.txt"))
            f_sel = st.selectbox("Fase:", ["Sala de Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"])
            if st.button("LANZAR FASE"):
                nueva = 0 if "Sala" in f_sel else (99 if "Podio" in f_sel else int(f_sel.split(" ")[1]))
                escribir_archivo("fase.txt", nueva)
                escribir_archivo("tiempo.txt", "OFF")
                st.session_state.ya_respondio = False # Reset local al cambiar fase
                st.rerun()
            if 0 < f_act < 99:
                seg = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR TIEMPO"):
                    escribir_archivo("tiempo.txt", time.time() + seg)
                    st.rerun()
                st.write("### 📊 Monitor:")
                if os.path.exists("data.csv"):
                    df = pd.read_csv("data.csv")
                    ints = df[df['Fase'] == 0]['Alias'].unique()
                    for alu in ints:
                        v = not df[(df['Alias'] == alu) & (df['Fase'] == f_act)].empty
                        st.write(f"{'✅' if v else '⏳'} {alu}")

# --- 4. LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None
if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", index=False)
            pd.DataFrame([[m, a, 0, 0]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.usuario = {"mail": m, "alias": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE JUEGO ---
fase = int(leer_archivo("fase.txt"))
tiempo_raw = leer_archivo("tiempo.txt", "OFF")

# Chequeo de voto (Archivo + Sesión)
voto_en_archivo = False
if os.path.exists("data.csv"):
    df_v = pd.read_csv("data.csv")
    voto_en_archivo = not df_v[(df_v['Email'] == st.session_state.usuario['mail']) & (df_v['Fase'] == fase)].empty

if fase == 0:
    st.header("🏛️ Sala de Audiencias")
    st.info("Aguarde el inicio de la sesión...")
    time.sleep(4); st.rerun()

elif fase == 99:
    st.balloons()
    st.header("🏆 SENTENCIA FINAL")
    df = pd.read_csv("data.csv")
    st.table(df[df['Fase'] > 0].groupby("Alias")["Puntos"].sum().sort_values(ascending=False))

else:
    # PANTALLA DE ÉXITO (Si ya votó, cortamos acá todo)
    if st.session_state.ya_respondio or voto_en_archivo:
        st.markdown(f"""<div class="cartel-exito"><h1 style="color: #2ECC71 !important;">✔️ RESPUESTA ENVIADA</h1>
                    <p>Su veredicto ha sido registrado. Espere al Juez.</p></div>""", unsafe_allow_html=True)
        time.sleep(5); st.rerun()
    
    # PANTALLA DE PREGUNTA
    else:
        # Reloj
        if tiempo_raw != "OFF":
            restante = int(float(tiempo_raw) - time.time())
            if restante > 0:
                st.markdown(f'<div class="reloj-container">⌛ {restante}s</div>', unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else:
                st.markdown('<div class="reloj-container">🚫 FIN</div>', unsafe_allow_html=True)
                st.error("TIEMPO AGOTADO.")
                st.stop()

        banco = {1: {"q": "¿Porción legítima?", "op": ["1/2", "2/3"], "ok": "2/3"},
                 2: {"q": "¿Plazo aceptación?", "op": ["10 años", "20 años"], "ok": "10 años"},
                 3: {"q": "¿Testamento ológrafo?", "op": ["Sí", "No"], "ok": "No"}}
        p = banco[fase]
        st.header(f"RONDA {fase}")
        st.write(f"### {p['q']}")
        rta = st.radio("Veredicto:", p['op'], key=f"r{fase}")
        if st.button("ENVIAR VOTACIÓN"):
            # GUARDAR E INMEDIATAMENTE MARCAR COMO RESPONDIDO
            pts = 100 if rta == p['ok'] else 0
            pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], fase, pts]], 
                         columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.ya_respondio = True
            st.rerun()
