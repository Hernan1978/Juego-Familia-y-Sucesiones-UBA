import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA REFORZADA (ATAQUE TOTAL A BORDES) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    # La misma imagen de fondo elegante
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        
        /* 1. OCULTAR INTERFAZ DE STREAMLIT (Nube, Menú, etc.) */
        header, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stStatusWidget"] {{ 
            visibility: hidden !important; 
            position: absolute !important; 
            display: none !important;
        }}
        
        /* 2. FONDO Y FUENTE */
        .stApp {{ 
            background-image: url("{img}") !important; 
            background-size: cover !important; 
            background-attachment: fixed !important; 
            font-family: 'Inter', sans-serif !important; 
        }}
        
        /* --- 3. OPERACIÓN "BARRA CERO" (ANTI-DORADO) --- */
        /* Esta es la parte clave. Matamos CUALQUIER borde superior en CUALQUIER contenedor. */
        
        /* Mata los bordes de los bloques verticales */
        [data-testid="stVerticalBlock"] > div {{ border: none !important; border-top: none !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
        
        /* Mata los bordes de las filas de widgets */
        [data-testid="stHorizontalBlock"] > div {{ border: none !important; border-top: none !important; }}
        
        /* Mata las líneas horizontales (HR) */
        hr {{ display: none !important; border: none !important; }}
        
        /* Mata los bordes de los Expanders */
        .stExpander {{ border: none !important; box-shadow: none !important; }}
        
        /* Mata los bordes que Streamlit pone arriba de los inputs */
        .stTextInput, .stSelectbox, .stNumberInput, .stRadio {{ border-top: none !important; }}
        
        /* Asegura que el contenedor principal no tenga bordes */
        [data-testid="stAppViewContainer"] {{ border: none !important; }}
        
        /* 4. CONTENEDOR PRINCIPAL NEGRO (Vidrio) */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.88) !important;
            backdrop-filter: blur(10px);
            padding: 3rem !important; 
            margin-top: 30px !important;
            border-radius: 20px !important;
            border: none !important; /* Forzamos NO borde aquí */
            box-shadow: 0 15px 40px rgba(0,0,0,0.8);
        }}

        /* 5. PANEL DEL JUEZ (MODERNO) */
        .panel-juez {{
            background: rgba(212, 175, 55, 0.1) !important;
            padding: 25px !important;
            border-radius: 15px !important;
            border: 2px solid #D4AF37 !important;
            margin-bottom: 30px !important;
            border-top: 2px solid #D4AF37 !important; /* Este borde SÍ lo queremos */
        }}

        /* 6. RELOJ */
        .reloj-pantalla {{
            position: fixed !important; top: 25px !important; right: 25px !important;
            background: #C0392B !important; color: white !important;
            padding: 12px 28px !important; border-radius: 10px !important;
            z-index: 99999 !important; font-size: 3rem !important; 
            font-weight: 900;
        }}

        /* 7. TIPOGRAFÍAS Y BOTONES Alumno */
        h1, h2, h3, h4, h5, h6 {{ color: #D4AF37 !important; font-weight: 900 !important; text-transform: uppercase; letter-spacing: -1px; text-align: center; }}
        p, span, label, [data-testid="stWidgetLabel"] p {{ color: #FFFFFF !important; }}
        
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 700 !important; text-transform: uppercase; 
            border: none !important; border-radius: 8px !important;
            transition: 0.2s;
        }}
        .stButton>button:hover {{ background-color: #FFFFFF !important; transform: translateY(-2px); }}
        
        /* ESTILO DE LOS INPUTS */
        .stTextInput input, .stSelectbox div, .stNumberInput input {{
            background-color: rgba(255,255,255,0.06) !important;
            color: white !important; 
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            border-radius: 8px !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE DATOS Y ESTADO ---
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

# Forzamos refresco del estado
if 'refrescador' not in st.session_state: st.session_state.refrescador = False

fase_str, t_limite_str = leer_f()
fase = int(fase_str)
t_limite = float(t_limite_str)
df_global = cargar_datos()

# --- 3. PANEL JUEZ CON CLAVE (SÓLO SI ?admin=true) ---
if st.query_params.get("admin") == "true":
    st.markdown('<div class="panel-juez">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ CONTROL SUPERIOR DE AUDIENCIA")
    clave = st.text_input("Ingrese la Clave Maestra:", type="password", key="admin_pwd_main")
    
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"]
            idx = 0 if fase==0 else (4 if fase==99 else fase)
            sel = st.selectbox("Seleccione Fase:", ops, index=idx)
            if st.button("🔄 ACTUALIZAR ETAPA"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir_f(nv, 0); st.session_state.refrescador = not st.session_state.refrescador; st.rerun()
        with c2:
            dur = st.number_input("Segundos Ronda:", 5, 120, 20)
            if st.button("⏱️ LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.session_state.refrescador = not st.session_state.refrescador; st.rerun()
        with c3:
            if st.button("🗑️ REINICIAR DATOS"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f(0, 0); st.session_state.refrescador = not st.session_state.refrescador; st.rerun()
    elif clave != "":
        st.error("Clave incorrecta, colega.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ LEXPLAY UBA")
    st.write("#### Identifíquese para la audiencia de Familia y Sucesiones")
    st.write("")
    e = st.text_input("Email Institucional:")
    a = st.text_input("Nombre / Alias:")
    st.write("")
    if st.button("INGRESAR AL TRIBUNAL"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE TIEMPO Y VOTO ---
ahora = time.time()
v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
if (0 < fase < 99) and (t_limite > ahora) and not v_ok:
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS DE JUEGO ---
st.write("") # Espaciador
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Estimado/a Dr/a. **{st.session_state.u['a']}**, aguarde a que el Juez inicie la audiencia.")
    st.write("Su presencia ha sido registrada.")
    
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL: EL PODIO"); st.balloons()
    if not df_global.empty:
        st.table(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(10))

else:
    st.header(f"RONDA {fase}")
    if v_ok:
        st.success("✅ Su veredicto ha sido enviado correctamente. Aguarde la resolución.")
        if not df_global.empty:
            st.write("---")
            st.write("**Top 3 actual:**")
            st.write(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(3))
    else:
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.subheader(banco[fase]['q'])
        rta = st.radio("Su veredicto, Dr/a:", banco[fase]['o'], key=f"radio_{fase}")
        st.write("")
        if st.button("ENVIAR VOTACIÓN", disabled=not ((0 < fase < 99) and (t_limite > ahora)), key=f"btn_{fase}"):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR DOCENTE (PIE) ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    cols = st.columns(10)
    for i, n in enumerate(al):
        stt = "🟢" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "⚪"
        cols[i % 10].caption(f"{stt} {n}")

time.sleep(1); st.rerun()
