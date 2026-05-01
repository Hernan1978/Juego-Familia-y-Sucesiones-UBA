import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# INICIALIZACIÓN DE VARIABLES (Esto evita el AttributeError)
if 'u' not in st.session_state:
    st.session_state.u = None
if 'audio_ok' not in st.session_state:
    st.session_state.audio_ok = False

def play_audio(file_path):
    """Reproduce audio usando el componente oficial de Streamlit (más compatible)"""
    if os.path.exists(file_path):
        st.audio(file_path, format="audio/mp3", autoplay=True)

def aplicar_estilo():
    st.markdown("""
        <style>
        header, [data-testid="stHeader"] { visibility: hidden !important; }
        .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
        .main .block-container { 
            background: rgba(0, 0, 0, 0.94) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; border-radius: 20px !important; border: 2px solid #D4AF37;
        }
        h1, h2, h3, h4, p, label, span, .stMarkdown { 
            color: #FFFFFF !important; font-weight: 800 !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }
        .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-align: center; text-transform: uppercase; }
        .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; height: 3em !important; width: 100% !important; }
        .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }
        .usuario-badge { background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: right; margin-bottom: 20px; }
        .oro { color: #FFD700 !important; font-size: 4rem !important; text-shadow: 0 0 15px gold; text-align: center; margin: 0; }
        .plata { color: #C0C0C0 !important; font-size: 2.5rem !important; text-align: center; margin: 0; }
        .bronce { color: #CD7F32 !important; font-size: 2rem !important; text-align: center; margin: 0; }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P"])
    return pd.read_csv("d.csv", on_bad_lines='skip', engine='c')

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Seg:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()

# --- 4. ACCESO ---
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    
    if not st.session_state.audio_ok:
        st.write("### Bienvenido al Sistema de Sentencias")
        st.write("Para activar el sistema de audio y notificaciones, presione el botón:")
        if st.button("⚖️ ENTRAR AL TRIBUNAL"):
            st.session_state.audio_ok = True
            st.rerun()
    else:
        play_audio("bienvenida.mp3") 
        m_in = st.text_input("Email:")
        n_in = st.text_input("Nombre:")
        if st.button("INGRESAR") and m_in and n_in:
            h = not os.path.exists("d.csv")
            with open("d.csv", "a") as f:
                if h: f.write("E,A,F,P\n")
                f.write(f"{m_in.replace(',','')},{n_in.replace(',','')},0,0\n")
            st.session_state.u = {"e": m_in, "a": n_in}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE USUARIO ---
st.markdown(f"<div class='usuario-badge'>👤 Dr/a. <b>{st.session_state.u['a']}</b></div>", unsafe_allow_html=True)
ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write("Aguarde a que el Juez inicie la sesión.")

elif fase == 10:
    st.header("📊 POSICIONES ACTUALES")
    play_audio("votado.mp3")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False)
        idx = total.index.tolist()
        votos = total.values.tolist()
        
        # --- LÓGICA DE SONIDO DEL PODIO ---
        if st.session_state.u['a'] in idx:
            puesto = idx.index(st.session_state.u['a']) + 1
            if puesto <= 3:
                st.balloons()
                play_audio("ganador.mp3")
            else:
                play_audio("bart.mp3")
        else:
            play_audio("bart.mp3")
        # ----------------------------------

        st.markdown("<br>", unsafe_allow_html=True)
        if len(idx) >= 1: 
            st.markdown(f"<p class='oro'>🥇 {idx[0].upper()}</p><p style='text-align:center;'>{int(votos[0])} pts</p>", unsafe_allow_html=True)
        if len(idx) >= 2: 
            st.markdown(f"<p class='plata'>🥈 {idx[1]}</p><p style='text-align:center;'>{int(votos[1])} pts</p>", unsafe_allow_html=True)
        if len(idx) >= 3: 
            st.markdown(f"<p class='bronce'>🥉 {idx[2]}</p><p style='text-align:center;'>{int(votos[2])} pts</p>", unsafe_allow_html=True)

else:
    banco = {
        1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Cuál es el plazo para aceptar la herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    
    if ya_voto:
        st.success("✅ Veredicto registrado.")
        play_audio("votado.mp3")
    elif reloj_on:
        st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        play_audio("suspenso.mp3")
    
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=ya_voto or not reloj_on, key=f"v{fase}")
    
    if not ya_voto and st.button("RESPONDER", disabled=not reloj_on):
        correcta = (rta == banco[fase]['k'])
        pts = (100 + (max(0, int(t_limite - ahora)) * 2)) if correcta else 0
        with open("d.csv", "a") as f:
            f.write(f"{st.session_state.u['e']},{st.session_state.u['a']},{fase},{pts}\n")
        play_audio("exito.mp3" if correcta else "error.mp3")
        time.sleep(0.5)
        st.rerun()

# --- 7. REFRESH ---
time.sleep(1)
st.rerun()
