import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA SIN ERRORES (SELECTOR ESPECÍFICO) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* 1. ELIMINAR LA BARRA MALDITA (EL SELECTOR REAL) */
        /* Streamlit usa un ::before en los bloques para esa línea superior */
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div {{
            border-top: none !important;
        }}
        [data-testid="stVerticalBlock"] > div > div:nth-child(1) > div::before {{
            display: none !important;
            content: none !important;
            height: 0px !important;
        }}
        div[data-testid="stVerticalBlock"] > div:first-child {{
            border-top: none !important;
        }}
        
        /* Ocultar todo lo de Streamlit */
        header, [data-testid="stHeader"], [data-testid="stSidebar"] {{ visibility: hidden !important; }}
        
        /* Fondo */
        .stApp {{ 
            background-image: url("{img}") !important; 
            background-size: cover !important; 
            background-attachment: fixed !important; 
        }}
        
        /* Contenedor Principal con Blur */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.88) !important;
            backdrop-filter: blur(12px);
            padding: 3rem !important; 
            margin-top: 50px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.9);
            border: none !important;
        }}

        /* Panel Juez */
        .panel-juez {{
            background: rgba(212, 175, 55, 0.1) !important;
            padding: 25px !important;
            border-radius: 15px !important;
            border: 2px solid #D4AF37 !important;
            margin-bottom: 40px !important;
        }}

        /* Reloj */
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background: #C0392B !important; color: white !important;
            padding: 15px 30px !important; border-radius: 12px !important;
            z-index: 99999 !important; font-size: 3.5rem !important; 
            font-weight: 900; font-family: monospace;
        }}

        h1, h2, h3 {{ color: #D4AF37 !important; text-align: center; font-weight: 900 !important; }}
        p, label, span {{ color: white !important; }}
        
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: black !important; 
            font-weight: bold !important; border: none !important;
            width: 100% !important; height: 3.5rem !important;
        }}
        
        /* Inputs */
        .stTextInput input, .stSelectbox div {{
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important; border: 1px solid #D4AF37 !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA ---
def leer_f():
    if os.path.exists("f.txt"):
        try:
            with open("f.txt", "r") as x: return x.read().strip().split(",")
        except: pass
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if os.path.exists("d.csv"):
        try: return pd.read_csv("d.csv")
        except: pass
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()

# --- 3. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown('<div class="panel-juez">', unsafe_allow_html=True)
    st.subheader("🔑 PANEL DE CONTROL")
    clave = st.text_input("Clave Maestra:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns(3)
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"])
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir_f(nv, 0); st.rerun()
        with c2:
            dur = st.number_input("Segundos:", 5, 60, 20)
            if st.button("INICIAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            if st.button("RESET DATOS"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f(0, 0); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. REGISTRO / JUEGO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e, a = st.text_input("Email:"), st.text_input("Nombre:")
    if st.button("INGRESAR"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

ahora = time.time()
v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False

if (0 < fase < 99) and (t_limite > ahora) and not v_ok:
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Dr/a. {st.session_state.u['a']}, aguarde al Juez.")
elif fase == 99:
    st.header("🏆 PODIO"); st.balloons()
    if not df_global.empty:
        st.table(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False))
else:
    st.header(f"RONDA {fase}")
    if v_ok:
        st.success("Voto enviado.")
    else:
        banco = {1:{"q":"Pregunta 1", "o":["A","B"], "k":"A"}, 2:{"q":"Pregunta 2", "o":["C","D"], "k":"C"}, 3:{"q":"Pregunta 3", "o":["E","F"], "k":"E"}}
        st.subheader(banco[fase]['q'])
        rta = st.radio("Veredicto:", banco[fase]['o'])
        if st.button("VOTAR", disabled=not (t_limite > ahora)):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

time.sleep(1); st.rerun()
