import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA (SANEADA) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide", initial_sidebar_state="collapsed")

def aplicar_estilo():
    st.markdown("""
        <style>
        /* Ocultar barra superior de forma segura */
        header, [data-testid="stHeader"] { 
            display: none !important;
        }
        
        /* Fondo de pantalla */
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070");
            background-size: cover;
            background-attachment: fixed;
        }

        /* Contenedor Principal */
        .main .block-container { 
            background-color: rgba(0, 0, 0, 0.85) !important; 
            padding: 3rem !important; 
            border-radius: 20px !important; 
            border: 2px solid #D4AF37 !important; 
            margin-top: 60px !important;
            max-width: 900px;
        }

        /* Reloj */
        .reloj-container {
            position: fixed; bottom: 30px; right: 30px; background-color: #C0392B; color: white;
            padding: 15px 25px; border-radius: 50px; border: 3px solid #D4AF37; z-index: 9999;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7);
        }
        
        /* Textos Blancos con Sombra */
        h1, h2, h3, p, label, span, .stMarkdown { 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important;
        }

        /* Cartel de Éxito */
        .cartel-exito { 
            background-color: rgba(46, 204, 113, 0.3); 
            border: 3px solid #2ECC71; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center;
        }

        /* Botón Rojo */
        .stButton>button { 
            background-color: #C0392B !important; 
            color: white !important; 
            font-size: 1.2rem !important;
            font-weight: bold !important;
            height: 3.5rem !important;
            width: 100% !important;
            border-radius: 10px !important;
            border: 1px solid #D4AF37 !important;
        }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. PERSISTENCIA ---
def leer(n, d="0"): return open(n, "r").read().strip() if os.path.exists(n) else d
def escribir(n, v): open(n, "w").write(str(v))

# --- 3. PANEL DOCENTE ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("MANDO JUEZ")
        if st.text_input("Clave:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("data.csv"): os.remove("data.csv")
                escribir("fase.txt", "0"); escribir("tiempo.txt", "OFF")
                st.rerun()
            st.write("---")
            f_act = int(leer("fase.txt"))
            f_sel = st.selectbox("Fase:", ["Esperando", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio"])
            if st.button("LANZAR FASE"):
                nv = 0 if "Esp" in f_sel else (99 if "Podio" in f_sel else int(f_sel.split(" ")[1]))
                escribir("fase.txt", nv); escribir("tiempo.txt", "OFF")
                st.rerun()
            if 0 < f_act < 99:
                seg = st.slider("Segundos:", 10, 60, 20)
                if st.button("⏱️ INICIAR"):
                    escribir("tiempo.txt", time.time() + seg); st.rerun()
                if os.path.exists("data.csv"):
                    df_m = pd.read_csv("data.csv")
                    st.write("### 📊 Monitor:")
                    for alu in df_m[df_m['Fase'] == 0]['Alias'].unique():
                        v = not df_m[(df_m['Alias'] == alu) & (df_m['Fase'] == f_act)].empty
                        st.write(f"{'✅' if v else '⏳'} {alu}")

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            if not os.path.exists("data.csv"): pd.DataFrame(columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", index=False)
            df_l = pd.read_csv("data.csv")
            if df_l[(df_l['Email'] == m) & (df_l['Fase'] == 0)].empty:
                pd.DataFrame([[m, a, 0, 0]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
            st.session_state.u = {"m": m, "a": a}; st.rerun()
    st.stop()

# --- 5. JUEGO ---
fase = int(leer("fase.txt"))
t_raw = leer("tiempo.txt", "OFF")
voto = False
if os.path.exists("data.csv"):
    df_v = pd.read_csv("data.csv")
    voto = not df_v[(df_v['Email'] == st.session_state.u['m']) & (df_v['Fase'] == fase)].empty

if fase == 0:
    st.header(f"🏛️ Sala de Audiencias")
    st.write(f"Bienvenido: {st.session_state.u['a']}")
    st.info("Aguarde a que el Juez inicie...")
    time.sleep(4); st.rerun()
elif fase == 99:
    st.balloons(); st.header("🏆 PODIO FINAL")
    if os.path.exists("data.csv"):
        df_r = pd.read_csv("data.csv")
        st.table(df_r[df_r['Fase'] > 0].groupby("Alias")["Puntos"].sum().sort_values(ascending=False))
else:
    if voto:
        st.markdown('<div class="cartel-exito"><h1>✔️ ENVIADO</h1><p>Veredicto registrado. Espere al Juez.</p></div>', unsafe_allow_html=True)
        time.sleep(5); st.rerun()
        st.stop()
    
    if t_raw != "OFF":
        rest = int(float(t_raw) - time.time())
        if rest > 0:
            st.markdown(f'<div class="reloj-container">⌛ {rest}s</div>', unsafe_allow_html=True)
        else:
            st.error("TIEMPO AGOTADO"); st.stop()

    banco = {1: {"q": "¿Porción legítima?", "op": ["1/2", "2/3"], "ok": "2/3"},
             2: {"q": "¿Plazo aceptación?", "op": ["10 años", "20 años"], "ok": "10 años"},
             3: {"q": "¿Testamento ológrafo?", "op": ["Sí", "No"], "ok": "No"}}
    p = banco[fase]
    st.header(f"RONDA {fase}")
    st.write(f"### {p['q']}")
    rta = st.radio("Veredicto:", p['op'], key=f"r{fase}")
    if st.button("ENVIAR VOTACIÓN"):
        pts = 100 if rta == p['ok'] else 0
        pd.DataFrame([[st.session_state.u['m'], st.session_state.u['a'], fase, pts]], columns=["Email", "Alias", "Fase", "Puntos"]).to_csv("data.csv", mode='a', header=False, index=False)
        st.rerun()
    
    if t_raw != "OFF":
        time.sleep(1); st.rerun()
