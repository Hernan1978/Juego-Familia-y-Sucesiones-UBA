import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA DE BIBLIOTECA UBA ---
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
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85) !important; 
            padding: 3rem !important; 
            border-radius: 20px !important; 
            border: 3px solid #D4AF37 !important; 
            margin-top: 50px !important;
        }}
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
        h1, h2, h3, p, label, .stMarkdown {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important; 
        }}
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            font-weight: bold !important;
            border: 2px solid #D4AF37 !important; 
            height: 3.5rem !important;
            width: 100% !important;
        }}
        .stButton>button:disabled {{ 
            background-color: #444 !important; 
            border-color: #222 !important; 
        }}
        input {{ 
            background-color: #333 !important; 
            color: white !important; 
            border: 1px solid #D4AF37 !important; 
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE ARCHIVOS ---
def leer_f():
    if os.path.exists("f.txt"):
        return open("f.txt", "r").read().strip()
    return "0"

def escribir_f(v):
    with open("f.txt", "w") as x:
        x.write(str(v))

if "t_limite" not in st.session_state:
    st.session_state.t_limite = 0

fase = int(leer_f())

# --- 3. PANEL JUEZ (?admin=true) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO JUEZ")
        if st.button("🗑️ REINICIAR TODO"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f("0")
            st.session_state.t_limite = 0
            st.rerun()
        
        ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
        sel = st.selectbox("Fase:", ops)
        if st.button("CAMBIAR FASE"):
            nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
            escribir_f(str(nv))
            st.session_state.t_limite = 0
            st.rerun()
            
        if 0 < fase < 99:
            if st.button("⏱️ LARGAR 20 SEG"):
                st.session_state.t_limite = time.time() + 21
                st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state:
    st.session_state.u = None

if not st.session_state.u:
    st.title("🏛️ REGISTRO DE LETRADOS")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
        df_l = pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"])
        df_l.to_csv("d.csv", mode='a', header=False, index=False)
        st.session_state.u = {"e": e, "a": a}
        st.rerun()
    st.stop()

# --- 5. TIEMPO Y VOTO ---
voto_hecho = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    m_u = st.session_state.u["e"]
    voto_hecho = not df_v[(df_v.E == m_u) & (df_v.F == fase)].empty

ahora = time.time()
puede_votar = False
if 0 < fase < 99 and not voto_hecho and st.session_state.t_limite > ahora:
    resta = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">⌛ {resta}s</div>', unsafe_allow_html=True)
    puede_votar = True

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("🏛️ Sala de Espera")
    st.write(f"Bienvenido Dr. **{st.session_state.u['a']}**")
elif fase == 99:
    st.header("🏆 Podio Final")
    if os.path.exists("d.csv"):
        dz = pd.read_csv("d.csv")
        st.table(dz[dz.F > 0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if voto_hecho:
        st.success("✅ Veredicto enviado. Espere la siguiente ronda.")
    else:
        qs = {1: ["¿Porción legítima descendientes?", "2/3", "1/2"], 
              2: ["¿Plazo máximo aceptación?", "10 años", "5 años"], 
              3: ["¿Válido testamento ológrafo a máquina?", "No", "Sí"]}
        st.header(f"RONDA {fase}")
        st.write(f"### {qs[fase][0]}")
        rt = st.radio("Veredicto:", qs[fase][1:])
        if st.button("ENVIAR VOTACIÓN", disabled=not puede_votar):
            pts = 100 if rt == qs[fase][1] else 0
            nr = [[st.session_state.u["e"], st.session_state.u["a"], fase, pts]]
            df3 = pd.DataFrame(nr, columns=["E","A","F","P"])
            df3.to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    dm = pd.read_csv("d.csv")
    lista = dm[dm.F == 0].A.unique()
    st.write("### 👥 Letrados en Audiencia")
    cols = st.columns(4)
    for i, n in enumerate(lista):
        stt = "✅" if not dm[(dm.A == n) & (dm.F == fase)].empty else "👤"
        cols[i % 4].write(f"{stt} {n}")

if st.session_state.t_limite > ahora or fase == 0:
    time.sleep(1)
    st.rerun()
