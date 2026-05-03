import streamlit as st
import pandas as pd
import os
import time
import base64
import requests

# --- 1. FUNCIÓN DE AUDIO ---
def play_audio(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN Y URL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbw2lL020VODloofb-og7k7ERWXBYo5oa3axf5fRkX_e3JgA7lLs9PObfxHWw-T88lg_/exec"

if 'u' not in st.session_state: st.session_state.u = None
if 'audio_ok' not in st.session_state: st.session_state.audio_ok = False

# --- 3. GESTIÓN DE DATOS ---
def cargar_datos():
    cols = ["E", "A", "F", "P"]
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv("d.csv", on_bad_lines='skip', engine='c')
        for c in cols:
            if c not in df.columns: df[c] = None
        return df
    except: return pd.DataFrame(columns=cols)

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

def aplicar_estilo():
    st.markdown("""
        <style>
        /* BLOQUEO TOTAL DE INTERFAZ ESTÁNDAR */
        header, [data-testid="stHeader"], [data-testid="stToolbar"], .st-emotion-cache-zq59db {
            display: none !important;
            visibility: hidden !important;
        }
        
        .stApp { 
            background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
            background-size: cover; 
            background-attachment: fixed; 
        }
        
        /* CENTRADO DEL CONTENEDOR PRINCIPAL */
        .main .block-container { 
            background: rgba(0, 0, 0, 0.92) !important; 
            backdrop-filter: blur(15px); 
            padding: 2rem !important; 
            border-radius: 20px !important; 
            border: 2px solid #D4AF37; 
            max-width: 900px !important; /* Limita el ancho para que se vea como un cuadro central */
            margin: 20px auto !important; /* MARGEN AUTO PARA CENTRAR HORIZONTALMENTE */
            float: none !important;
        }

        h1, h2, h3, h4, p, label, span, .stMarkdown { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center !important; }
        .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-align: center; text-transform: uppercase; }
        .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; }
        
        /* PODIO ESTILO JUZGADO */
        .podio-wrapper {
            display: block;
            text-align: center;
            width: 100%;
            margin-top: 0px;
        }
        .sentencia-final-titulo { color: #D4AF37 !important; font-size: 4rem !important; text-transform: uppercase; font-weight: 900 !important; margin-bottom: 20px; }
        .oro-podio { color: #FFD700 !important; font-size: 5rem !important; text-shadow: 0 0 30px gold; font-weight: 900 !important; margin: 10px 0; }
        .plata-podio { color: #C0C0C0 !important; font-size: 3.5rem !important; text-shadow: 0 0 15px silver; margin: 10px 0; }
        .bronce-podio { color: #CD7F32 !important; font-size: 2.8rem !important; margin: 10px 0; }
        
        .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }
        .usuario-badge { background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: center !important; margin-bottom: 20px; }
        
        .lista-competencia {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #D4AF37;
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 4. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        inscriptos_list = df_global["A"].unique() if not df_global.empty else []
        st.write(f"### 👥 Alumnos en sala: {len(inscriptos_list)}")
        col1, col2, col3 = st.columns(3)
        with col1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + t_set); st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
    st.divider()

# --- 5. ACCESO ---
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    if not st.session_state.audio_ok:
        if st.button("⚖️ ENTRAR AL TRIBUNAL"):
            st.session_state.audio_ok = True; st.rerun()
    else:
        play_audio("bienvenida.mp3") 
        m_in = st.text_input("Email Académico:")
        n_in = st.text_input("Nombre y Apellido:")
        if st.button("INGRESAR") and m_in and n_in:
            e_l, n_l = m_in.strip().lower(), n_in.strip().replace(',', '')
            if not os.path.exists("d.csv"): 
                with open("d.csv", "w") as f: f.write("E,A,F,P\n")
            with open("d.csv", "a") as f: f.write(f"{e_l},{n_l},0,0\n")
            try: requests.get(f"{URL_APPS_SCRIPT}?email={e_l}", timeout=5)
            except: pass
            st.session_state.u = {"e": e_l, "a": n_l}; st.rerun()
    st.stop()

# --- 6. JUEGO ---
st.markdown(f"<div class='usuario-badge'>👤 Dr/a. <b>{st.session_state.u['a']}</b></div>", unsafe_allow_html=True)
ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.markdown('<div class="lista-competencia">', unsafe_allow_html=True)
    st.subheader("👥 POSTULANTES EN SALA")
    if not df_global.empty:
        nombres = df_global["A"].unique()
        st.write(", ".join(nombres))
    else:
        st.write("Esperando colegas...")
    st.markdown('</div>', unsafe_allow_html=True)

elif fase == 10:
    st.header("📊 POSICIONES ACTUALES")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)
        
elif fase == 99:
    # --- PODIO CENTRADO ARRIBA ---
    st.markdown('<div class="podio-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="sentencia-final-titulo">🏆 SENTENCIA FINAL</div>', unsafe_allow_html=True)
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False)
        idx, votos = total.index.tolist(), total.values.tolist()
        if st.session_state.u['a'] in idx:
            if idx.index(st.session_state.u['a']) < 3:
                st.balloons(); play_audio("ganador.mp3")
            else: play_audio("bart.mp3")
        if len(idx) >= 1: st.markdown(f'<div class="oro-podio">🥇 {idx[0].upper()} ({int(votos[0])} pts)</div>', unsafe_allow_html=True)
        if len(idx) >= 2: st.markdown(f'<div class="plata-podio">🥈 {idx[1]} ({int(votos[1])} pts)</div>', unsafe_allow_html=True)
        if len(idx) >= 3: st.markdown(f'<div class="bronce-podio">🥉 {idx[2]} ({int(votos[2])} pts)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    banco = {1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
             2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
             3: {"q": "¿Válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"}}
    if ya_voto:
        st.success("✅ Veredicto registrado."); play_audio("votado.mp3")
    elif reloj_on:
        st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        if int(t_limite - ahora) > 10: play_audio("suspenso.mp3")
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=ya_voto or not reloj_on, key=f"v{fase}")
    if not ya_voto and st.button("RESPONDER", disabled=not reloj_on):
        correcta = (rta == banco[fase]['k'])
        pts = (100 + int(t_limite - ahora)*2) if correcta else 0
        with open("d.csv", "a") as f: f.write(f"{st.session_state.u['e']},{st.session_state.u['a']},{fase},{pts}\n")
        time.sleep(0.5); st.rerun()

time.sleep(1)
st.rerun()
