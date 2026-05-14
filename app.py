import streamlit as st
import pandas as pd
import os
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=["E", "A", "F", "P", "G"])

def leer_f():
    # El random previene que Streamlit use una versión cacheada del archivo
    if not os.path.exists("f.txt"): return ["0", "0"]
    try:
        with open("f.txt", "r") as x:
            cont = x.read().strip().split(",")
            return cont if len(cont) == 2 else ["0", "0"]
    except: return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x:
        x.write(f"{fase},{t_limite}")

# --- ESTILOS ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center; }
    .main .block-container { background: rgba(0, 0, 0, 0.85) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: auto; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; text-transform: uppercase; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; border: 1px solid #FFFFFF; height: 3.5em; }
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #C0392B; color: white !important; padding: 15px 25px; border-radius: 10px; font-size: 3.5rem; border: 3px solid #D4AF37; z-index: 9999; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

if 'user' not in st.session_state: st.session_state.user = None
if 'f_actual' not in st.session_state: st.session_state.f_actual = -1

# --- LOGIN ---
if st.session_state.user is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email Académico o Clave Maestra:")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m == "derecho2024": st.session_state.user = {"tipo": "juez"}
        elif m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            df = cargar_datos()
            if m not in df['E'].values:
                df = pd.concat([df, pd.DataFrame([{"E":m, "A":n, "F":0, "P":0, "G":g}])], ignore_index=True)
                df.to_csv("d.csv", index=False)
        st.rerun()
    st.stop()

# --- LÓGICA DE SINCRONIZACIÓN ---
f_info = leer_f()
fase_serv = int(f_info[0])
t_limite = float(f_info[1])
ahora = time.time()

# --- PANEL JUEZ ---
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ ESTRADOS DEL JUEZ</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        f_sel = st.selectbox("Elegir Pregunta:", [0] + list(banco.keys()) + [99])
        if st.button("📢 LANZAR PREGUNTA"): 
            escribir_f(f_sel, "0")
            st.rerun()
    with col2:
        t_set = st.number_input("Segundos:", 5, 60, 20)
        if st.button("⏱️ INICIAR RELOJ"):
            escribir_f(fase_serv, str(time.time() + t_set))
            st.rerun()
    
    df_v = cargar_datos()
    st.table(df_v[['A', 'P']].sort_values(by='P', ascending=False))

# --- PANEL ALUMNO ---
else:
    # Si el juez cambió la fase, resetear el estado local del alumno
    if st.session_state.f_actual != fase_serv:
        st.session_state.f_actual = fase_serv
        st.rerun()

    if t_limite > ahora:
        st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()

    if fase_serv in banco:
        p = banco[fase_serv]
        st.markdown(f"## {p['q']}")
        bloqueo = ahora > t_limite if t_limite > 0 else True
        
        rta = st.radio("Veredicto:", p["o"], key=f"r{fase_serv}")
        if st.button("ENVIAR", disabled=(t_limite == 0 or ahora > t_limite)):
            if rta == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df = cargar_datos()
                df.loc[df['E'] == st.session_state.user['e'], 'P'] += pts
                df.to_csv("d.csv", index=False)
                st.success("¡Correcto!")
            else: st.error("Incorrecto")
            time.sleep(1)
            st.rerun()
    elif fase_serv == 99:
        st.balloons()
        st.write("### FIN DEL JUEGO")
    else:
        st.info("Esperando instrucciones del Tribunal...")
        time.sleep(2)
        st.rerun()
