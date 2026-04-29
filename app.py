import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN VISUAL (TEXTO BLANCO / INPUTS NEGROS) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* 1. ELIMINAR BARRAS Y DECORACIONES DE STREAMLIT */
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {{ border: none !important; }}
        [data-testid="stVerticalBlock"] > div > div:nth-child(1) > div::before {{ display: none !important; content: none !important; }}
        hr {{ display: none !important; }}
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}

        /* 2. FONDO DE PANTALLA */
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
        }}

        /* 3. CONTENEDOR CENTRAL (VIDRIO OSCURO) */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(10px);
            padding: 3rem !important; 
            margin-top: 40px !important;
            border-radius: 15px !important;
            border: none !important;
        }}

        /* --- 4. TÍTULOS Y TEXTOS EN BLANCO --- */
        h1, h2, h3, h4, h5, h6, 
        p, label, span, 
        [data-testid="stWidgetLabel"] p, 
        .stMarkdown p {{ 
            color: #FFFFFF !important; 
            font-weight: 700 !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}

        /* --- 5. INPUTS (FONDO BLANCO, LETRA NEGRA) --- */
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 5px !important;
        }}
        
        /* Asegurar que el texto tipeado sea negro */
        input[type="text"], input[type="password"], input[type="number"] {{
            color: #000000 !important;
        }}

        /* BOTONES (DORADO / LETRA NEGRA) */
        .stButton>button {{ 
            background-color: #D4AF37 !important; 
            color: #000000 !important; 
            font-weight: 900 !important;
            border: none !important;
            text-transform: uppercase;
        }}

        /* RELOJ ROJO */
        .reloj-pantalla {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 15px 30px; border-radius: 10px;
            z-index: 99999; font-size: 3rem; font-weight: 900;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE PERSISTENCIA ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("### 🔑 PANEL DEL JUEZ")
    clave = st.text_input("Contraseña de Mando:", type="password")
    if clave == "derecho2024":
        sel = st.selectbox("Cambiar Etapa de la Audiencia:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"])
        if st.button("EJECUTAR CAMBIO"):
            nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
            escribir_f(nv, 0); st.rerun()
        
        dur = st.number_input("Establecer Segundos:", 5, 60, 20)
        if st.button("LARGAR CRONÓMETRO"):
            escribir_f(fase, time.time() + dur); st.rerun()
    st.write("---")

# --- 4. REGISTRO Y PANTALLAS ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ AUDIENCIA VIRTUAL UBA")
    a = st.text_input("Ingrese su Nombre Completo:")
    if st.button("ENTRAR A LA SALA"):
        if a: st.session_state.u = {"a": a}; st.rerun()
    st.stop()

ahora = time.time()
if (0 < fase < 99) and (t_limite > ahora):
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Doctor/a **{st.session_state.u['a']}**, por favor aguarde el inicio del proceso.")
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL"); st.balloons()
else:
    st.header(f"RONDA N° {fase}")
    st.write("### Dictamine su veredicto:")
    st.radio("Opciones legales:", ["Opción A", "Opción B", "Opción C"])
    if st.button("PRESENTAR VOTO", disabled=not (t_limite > ahora)):
        st.success("Dictamen recibido.")

time.sleep(1); st.rerun()
