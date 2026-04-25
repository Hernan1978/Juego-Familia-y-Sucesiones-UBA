import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA UBA (FONDO NEGRO Y DORADO) ---
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
        /* PANEL CENTRAL NEGRO SOLIDO */
        .main .block-container {{ 
            background-color: #000000 !important; 
            padding: 3rem !important; 
            border: 4px solid #D4AF37 !important; 
            margin-top: 30px !important;
            border-radius: 15px !important;
        }}
        /* TEXTOS BLANCOS GIGANTES */
        h1, h2, h3, p, label, span, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; 
            text-shadow: 3px 3px 5px #000000 !important;
            font-weight: 800 !important;
        }}
        /* RELOJ ROJO */
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 30px !important; border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; z-index: 99999 !important;
            font-size: 2.5rem !important; font-family: monospace;
        }}
        /* BOTONES */
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            border: 2px solid #D4AF37 !important; font-weight: bold !important;
            height: 4rem !important; font-size: 1.5rem !important;
        }}
        /* ENTRADAS DE TEXTO */
        input {{ background-color: #1A1A1A !important; color: white !important; border: 1px solid #D4AF37 !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        try: 
            with open("f.txt", "r") as x: return x.read().strip()
        except: pass
    return "0"

def escribir_f(v):
    with open("f.txt", "w") as x: x.write(str(v))

def cargar_datos():
    if os.path.exists("d.csv"):
        try:
            df = pd.read_csv("d.csv")
            if all(c in df.columns for c in ["E","A","F","P"]): return df
        except: pass
    return pd.DataFrame(columns=["E","A","F","P"])

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
if "t_duracion" not in st.session_state: st.session_state.t_duracion = 20

fase = int(leer_f())
df_global = cargar_datos()

# --- 3. PANEL JUEZ (?admin=true) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO JUEZ")
        if st.text_input("Clave:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR JUEGO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            st.write("---")
            ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
            sel = st.selectbox("Fase Actual:", ops)
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir_f(str(nv)); st.session_state.t_limite = 0; st.rerun()
            if 0 < fase < 99:
                st.session_state.t_duracion = st.slider("Segundos de Ronda:", 5, 60, 20)
                if st.button("⏱️ INICIAR RELOJ"):
                    st.session_state.t_limite = time.time() + st.session_state.t_duracion + 1
                    st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR AL AULA") and e and a:
        pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
        st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE VOTACIÓN (RE-LECTURA FORZADA) ---
df_global = cargar_datos() # Forzamos lectura para que el botón sepa si ya votaste
v_ok = False
if not df_global.empty:
    m_u = st.session_state.u["e"]
    v_ok = not df_global[(df_global["E"] == m_u) & (df_global["F"] == fase)].empty

ahora = time.time()
activo = False
if 0 < fase < 99 and not v_ok and st.session_state.t_limite > ahora:
    st.markdown(f'<div class="reloj-pantalla">⌛ {int(st.session_state.t_limite-ahora)}s</div>', unsafe_allow_html=True)
    activo = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Bienvenido Dr/a. **{st.session_state.u['a']}**, aguarde instrucciones del Juez.")
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    st.balloons()
    if not df_global.empty:
        puntos = df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False)
        st.table(puntos)
else:
    if v_ok:
        st.success("✅ Veredicto enviado correctamente.")
    else:
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.header(f"RONDA {fase}"); st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Seleccione su veredicto:", banco[fase]['o'])
        
        # EL BOTÓN AHORA RESPONDE SI EL RELOJ ESTÁ ACTIVO
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], 
                         columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()
        
        if not activo:
            st.warning("⏳ Aguarde a que el Juez inicie el cronómetro para votar.")

# --- 7. MONITOR DE PARTICIPANTES ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    st.write("### 👥 Letrados en Audiencia")
    cols = st.columns(4)
    for i, n in enumerate(al):
        stt = "✅" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "👤"
        cols[i % 4].write(f"{stt} {n}")

if st.session_state.t_limite > ahora or fase == 0:
    time.sleep(1); st.rerun()
