import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* 1. ELIMINACIÓN DE BARRAS (ATAQUE DIRECTO) */
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {{ border: none !important; }}
        [data-testid="stVerticalBlock"] > div > div:nth-child(1) > div::before {{ display: none !important; content: none !important; }}
        hr {{ display: none !important; }}
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}

        /* 2. FONDO */
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
        }}

        /* 3. CONTENEDOR PRINCIPAL */
        .main .block-container {{ 
            background: rgba(255, 255, 255, 0.9) !important; /* Fondo blanco casi sólido para máxima legibilidad */
            padding: 3rem !important; 
            margin-top: 40px !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}

        /* 4. TEXTOS (NEGRO TOTAL) */
        h1, h2, h3, p, label, span, .stMarkdown, [data-testid="stWidgetLabel"] p {{ 
            color: #000000 !important; 
            font-weight: 600 !important;
        }}

        /* 5. INPUTS Y SELECTORES (FONDO CLARO, LETRA NEGRA) */
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
        }}

        /* 6. BOTONES (DORADO CON LETRA NEGRA) */
        .stButton>button {{ 
            background-color: #D4AF37 !important; 
            color: #000000 !important; 
            border: 2px solid #000000 !important;
            font-weight: 900 !important;
            text-transform: uppercase;
        }}

        /* 7. RELOJ */
        .reloj-pantalla {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 15px 30px; border-radius: 10px;
            z-index: 99999; font-size: 3rem; font-weight: 900;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE ARCHIVOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)

# --- 3. PANEL ADMIN (SIN COLUMNAS PARA EVITAR LA BARRA) ---
if st.query_params.get("admin") == "true":
    st.markdown("### 🔑 CONTROL DOCENTE")
    clave = st.text_input("Clave Maestra:", type="password")
    if clave == "derecho2024":
        sel = st.selectbox("Seleccionar Etapa:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"])
        if st.button("ACTUALIZAR FASE"):
            nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
            escribir_f(nv, 0); st.rerun()
        
        dur = st.number_input("Tiempo de Ronda (segundos):", 5, 60, 20)
        if st.button("LARGAR RELOJ"):
            escribir_f(fase, time.time() + dur); st.rerun()
    st.write("---")

# --- 4. REGISTRO Y PANTALLAS ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ DESAFÍO FAMILIA Y SUCESIONES")
    a = st.text_input("Ingrese su Nombre y Apellido:")
    if st.button("INGRESAR AL TRIBUNAL"):
        if a: st.session_state.u = {"a": a}; st.rerun()
    st.stop()

ahora = time.time()
if (0 < fase < 99) and (t_limite > ahora):
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Bien
