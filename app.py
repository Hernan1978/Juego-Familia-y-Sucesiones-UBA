import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ background-color: rgba(0, 0, 0, 0.9); padding: 2rem 3rem; border-radius: 20px; border: 2px solid #D4AF37; margin-top: 20px; }}
        .reloj-container {{
            position: fixed; bottom: 30px; right: 30px; background-color: #C0392B; color: white;
            padding: 15px 25px; border-radius: 50px; border: 3px solid #D4AF37; z-index: 9999;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7); animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        .cartel-exito {{ 
            background-color: rgba(46, 204, 113, 0.2); border: 2px solid #2ECC71; 
            padding: 40px; border-radius: 15px; text-align: center; margin-top: 50px;
        }}
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; }}
        .stButton>button {{ background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; height: 3.5rem; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES DE ARCHIVOS ---
def leer_archivo(nombre, default="0"):
    if not os.path.exists(nombre): return default
    with open(nombre, "r") as f: return f.read().strip()

def escribir_archivo(nombre, valor):
    with open(nombre, "w") as f: f.write(str(valor))

# --- 3. ESTADO DE SESIÓN (Para frenar el reloj al instante) ---
if 'ha_votado_fase' not in st.session_state:
    st.session_state.ha_votado_fase = -1  # Guardamos qué fase ya votó

# --- 4. PANEL DOCENTE ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO DOCENTE")
        if st.text_input("Contraseña:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR CLASE"):
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
                st.rerun()
            if 0 < f_act < 99:
                seg = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR TIEMPO"):
                    escribir_archivo("tiempo.txt", time.time() + seg)
                    st.rerun()

# --- 5. LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO")
    m = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", index=False)
            pd.DataFrame([[m, a, 0, 0]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
    st.stop()

# --- 6. DINÁMICA DE JUEGO ---
fase = int(leer_archivo("fase.txt"))
tiempo_raw = leer_archivo("tiempo.txt", "OFF")

# SI CAMBIÓ LA FASE, RESETEAMOS EL BLOQUEO LOCAL
if st.session_state.ha_votado_fase != fase:
    # Solo reseteamos si es una fase nueva de pregunta
    pass

if fase == 0:
    st.header("🏛️ Sala de Audiencias")
    st.info("Esperando inicio...")
    time.sleep(3); st.rerun()

elif fase == 99:
    st.balloons()
    st.header("🏆 PODIO FINAL")
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        st.table(df[df['Fase'] > 0].groupby("Alias")["Puntos"].sum().sort_values(ascending=False))

else:
    # --- LÓGICA DE PREGUNTAS ---
    # PRIMERO: ¿Votó en esta sesión o en el archivo?
    # Chequeamos archivo por si refresca la página
    df_v = pd.read_csv("data.csv") if os.path.exists("data.csv") else pd.DataFrame()
    ya_registrado = False
    if not df_v.empty:
        ya_registrado = not df_v[(df_v['Email'] == st.session_state.usuario['mail']) & (df_v['Fase'] == fase)].empty

    if st.session_state.ha_votado_fase == fase or ya_registrado:
        st.markdown(f"""<div class="cartel-exito"><h1>✔️ ENVIADO</h1><p>Voto registrado. Esperá al Juez.</p></div>""", unsafe_allow_html=True)
        time.sleep(5); st.rerun()
    
    else:
        # RELOJ (Solo si no votó)
        if tiempo_raw != "OFF":
            restante = int(float(tiempo_raw) - time.time())
            if restante > 0:
                st.markdown(f'<div class="reloj-container">⌛ {restante}s</div>', unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else:
                st.error("¡TIEMPO AGOTADO!")
                st.stop()

        # PREGUNTA
        banco = {1: {"q": "¿Porción legítima?", "op": ["1/2", "2/3"], "ok": "2/3"},
                 2: {"q": "¿Plazo aceptación?", "op": ["10 años", "20 años"], "ok": "10 años"},
                 3: {"q": "¿Testamento ológrafo?", "op": ["Sí", "No"], "ok": "No"}}
        
        p = banco[fase]
        st.header(f"Ronda {fase}")
        st.write(f"### {p['q']}")
        rta = st.radio("Veredicto:", p['op'], key=f"r{fase}")
        
        if st.button("ENVIAR VOTACIÓN"):
            # BLOQUEO INSTANTÁNEO
            st.session_state.ha_votado_fase = fase 
            # GUARDAR
            pts = 100 if rta == p['ok'] else 0
            pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], fase, pts]], 
                         columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.rerun()
