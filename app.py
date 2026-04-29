import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA REFINADA (GLASSMORPHISM) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

        header, [data-testid="stHeader"], [data-testid="stSidebar"] {{ visibility: hidden; position: absolute; }}
        
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* EL PANEL CENTRAL: EFECTO VIDRIO */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.8) !important;
            backdrop-filter: blur(10px);
            padding: 3rem !important; 
            border: 1px solid rgba(212, 175, 55, 0.3) !important; 
            margin-top: 30px !important;
            border-radius: 24px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }}

        /* PANEL DEL JUEZ: MÁS LIMPIO Y INTEGRADO */
        .panel-juez {{
            background: rgba(212, 175, 55, 0.1) !important;
            border: 2px solid #D4AF37 !important;
            padding: 20px !important;
            border-radius: 15px !important;
            margin-bottom: 30px !important;
        }}

        /* RELOJ: MODERNO Y MINIMALISTA */
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background: #C0392B !important; 
            color: white !important;
            padding: 10px 30px !important; 
            border-radius: 12px !important;
            z-index: 99999 !important;
            font-size: 3rem !important; 
            font-weight: 900;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 10px 30px rgba(192, 57, 43, 0.4);
        }}

        h1, h2, h3 {{ color: #FFFFFF !important; font-weight: 900 !important; text-transform: uppercase; letter-spacing: -1px; }}
        
        /* BOTONES: COLOR SÓLIDO SIN DEGRADADOS RAROS */
        .stButton>button {{ 
            background-color: #D4AF37 !important; 
            color: #000000 !important; 
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            transition: 0.3s;
        }}
        .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4); }}
        
        /* INPUTS */
        .stTextInput input, .stSelectbox div {{
            background-color: rgba(255,255,255,0.05) !important;
            color: white !important;
            border: 1px solid rgba(212, 175, 55, 0.5) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. SISTEMA DE ARCHIVOS ---
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

# --- 3. PANEL JUEZ (LIMPIO) ---
if st.query_params.get("admin") == "true":
    st.markdown('<div class="panel-juez">', unsafe_allow_html=True)
    st.markdown("### ⚙️ CONTROL DE AUDIENCIA")
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"]
        idx = 0 if fase==0 else (4 if fase==99 else fase)
        sel = st.selectbox("Fase actual:", ops, index=idx)
        if st.button("ACTUALIZAR FASE"):
            nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
            escribir_f(nv, 0); st.rerun()
    with c2:
        dur = st.number_input("Segundos:", 5, 120, 20)
        if st.button("LARGAR RELOJ"):
            escribir_f(fase, time.time() + dur); st.rerun()
    with c3:
        if st.button("REINICIAR TODO"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0, 0); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ LEXPLAY UBA")
    st.write("Ingrese sus datos para comenzar")
    e = st.text_input("Email:")
    a = st.text_input("Nombre:")
    if st.button("INGRESAR"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. TIEMPO Y ESTADO ---
ahora = time.time()
v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
activo = (0 < fase < 99) and (t_limite > ahora) and not v_ok

if activo:
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.info(f"Registrado como: {st.session_state.u['a']}. Aguarde el inicio de la audiencia.")
elif fase == 99:
    st.header("🏆 RESULTADOS FINALES"); st.balloons()
    if not df_global.empty:
        st.table(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(10))
else:
    st.header(f"PREGUNTA {fase}")
    if v_ok:
        st.success("Veredicto enviado. Esperando a los demás colegas...")
        # Ranking parcial discreto
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
        rta = st.radio("Su veredicto:", banco[fase]['o'])
        if st.button("ENVIAR RESPUESTA", disabled=not activo):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR (PIE DE PÁGINA) ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    cols = st.columns(8)
    for i, n in enumerate(al):
        stt = "🟢" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "⚪"
        cols[i % 8].caption(f"{stt} {n}")

time.sleep(1); st.rerun()
