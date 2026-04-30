import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

SOUNDS = {
    "exito": "https://www.myinstants.com/media/sounds/correct-answer.mp3",
    "error": "https://www.myinstants.com/media/sounds/eso-tuvo-que-doler-oficina.mp3",
    "ganador": "https://www.myinstants.com/media/sounds/tada_6.mp3"
}

def play_audio(url):
    st.components.v1.html(f"<audio autoplay><source src='{url}' type='audio/mp3'></audio>", height=0)

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.92) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; margin-top: 40px !important; 
            border-radius: 20px !important; border: 2px solid #D4AF37;
        }}
        h1, h2, h3, h4, p, label, span {{ 
            color: #FFFFFF !important; font-weight: 800 !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        .titulo-oro {{ color: #D4AF37 !important; font-size: 2.5rem !important; text-align: center; }}
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 900 !important; border: 2px solid #FFFFFF !important;
        }}
        .reloj-juez {{ 
            position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; 
            padding: 20px 40px; border-radius: 15px; font-size: 4.5rem; border: 4px solid #D4AF37; z-index: 9999; 
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE DATOS PROTEGIDA ---
COLUMNAS = ["E", "A", "F", "P"]

def leer_f():
    if os.path.exists("f.txt"):
        try:
            with open("f.txt", "r") as x: return x.read().strip().split(",")
        except: return ["0", "0"]
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if not os.path.exists("d.csv"):
        return pd.DataFrame(columns=COLUMNAS)
    try:
        df = pd.read_csv("d.csv")
        # Si faltan columnas, lo reseteamos para evitar el KeyError
        if not all(col in df.columns for col in COLUMNAS):
            return pd.DataFrame(columns=COLUMNAS)
        return df
    except:
        return pd.DataFrame(columns=COLUMNAS)

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns(3)
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Seg:", 5, 60, 25)
            if st.button("🚀 LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        # Monitor blindado contra archivos vacíos
        if 0 < fase < 10 and not df_global.empty:
            st.write("---")
            # Verificamos que las columnas existan antes de filtrar
            if "F" in df_global.columns and "A" in df_global.columns:
                inscriptos = df_global[df_global["F"] == 0]["A"].unique()
                votaron = df_global[df_global["F"] == fase]["A"].unique()
                faltan = [a for a in inscriptos if a not in votaron]
                st.write(f"**Votaron:** {len(votaron)} / **Inscriptos:** {len(inscriptos)}")

# --- 4. ACCESO ALUMNO ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    mail = st.text_input("Email:")
    nombre = st.text_input("Nombre:")
    if st.button("INGRESAR"):
        if mail and nombre:
            headers = not os.path.exists("d.csv")
            pd.DataFrame([[mail, nombre, 0, 0]], columns=COLUMNAS).to_csv("d.csv", mode='a', header=headers, index=False)
            st.session_state.u = {"e": mail, "a": nombre}
            st.rerun()
    st.stop()

# --- 5. INTERFAZ ---
st.markdown(f"<p style='text-align:right;'>👤 {st.session_state.u['a']}</p>", unsafe_allow_html=True)

ya_voto = False
if not df_global.empty and "E" in df_global.columns:
    ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty

reloj_on = (t_limite > ahora)

if fase == 0:
    st.header("⚖️ Sala de Espera")
elif fase == 10:
    st.header("📊 RESULTADOS")
    if not df_global.empty: st.table(df_global.groupby("A")["P"].sum().sort_values(ascending=False))
elif fase == 99:
    st.header("🏆 PODIO")
    st.balloons()
else:
    if reloj_on and not ya_voto:
        st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
    
    banco = {
        1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Cuál es el plazo para aceptar la herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Dictamen:", banco[fase]['o'], disabled=ya_voto or not reloj_on, key=f"p{fase}")
    
    if ya_voto:
        st.success("✅ Veredicto enviado.")
    elif st.button("DICTAMINAR", disabled=not reloj_on):
        t_rest = int(t_limite - ahora)
        pts = (100 + (t_rest * 2)) if rta == banco[fase]['k'] else 0
        pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, pts]], columns=COLUMNAS).to_csv("d.csv", mode='a', header=False, index=False)
        play_audio(SOUNDS["exito"] if pts > 0 else SOUNDS["error"])
        st.rerun()

time.sleep(1); st.rerun()
