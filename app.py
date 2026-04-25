import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA UBA (COLORES SOLICITADOS) ---
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
        /* CAJA PRINCIPAL NEGRA Y DORADA */
        .main .block-container {{ 
            background-color: #000000 !important; 
            padding: 3rem !important; 
            border-radius: 15px !important; 
            border: 4px solid #D4AF37 !important; 
            margin-top: 30px !important;
        }}
        /* RELOJ ROJO UBA */
        .reloj-pantalla {{
            position: fixed !important; top: 15px !important; right: 15px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 10px 25px !important; border-radius: 30px !important;
            border: 2px solid #D4AF37 !important; z-index: 99999 !important;
            font-family: monospace !important; font-size: 2.2rem !important;
            font-weight: bold !important;
        }}
        /* TEXTOS BLANCO PURO */
        h1, h2, h3, p, label, span, .stMarkdown p {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        /* INPUTS Y SELECTS */
        input, select, .stSelectbox div {{ 
            background-color: #1A1A1A !important; 
            color: white !important; 
        }}
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            border: 2px solid #D4AF37 !important;
            font-weight: bold !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES DE DATOS ---
def leer_f():
    return open("f.txt", "r").read().strip() if os.path.exists("f.txt") else "0"

def escribir_f(v):
    with open("f.txt", "w") as x: x.write(str(v))

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
if "t_duracion" not in st.session_state: st.session_state.t_duracion = 20

fase = int(leer_f())

# --- 3. PANEL JUEZ (?admin=true) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ PANEL DE CONTROL")
        clave = st.text_input("Contraseña:", type="password")
        if clave == "derecho2024":
            if st.button("🗑️ REINICIAR JUEGO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            
            st.write("---")
            op_fases = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
            sel_fase = st.selectbox("Seleccionar Fase:", op_fases)
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel_fase else (99 if "Pod" in sel_fase else int(sel_fase.split(" ")[1]))
                escribir_f(str(nv)); st.session_state.t_limite = 0; st.rerun()
            
            if 0 < fase < 99:
                st.write("---")
                # ACÁ VOLVIÓ EL CONTROL DE TIEMPO
                st.session_state.t_duracion = st.slider("Segundos de ronda:", 5, 60, 20)
                if st.button("⏱️ INICIAR CRONÓMETRO"):
                    st.session_state.t_limite = time.time() + st.session_state.t_duracion + 1
                    st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE PARTICIPANTES")
    e = st.text_input("Email institucional:")
    a = st.text_input("Alias / Nombre:")
    if st.button("ENTRAR AL AULA"):
        if e and a:
            if not os.path.exists("d.csv"):
                pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE JUEGO ---
voto_realizado = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    voto_realizado = not df_v[(df_v.E == st.session_state.u["e"]) & (df_v.F == fase)].empty

ahora = time.time()
activo = False
if 0 < fase < 99 and not voto_realizado and st.session_state.t_limite > ahora:
    seg_restantes = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">⌛ {seg_restantes}s</div>', unsafe_allow_html=True)
    activo = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Bienvenido Dr/a. **{st.session_state.u['a']}**. El Juez iniciará la sesión pronto.")
elif fase == 99:
    st.header("🏆 Sentencia Final: Podio")
    if os.path.exists("d.csv"):
        df_p = pd.read_csv("d.csv")
        st.table(df_p[df_p.F > 0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if voto_realizado:
        st.success("✅ Su voto ha sido registrado correctamente.")
    else:
        # BANCO DE PREGUNTAS (RESTAURADO)
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2", "3/4"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años", "20 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.header(f"RONDA {fase}")
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Seleccione su veredicto:", banco[fase]['o'])
        if st.button("ENVIAR VOTO", disabled=not activo):
            puntos = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, puntos]], 
                         columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()
        if not activo:
            st.warning("⏳ Esperando que el Juez habilite el tiempo...")

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    dm = pd.read_csv("d.csv")
    alumnos = dm[dm.F == 0].A.unique()
    st.write("### 👥 Letrados en Audiencia")
    cols = st.columns(4)
    for i, n in enumerate(alumnos):
        stt = "✅" if not dm[(dm.A == n) & (dm.F == fase)].empty else "👤"
        cols[i % 4].write(f"{stt} {n}")

if st.session_state.t_limite > ahora or fase == 0:
    time.sleep(1); st.rerun()
