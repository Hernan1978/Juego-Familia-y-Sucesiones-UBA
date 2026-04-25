import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA RESTAURADA (ORO, ROJO Y MADERA) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header {{ visibility: hidden; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        /* Contenedor principal */
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85) !important; 
            padding: 3rem !important; border-radius: 20px !important; 
            border: 3px solid #D4AF37 !important; margin-top: 50px !important;
            max-width: 900px !important;
        }}

        /* Reloj flotante */
        .reloj {{
            position: fixed !important; top: 20px !important; right: 20px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 15px 25px !important; border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; z-index: 9999;
            font-family: monospace !important; font-size: 2.2rem !important;
            font-weight: bold !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}

        /* Textos y etiquetas */
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; text-shadow: 2px 2px 4px #000000 !important; 
            font-size: 1.2rem !important;
        }}
        h1 {{ font-size: 3rem !important; color: #D4AF37 !important; }}

        /* Botón Rojo UBA */
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            font-size: 1.5rem !important; font-weight: bold !important;
            border: 2px solid #D4AF37 !important; border-radius: 10px !important;
            height: 3.5rem !important; width: 100% !important;
        }}
        .stButton>button:disabled {{ background-color: #444 !important; border-color: #222 !important; }}

        /* Inputs (Fondo oscuro para que no maten la vista) */
        input {{ background-color: #222 !important; color: white !important; border: 1px solid #D4AF37 !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. PERSISTENCIA ---
def leer_f(): return open("f.txt","r").read().strip() if os.path.exists("f.txt") else "0"
def escribir_f(v): open("f.txt","w").write(str(v))

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
fase = int(leer_f())

# --- 3. PANEL JUEZ ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO")
        if st.text_input("Clave:", type="password") == "derecho2024":
            if st.button("🗑️ RESET"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            sel = st.selectbox("Fase:", ["0", "1", "2", "3", "99"], index=0)
            if st.button("CAMBIAR FASE"):
                escribir_f(sel); st.session_state.t_limite = 0; st.rerun()
            if 0 < fase < 99:
                if st.button("⏱️ LARGAR 20s"):
                    st.session_state.t_limite = time.time() + 21; st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
        pd.DataFrame([[e,a,0,0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA JUEGO ---
voto = False
if os.path.exists("d.csv"):
    df = pd.read_csv("d.csv")
    voto = not df[(df.E == st.session_state.u['e']) & (df.F == fase)].empty

ahora = time.time()
activo = False
if 0 < fase < 99 and not voto and st.session_state.t_limite > ahora:
    rem = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj">⌛ {rem}s</div>', unsafe_allow_html=True)
    activo = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.info(f"Bienvenido, Dr. {st.session_state.u['a']}. Aguarde al Juez.")
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    if os.path.exists("d.csv"):
        res = pd.read_csv("d.csv")
        st.table(res[res.F > 0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if voto:
        st.success("✅ Voto emitido correctamente.")
    else:
        qs = {1: ["¿Legítima?", "2/3", "1/2"], 2: ["¿Plazo?", "10 años", "5 años"], 3: ["¿Máquina?", "No", "Sí"]}
        st.header(f"RONDA {fase}")
        st.write(f"### {qs[fase][0]}")
        rta = st.radio("Veredicto:", qs[fase][1:])
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            pts = 100 if rta == qs[fase][1] else 0
            pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, pts]], 
                         columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    df_m = pd.read_csv("d.csv")
    al = df_m[df_m.F == 0].A.unique()
    st.write("### 👥 Letrados en Audiencia")
    cols = st.columns(4)
    for i, n in enumerate(al):
        status = "✅" if not df_m[(df_m.A == n) & (df_m.F == fase)].empty else "⏳"
        cols[i % 4].write(f"{status} {n}")

if st.session_state.t_limite > ahora or fase == 0:
    time.sleep(1); st.rerun()
