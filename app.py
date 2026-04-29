import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA REFORZADA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Roboto+Mono:wght@700&display=swap');

        header, [data-testid="stHeader"], [data-testid="stSidebar"] {{ visibility: hidden; position: absolute; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        /* CONTENEDOR PRINCIPAL */
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.9) !important; 
            padding: 2.5rem !important; 
            border: 4px solid #D4AF37 !important; 
            margin-top: 20px !important;
            border-radius: 15px !important;
        }}

        /* PANEL DEL JUEZ - ALTA VISIBILIDAD */
        .panel-juez {{
            background-color: #1a1a1a !important;
            border: 5px solid #D4AF37 !important;
            padding: 25px !important;
            border-radius: 15px !important;
            margin-bottom: 40px !important;
            box-shadow: 0px 0px 25px rgba(212, 175, 55, 0.4) !important;
        }}

        /* RELOJ GIGANTE */
        .reloj-pantalla {{
            position: fixed !important; top: 15px !important; right: 15px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 35px !important; border-radius: 10px !important;
            border: 3px solid #D4AF37 !important; z-index: 99999 !important;
            font-size: 3.5rem !important; font-family: 'Roboto Mono', monospace;
        }}

        h1, h2, h3 {{ font-family: 'Cinzel', serif !important; color: #D4AF37 !important; text-align: center; }}
        
        /* BOTONES DEL PANEL */
        .stButton>button {{ 
            height: 3.5rem !important;
            font-weight: bold !important;
            border: 2px solid #D4AF37 !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. PERSISTENCIA ---
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

# --- 3. PANEL JUEZ (VISIBLE SOLO CON ?admin=true) ---
if st.query_params.get("admin") == "true":
    st.markdown('<div class="panel-juez">', unsafe_allow_html=True)
    st.markdown("### ⚖️ MANDO SUPREMO DEL JUEZ")
    
    col1, col2, col3 = st.columns([1.5, 1, 1])
    
    with col1:
        ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"]
        idx = 0 if fase==0 else (4 if fase==99 else fase)
        sel = st.selectbox("Seleccionar Etapa de la Audiencia:", ops, index=idx)
        if st.button("🔄 CAMBIAR FASE AHORA"):
            nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
            escribir_f(nv, 0); st.rerun()
            
    with col2:
        dur = st.number_input("Duración (seg):", 5, 120, 30)
        if st.button("⏱️ INICIAR RELOJ"):
            escribir_f(fase, time.time() + dur); st.rerun()
            
    with col3:
        st.write("Control de Datos:")
        if st.button("🗑️ REINICIAR JUEGO"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0, 0); st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ AUDIENCIA DE FAMILIA Y SUCESIONES")
    e, a = st.text_input("Email:"), st.text_input("Nombre / Alias:")
    if st.button("INGRESAR AL TRIBUNAL"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA VOTO ---
ahora = time.time()
v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
activo = (0 < fase < 99) and (t_limite > ahora) and not v_ok

if activo:
    st.markdown(f'<div class="reloj-pantalla">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Bienvenido Dr/a. **{st.session_state.u['a']}**. Aguarde el inicio.")
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL"); st.balloons()
    if not df_global.empty:
        st.table(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(10))
else:
    st.header(f"RONDA N° {fase}")
    if v_ok:
        st.success("✅ Veredicto enviado. Líderes actuales:")
        if not df_global.empty:
            st.dataframe(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(3), use_container_width=True)
    else:
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Veredicto:", banco[fase]['o'])
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    cols = st.columns(6)
    for i, n in enumerate(al):
        stt = "✅" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "👤"
        cols[i % 6].write(f"{stt} {n}")

time.sleep(1); st.rerun()
