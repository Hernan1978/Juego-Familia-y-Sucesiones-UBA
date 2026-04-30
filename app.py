import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA "JUEZ PRO" Y MULTIMEDIA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {{ border: none !important; }}
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(12px); padding: 3rem !important; margin-top: 40px !important; border-radius: 15px !important;
        }}

        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        input, select, .stSelectbox div, .stNumberInput input, .stTextInput input {{
            background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold !important;
        }}

        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 900 !important; border: none !important; width: 100%; height: 3.5rem;
        }}
        .stButton>button:disabled {{ background-color: #444444 !important; color: #888888 !important; }}

        /* RELOJ IMPONENTE */
        .reloj-juez {{
            position: fixed; top: 30px; right: 30px;
            background: #C0392B; color: white !important;
            padding: 20px 40px; border-radius: 15px;
            z-index: 99999; font-size: 4.5rem; font-family: 'Courier New', monospace;
            border: 4px solid #D4AF37; box-shadow: 0 0 25px rgba(212, 175, 55, 0.6);
        }}

        /* ESTILOS DEL PODIO */
        .oro {{ color: #FFD700 !important; font-size: 5rem !important; text-transform: uppercase; text-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }}
        .plata {{ color: #C0C0C0 !important; font-size: 3.5rem !important; }}
        .bronce {{ color: #CD7F32 !important; font-size: 2.5rem !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if os.path.exists("d.csv"): return pd.read_csv("d.csv")
    return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ PANEL DE MANDO: JUEZ PRESIDENTE")
    clave = st.text_input("Clave de Seguridad:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase Actual:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("ACTUALIZAR ESTADO"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Segundos:", 5, 60, 20)
            if st.button("LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        st.write("---")
        if not df_global.empty:
            p = df_global[df_global["F"] == 0]["A"].unique()
            st.write(f"**👤 INTEGRANTES EN AUDIENCIA ({len(p)}):** " + ", ".join(p))
    st.write("---")

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ LEXPLAY UBA")
    n = st.text_input("Ingrese su Nombre y Apellido:")
    if st.button("CONECTAR AL TRIBUNAL"):
        if n:
            pd.DataFrame([["-", n, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"a": n}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE RONDA ---
voto_ok = not df_global[(df_global["A"] == st.session_state.u["a"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)
puede_votar = (0 < fase < 10) and reloj_on and not voto_ok

if puede_votar:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.info(f"Dr/a. {st.session_state.u['a']}, su presencia ha sido registrada.")

elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        top = df_global[df_global["F"] < 10].groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA DEFINITIVA: EL PODIO")
    st.balloons()
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        res = total.index.tolist()
        # PODIO ORO
        if len(res) >= 1:
            st.markdown(f"<div style='text-align:center;'><p class='oro'>🥇 {res[0].upper()}</p><p>CAMPEÓN DE LA AUDIENCIA</p></div>", unsafe_allow_html=True)
        # PLATA Y BRONCE
        c1, c2 = st.columns(2)
        if len(res) >= 2:
            c1.markdown(f"<div style='text-align:center;'><p class='plata'>🥈 {res[1]}</p></div>", unsafe_allow_html=True)
        if len(res) >= 3:
            c2.markdown(f"<div style='text-align:center;'><p class='bronce'>🥉 {res[2]}</p></div>", unsafe_allow_html=True)

else:
    st.header(f"RONDA N° {fase}")
    if voto_ok:
        st.success("✅ Veredicto recibido. El tiempo se ha detenido para usted. Aguarde resultados.")
    elif not reloj_on:
        st.warning("⏳ Aguarde a que el Juez habilite el cronómetro para dictaminar.")
    
    banco = {
        1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    st.write(f"### {banco[fase]['q']}")
    rta = st.radio("Veredicto:", banco[fase]['o'], disabled=not puede_votar)
    if st.button("ENVIAR VOTO", disabled=not puede_votar):
        pts = 100 if rta == banco[fase]['k'] else 0
        pd.DataFrame([["-", st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        st.rerun()

time.sleep(1); st.rerun()
