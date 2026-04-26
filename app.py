import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA UBA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"], [data-testid="stSidebar"] {{ visibility: hidden; position: absolute; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background-color: #000000 !important; 
            padding: 2.5rem !important; 
            border: 4px solid #D4AF37 !important; 
            margin-top: 20px !important;
            border-radius: 15px !important;
        }}
        .reloj-pantalla {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 30px !important; border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; z-index: 99999 !important;
            font-size: 2.5rem !important; font-family: monospace;
        }}
        h1, h2, h3, p, label, span, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important;
            font-weight: 800 !important;
        }}
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            border: 2px solid #D4AF37 !important; font-weight: bold !important;
            width: 100% !important; height: 3.5rem !important;
        }}
        .stExpander {{ border: 1px solid #D4AF37 !important; background-color: transparent !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE PERSISTENCIA (CON MANEJO DE ERRORES) ---
def leer_f():
    if os.path.exists("f.txt"):
        try:
            with open("f.txt", "r") as x:
                contenido = x.read().strip().split(",")
                if len(contenido) == 2:
                    return contenido
        except: pass
    return ["0", "0"] # Valor por defecto si el archivo falla

def escribir_f(fase, t_limite):
    try:
        with open("f.txt", "w") as x:
            x.write(f"{fase},{t_limite}")
    except: pass

def cargar_datos():
    if os.path.exists("d.csv"):
        try:
            df = pd.read_csv("d.csv")
            if all(c in df.columns for c in ["E","A","F","P"]): return df
        except: pass
    return pd.DataFrame(columns=["E","A","F","P"])

# Cargar estado actual
fase_str, t_limite_str = leer_f()
fase = int(fase_str)
t_limite = float(t_limite_str)
df_global = cargar_datos()

# --- 3. PANEL JUEZ ---
if st.query_params.get("admin") == "true":
    with st.expander("⚙️ PANEL DOCENTE EXCLUSIVO"):
        pwd = st.text_input("Clave:", type="password")
        if pwd == "derecho2024":
            c1, c2, c3 = st.columns(3)
            with c1:
                ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
                idx = 0 if fase==0 else (4 if fase==99 else fase)
                sel = st.selectbox("Fase:", ops, index=idx)
                if st.button("🔄 CAMBIAR FASE"):
                    nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                    escribir_f(nv, 0); st.rerun()
            with c2:
                dur = st.number_input("Segundos:", 5, 60, 20)
                if st.button("⏱️ INICIAR RELOJ"):
                    escribir_f(fase, time.time() + dur + 1); st.rerun()
            with c3:
                if st.button("🗑️ RESET"):
                    if os.path.exists("d.csv"): os.remove("d.csv")
                    if os.path.exists("f.txt"): os.remove("f.txt")
                    st.rerun()

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA TIEMPO Y VOTO ---
ahora = time.time()
v_ok = False
if not df_global.empty:
    v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty

activo = (0 < fase < 99) and (t_limite > ahora) and not v_ok

if activo:
    seg = int(t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">⌛ {seg}s</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write(f"Dr/a. **{st.session_state.u['a']}**, aguarde instrucciones.")
elif fase == 99:
    st.header("🏆 PODIO FINAL"); st.balloons()
    if not df_global.empty:
        st.table(df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False))
else:
    if v_ok:
        st.success("✅ Veredicto registrado.")
    else:
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.header(f"RONDA {fase}"); st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Veredicto:", banco[fase]['o'])
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    cols = st.columns(4)
    for i, n in enumerate(al):
        stt = "✅" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "👤"
        cols[i % 4].write(f"{stt} {n}")

time.sleep(1); st.rerun()
