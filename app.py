import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA UBA (FONDO NEGRO SÓLIDO) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden; }}
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
        }}
        /* PANEL CENTRAL: NEGRO TOTAL */
        .main .block-container {{ 
            background-color: #000000 !important; 
            padding: 3rem !important; 
            border-radius: 15px !important; 
            border: 4px solid #D4AF37 !important; 
            margin-top: 30px !important;
            box-shadow: 0 0 20px rgba(212,175,55,0.5);
        }}
        /* RELOJ ROJO GIGANTE */
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 30px !important; border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; z-index: 99999 !important;
            font-family: 'Courier New', monospace !important; font-size: 2.5rem !important;
            font-weight: bold !important;
        }}
        /* TEXTOS BLANCO PURO Y GRANDES */
        h1, h2, h3, p, label, span, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important;
            font-weight: bold !important;
        }}
        h1 {{ font-size: 3.5rem !important; color: #D4AF37 !important; }}
        h3 {{ font-size: 2rem !important; }}
        
        /* BOTONES Y FORMULARIOS */
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            border: 2px solid #D4AF37 !important; font-size: 1.5rem !important;
            height: 4rem !important; width: 100% !important;
        }}
        input {{ background-color: #1A1A1A !important; color: white !important; border: 1px solid #D4AF37 !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip()
    return "0"

def escribir_f(v):
    with open("f.txt", "w") as x: x.write(str(v))

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
if "t_duracion" not in st.session_state: st.session_state.t_duracion = 20

fase = int(leer_f())

# --- 3. PANEL JUEZ (?admin=true) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ CONTROL DOCENTE")
        clave = st.text_input("Clave:", type="password")
        if clave == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            
            st.write("---")
            ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
            sel = st.selectbox("Fase:", ops, index=0)
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir_f(str(nv)); st.session_state.t_limite = 0; st.rerun()
            
            if 0 < fase < 99:
                st.write("---")
                st.session_state.t_duracion = st.slider("Segundos:", 5, 60, 20)
                if st.button("⏱️ INICIAR RELOJ"):
                    st.session_state.t_limite = time.time() + st.session_state.t_duracion + 1
                    st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR"):
        if e and a:
            if not os.path.exists("d.csv"):
                pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE JUEGO ---
voto_ok = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    m_u = st.session_state.u["e"]
    # CORRECCIÓN AQUÍ: Uso de corchetes para evitar AttributeError
    voto_ok = not df_v[(df_v["E"] == m_u) & (df_v["F"] == fase)].empty

ahora = time.time()
activo = False
if 0 < fase < 99 and not voto_ok and st.session_state.t_limite > ahora:
    seg = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">⌛ {seg}s</div>', unsafe_allow_html=True)
    activo = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write
