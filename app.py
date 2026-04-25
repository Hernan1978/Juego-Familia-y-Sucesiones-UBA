import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header {{ visibility: hidden; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ 
            background-color: rgba(0,0,0,0.85) !important; 
            padding: 2rem !important; border-radius: 15px !important; 
            border: 2px solid #D4AF37 !important; margin-top: 30px !important;
        }}
        .reloj-pantalla {{
            position: fixed !important; top: 15px !important; right: 15px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 10px 20px !important; border-radius: 30px !important;
            border: 2px solid #D4AF37 !important; z-index: 99999 !important;
            font-family: monospace !important; font-size: 2rem !important;
        }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 1px 1px 2px black; }}
        .stButton>button {{ 
            background-color: #C0392B !important; color: white !important; 
            font-weight: bold !important; border: 1px solid #D4AF37 !important;
        }}
        .stButton>button:disabled {{ background-color: #444 !important; color: #888 !important; }}
        .caja-p {{
            background-color: rgba(212,175,55,0.1) !important;
            padding: 15px !important; border-radius: 10px !important;
            border: 1px solid #D4AF37 !important; margin-top: 20px !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES ---
def leer(n, d="0"):
    if os.path.exists(n):
        with open(n, "r") as f: return f.read().strip()
    return d

def escribir(n, v):
    with open(n, "w") as f: f.write(str(v))

# --- 3. ESTADO ---
fase = int(leer("fase.txt"))
limite = leer("tiempo.txt", "OFF")

# --- 4. ADMIN ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ JUEZ")
        pwd = st.text_input("Clave:", type="password")
        if pwd == "derecho2024":
            if st.button("🗑️ REINICIAR"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir("fase.txt","0"); escribir("tiempo.txt","OFF"); st.rerun()
            op = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"]
            sel = st.selectbox("Fase:", op, index=fase if fase < 4 else 4)
            if st.button("CAMBIAR FASE"):
                nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                escribir("fase.txt", nv); escribir("tiempo.txt", "OFF"); st.rerun()
            if 0 < fase < 99:
                t = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR"):
                    escribir("tiempo.txt", str(time.time() + t)); st.rerun()

# --- 5. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.title("⚖️ REGISTRO")
    em = st.text_input("Email:")
    al = st.text_input("Alias:")
    if st.button("ENTRAR"):
        if em and al:
            if not os.path.exists("data.csv"):
                pd.DataFrame(columns=["E","A","F","P"]).to_csv("data.csv", index=False)
            df = pd.read_csv("data.csv")
            if df[(df['E']==em) & (df['F']==0)].empty:
                pd.DataFrame([[em,al,0,0]], columns=["E","A","F","P"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.u = {"m": em, "a": al}; st.rerun()
    st.stop()

# --- 6. JUEGO ---
voto = False
if os.path.exists("data.csv"):
    df_v = pd.read_csv("data.csv")
    voto = not df_v[(df_v['E']==st.session_state.u['m']) & (df_v['F']==fase)].empty

activo = False
if 0 < fase < 99 and not voto and limite != "OFF":
    rem = int(float(limite) - time.time())
    if rem > 0:
        st.markdown(f'<div class="reloj-pantalla">⌛ {rem}s</div>', unsafe_allow_html=True)
        activo = True
    else:
        escribir("tiempo.txt", "OFF"); st.rerun()

# --- 7. PANTALLAS ---
if fase == 0:
    st.header("🏛️ Sala de Espera")
    st.write("Aguarde a que el Juez inicie el debate.")
elif fase == 99:
    st.header("🏆 PODIO FINAL")
    if os.path.exists("data.csv"):
        df_r = pd.read_csv("data.csv")
        res = df_r[df_r['F']>0].groupby("A")["P"].sum().sort_values(ascending=False)
        st.table(res)
else:
    if voto:
        st.success("✅ Voto registrado. Espere la siguiente ronda.")
    else:
        b = {1:{"q":"¿Legítima descendientes?","o":["1/2","2/3","4/5
