import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA RESTAURADA (UBA) ---
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
        /* PANEL CENTRAL NEGRO */
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.9) !important; 
            padding: 3rem !important; 
            border-radius: 20px !important; 
            border: 3px solid #D4AF37 !important; 
            margin-top: 50px !important;
        }}
        /* RELOJ ROJO */
        .reloj-pantalla {{
            position: fixed !important; 
            top: 20px !important; 
            right: 20px !important;
            background-color: #C0392B !important; 
            color: white !important;
            padding: 15px 25px !important; 
            border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; 
            z-index: 999999 !important;
            font-family: monospace !important; 
            font-size: 2.2rem !important;
            font-weight: bold !important;
        }}
        /* TEXTOS BLANCOS */
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important;
            font-size: 1.2rem !important;
        }}
        /* INPUTS GRIS OSCURO */
        input {{ 
            background-color: #222222 !important; 
            color: #FFFFFF !important; 
            border: 1px solid #D4AF37 !important; 
        }}
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            font-weight: bold !important;
            border: 2px solid #D4AF37 !important; 
            height: 3.5rem !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. PERSISTENCIA ---
def leer_f():
    return open("f.txt", "r").read().strip() if os.path.exists("f.txt") else "0"

def escribir_f(v):
    with open("f.txt", "w") as x: x.write(str(v))

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
fase = int(leer_f())

# --- 3. PANEL JUEZ (CON CONTRASEÑA) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO JUEZ")
        # ACÁ ESTÁ LA CONTRASEÑA
        clave = st.text_input("Ingrese Clave:", type="password")
        if clave == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"])
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir_f(str(nv)); st.session_state.t_limite = 0; st.rerun()
            
            if 0 < fase < 99:
                if st.button("⏱️ LARGAR RELOJ"):
                    st.session_state.t_limite = time.time() + 21; st.rerun()
        elif clave != "":
            st.error("Clave incorrecta")

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
        pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA VOTO ---
voto_ok = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    voto_ok = not df_v[(df_v.E == st.session_state.u["e"]) & (df_v.F == fase)].empty

ahora = time.time()
puede = False
if 0 < fase < 99 and not voto_ok and st.session_state.t_limite > ahora:
    st.markdown(f'<div class="reloj-pantalla">⌛ {int(st.session_state.t_limite-ahora)}s</div>', unsafe_allow_html=True)
    puede = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("🏛️ Sala de Espera")
    st.write(f"Dr/a. **{st.session_state.u['a']}**, aguarde el inicio.")
elif fase == 99:
    st.header("🏆 Podio Final")
    if os.path.exists("d.csv"):
        dz = pd.read_csv("d.csv")
        st.table(dz[dz.F > 0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if voto_ok:
        st.success("✅ Veredicto enviado.")
    else:
        qs = {1: ["¿Legítima?", "2/3", "1/2"], 2: ["¿Plazo?", "10 años", "5 años"], 3: ["¿Máquina?", "No", "Sí"]}
        st.header(f"RONDA {fase}")
        st.write(f"### {qs[fase][0]}")
        rt = st.radio("Opción:", qs[fase][1:])
        if st.button("ENVIAR", disabled=not puede):
            pts = 100 if rt == qs[fase][1] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    dm = pd.read_csv("d.csv")
    letrados = dm[dm.F == 0].A.unique()
    cols = st.columns(4)
    for i, n in enumerate(letrados):
        stt = "✅" if not dm[(dm.A == n) & (dm.F == fase)].empty else "👤"
        cols[i % 4].write(f"{stt} {n}")

if st.session_state.t_limite > ahora or fase == 0:
    time.sleep(1); st.rerun()
