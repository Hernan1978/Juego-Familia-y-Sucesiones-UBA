import streamlit as st
import pandas as pd
import os
import time

# --- ESTILO ---
st.set_page_config(layout="wide")
def style():
    st.markdown("""
    <style>
    header {visibility:hidden;}
    .stApp {background: #1a1a1a;}
    .main .block-container {
        background: #000; border: 2px solid #D4AF37; color: white;
    }
    .reloj {
        position:fixed; top:20px; right:20px; 
        background:#C0392B; color:white; padding:15px;
        font-size:2rem; z-index:99; border-radius:10px;
        border: 2px solid #D4AF37;
    }
    </style>""", unsafe_allow_html=True)
style()

# --- PERSISTENCIA SIMPLE ---
def leer_fase():
    if os.path.exists("f.txt"):
        return open("f.txt","r").read().strip()
    return "0"

def escribir_fase(v):
    with open("f.txt","w") as f:
        f.write(str(v))

# Inicializar tiempo en la sesión si no existe
if "t_limite" not in st.session_state:
    st.session_state.t_limite = 0

fase = int(leer_fase())

# --- JUEZ ---
if st.query_params.get("admin")=="true":
    with st.sidebar:
        st.title("JUEZ")
        pw = st.text_input("Clave:", type="password")
        if pw == "derecho2024":
            if st.button("BORRAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_fase("0")
                st.session_state.t_limite = 0
                st.rerun()
            
            f_nueva = st.selectbox("Fase:", ["0","1","2","3","99"])
            if st.button("CAMBIAR FASE"):
                escribir_fase(f_nueva)
                st.session_state.t_limite = 0
                st.rerun()
                
            if fase in [1,2,3]:
                if st.button("LARGAR RELOJ"):
                    st.session_state.t_limite = time.time() + 21
                    st.rerun()

# --- LOGIN ---
if 'u' not in st.session_state:
    st.session_state.u = None

if not st.session_state.u:
    st.title("REGISTRO")
    email = st.text_input("Email:")
    alias = st.text_input("Alias:")
    if st.button("ENTRAR") and email and alias:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv",index=False)
        pd.DataFrame([[email,alias,0,0]], columns=["E","A","F","P"]).to_csv("d.csv",mode='a',header=False,index=False)
        st.session_state.u = {"e":email, "a":alias}
        st.rerun()
    st.stop()

# --- LÓGICA RELOJ ---
voto_hecho = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    voto_hecho = not df_v[(df_v.E==st.session_state.u['e'])&(df_v.F==fase)].empty

activo = False
ahora = time.time()
if fase in [1,2,3] and not voto_hecho and st.session_state.t_limite > ahora:
    resta = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj">⌛ {resta}s</div>', unsafe_allow_html=True)
    activo = True

# --- PANTALLAS ---
if fase == 0:
    st.header("🏛️ SALA DE ESPERA")
    st.write(f"Hola {st.session_state.u['a']}, espera al Juez...")

elif fase == 99:
    st.header("🏆 RESULTADOS")
    if os.path.exists("d.csv"):
        df_res = pd.read_csv("d.csv")
        st.table(df_res[df_res.F > 0].groupby("A").P.sum())

else:
    if voto_hecho:
        st.success("✅ VOTO ENVIADO")
    else:
        preguntas = {
            1: ["¿Legítima?", "2/3", "1/2"],
            2: ["¿Plazo?", "10 años", "5 años"],
            3: ["¿Máquina?", "No", "Sí"]
        }
        st.header(f"RONDA {fase}")
        st.write(f"### {preguntas[fase][0]}")
        opcion = st.radio("Respuesta:", preguntas[fase][1:])
        
        if st.button("ENVIAR", disabled=not activo):
            puntos = 100 if opcion == preguntas[fase][1] else 0
            pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, puntos]], 
                         columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()
        
        if not activo:
            st.warning("⏳ Esperando que el Juez inicie el reloj...")

# --- PARTICIPANTES ---
st.write("---")
if os.path.exists("d.csv"):
    df_p = pd.read_csv("d.csv")
    presentes = df_
