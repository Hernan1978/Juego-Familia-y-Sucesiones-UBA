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

# TU LINK DE GOOGLE APPS SCRIPT (Asegurate que termine en /exec)
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbw2lL020VODloofb-og7k7ERWXBYo5oa3axf5fRkX_e3JgA7lLs9PObfxHWw-T88lg_/exec"

if 'u' not in st.session_state: st.session_state.u = None
if 'audio_ok' not in st.session_state: st.session_state.audio_ok = False

# --- 3. GESTIÓN DE DATOS ---
def cargar_datos():
    cols = ["E", "A", "F", "P"]
    if not os.path.exists("d.csv"): 
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv("d.csv", on_bad_lines='skip', engine='c')
        for c in cols:
            if c not in df.columns: df[c] = None
        return df
    except:
        return pd.DataFrame(columns=cols)

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# INICIALIZAMOS VARIABLES
f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

def aplicar_estilo():
    st.markdown("""
        <style>
        header, [data-testid="stHeader"] { visibility: hidden !important; }
        .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
        .main .block-container { background: rgba(0, 0, 0, 0.94) !important; backdrop-filter: blur(15px); padding: 3rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; }
        h1, h2, h3, h4, p, label, span, .stMarkdown { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; }
        .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-align: center; text-transform: uppercase; }
        .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; border: 2px solid #FFFFFF !important; width: 100% !important; }
        .reloj-juez { position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 5rem; border: 4px solid #D4AF37; z-index: 9999; }
        .usuario-badge { background: rgba(212, 175, 55, 0.2); padding: 10px 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: right; margin-bottom: 20px; }
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

# --- 5. ACCESO Y ASISTENCIA ---
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
            e_limpio = m_in.strip().lower()
            n_limpio = n_in.strip().replace(',', '')
            
            # Guardado local
            archivo_existe = os.path.exists("d.csv")
            with open("d.csv", "a") as f:
                if not archivo_existe or os.stat("d.csv").st_size == 0:
                    f.write("E,A,F,P\n")
                f.write(f"{e_limpio},{n_limpio},0,0\n")
            
            # Asistencia Google Sheets (Aumentamos el tiempo de espera)
            try: requests.get(f"{URL_APPS_SCRIPT}?email={e_limpio}", timeout=5)
            except: pass

            st.session_state.u = {"e": e_limpio, "a": n_limpio}; st.rerun()
    st.stop()

# --- 6. LÓGICA DE USUARIO ---
st.markdown(f"<div class='usuario-badge'>👤 Dr/a. <b>{st.session_state.u['a']}</b></div>", unsafe_allow_html=True)

# ERROR CORREGIDO: Filtramos por el email del usuario actual para saber si ÉL ya votó
if not df_global.empty:
    ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty
else:
    ya_voto = False

reloj_on = (t_limite > ahora)

# --- 7. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.subheader("👥 POSTULANTES EN SALA")
    if not df_global.empty:
        st.write(", ".join(df_global["A"].unique()))
    else:
        st.write("Esperando colegas...")

elif fase == 10:
    st.header("📊 POSICIONES ACTUALES")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)
        
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False)
        idx = total.index.tolist()
        votos = total.values.tolist()
        if st.session_state.u['a'] in idx:
            puesto = idx.index(st.session_state.u['a']) + 1
            if puesto <= 3:
                st.balloons(); play_audio("ganador.mp3")
            else: play_audio("bart.mp3")
        else: play_audio("bart.mp3")
        # Podio...
        if len(idx) >= 1: st.markdown(f"🥇 **{idx[0].upper()}** ({int(votos[0])} pts)")
        if len(idx) >= 2: st.markdown(f"🥈 {idx[1]} ({int(votos[1])} pts)")
        if len(idx) >= 3: st.markdown(f"🥉 {idx[2]} ({int(votos[2])} pts)")

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
        puntos = (100 + int(t_limite - ahora)*2) if correcta else 0
        with open("d.csv", "a") as f: 
            f.write(f"{st.session_state.u['e']},{st.session_state.u['a']},{fase},{puntos}\n")
        play_audio("exito.mp3" if correcta else "error.mp3")
        time.sleep(0.5); st.rerun()

time.sleep(1)
st.rerun()
