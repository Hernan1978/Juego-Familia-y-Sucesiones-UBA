import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden; display: none; }}
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85); 
            padding: 3rem 3rem; border-radius: 20px; border: 2px solid #D4AF37; margin-top: 50px;
        }}
        .reloj-container {{
            position: fixed !important; bottom: 30px !important; right: 30px !important; 
            background-color: #C0392B !important; color: white !important;
            padding: 15px 25px !important; border-radius: 50px !important; 
            border: 3px solid #D4AF37 !important; z-index: 999999 !important;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7); animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000; font-size: 1.3rem !important; }}
        .cartel-exito {{ 
            background-color: rgba(46, 204, 113, 0.4); border: 3px solid #2ECC71; 
            padding: 40px; border-radius: 15px; text-align: center; margin-top: 20px;
        }}
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; 
            height: 3.5rem; width: 100%; border: 1px solid #D4AF37;
        }}
        /* Estilo para la lista de participantes inferior */
        .lista-participantes {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 15px; border-radius: 10px; border: 1px solid #D4AF37;
            margin-top: 30px;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

def leer(n, d="0"): return open(n, "r").read().strip() if os.path.exists(n) else d
def escribir(n, v): open(n, "w").write(str(v))

# --- 2. PANEL DOCENTE ---
fase_actual = int(leer("fase.txt"))
tiempo_limite = leer("tiempo.txt", "OFF")

if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO DEL JUEZ")
        if st.text_input("Contraseña:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir("fase.txt", "0"); escribir("tiempo.txt", "OFF")
                st.session_state.clear(); st.rerun()
            st.write("---")
            f_sel = st.selectbox("Fase:", ["Sala de Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"], 
                                 index=fase_actual if fase_actual != 99 else 4)
            if st.button("LANZAR FASE"):
                nv = 0 if "Sala" in f_sel else (99 if "Podio" in f_sel else int(f_sel.split(" ")[1]))
                escribir("fase.txt", nv); escribir("tiempo.txt", "OFF"); st.rerun()
            if 0 < fase_actual < 99:
                seg = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR TIEMPO"):
                    escribir("tiempo.txt", time.time() + seg); st.rerun()

# --- 3. LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None
if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", index=False)
            df_login = pd.read_csv("data.csv")
            if df_login[(df_login['Email'] == m) & (df_login['Fase'] == 0)].empty:
                pd.DataFrame([[m, a, 0, 0]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.usuario = {"mail": m, "alias": a}; st.rerun()
    st.stop()

# --- 4. LÓGICA DE JUEGO ---
ya_voto_alumno = False
if os.path.exists("data.csv"):
    df_v = pd.read_csv("data.csv")
    ya_voto_alumno = not df_v[(df_v['Email'] == st.session_state.usuario['mail']) & (df_v['Fase'] == fase_actual)].empty

# RELOJ
if 0 < fase_actual < 99 and not ya_voto_alumno and tiempo_limite != "OFF":
    seg_restantes = int(float(tiempo_limite) - time.time())
    if seg_restantes > 0:
        st.markdown(f'<div class="reloj-container">⌛ {seg_restantes}s</div>', unsafe_allow_html=True)
    else:
        st.error("⚠️ TIEMPO AGOTADO."); time.sleep(1); st.rerun()

# CONTENIDO PRINCIPAL
if fase_actual == 0:
    st.header(f"🏛️
