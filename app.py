import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=["E", "A", "F", "P", "G"])

def leer_f():
    if not os.path.exists("f.txt"): return ["0", "0"]
    with open("f.txt", "r") as x:
        cont = x.read().strip().split(",")
        return cont if len(cont) == 2 else ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x:
        x.write(f"{fase},{t_limite}")

# --- 2. ESTILOS (MANTENIDOS) ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center; }
    .main .block-container { background: rgba(0, 0, 0, 0.85) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: auto; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; text-transform: uppercase; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; border: 1px solid #FFFFFF; height: 3.5em; }
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #C0392B; color: white !important; padding: 15px 25px; border-radius: 10px; font-size: 3.5rem; border: 3px solid #D4AF37; z-index: 9999; }
    .podio-oro { font-size: 2.5rem; padding: 20px; border: 3px solid #D4AF37; background: rgba(212, 175, 55, 0.3); border-radius: 15px; margin-bottom: 10px; }
    .podio-plata { font-size: 2rem; padding: 15px; border: 2px solid #C0C0C0; background: rgba(192, 192, 192, 0.2); border-radius: 15px; margin-bottom: 10px; }
    .podio-bronce { font-size: 1.5rem; padding: 10px; border: 2px solid #CD7F32; background: rgba(205, 127, 50, 0.2); border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. ACCESO ---
if 'user' not in st.session_state: st.session_state.user = None
if 'f_ok' not in st.session_state: st.session_state.f_ok = -1

if st.session_state.user is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email Académico o Clave Maestra:")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m == "derecho2024":
            st.session_state.user = {"tipo": "juez"}
        elif m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            df = cargar_datos()
            if m not in df['E'].values:
                with open("d.csv", "a") as f:
                    if os.stat("d.csv").st_size == 0: f.write("E,A,F,P,G\n")
                    f.write(f"{m},{n},0,0,{g}\n")
        st.rerun()
    st.stop()

# --- 5. LÓGICA COMPARTIDA ---
df_global = cargar_datos()
f_info = leer_f()
fase_serv, t_limite = int(f_info[0]), float(f_info[1])
ahora = time.time()

# --- PANEL JUEZ ---
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ ESTRADOS DEL JUEZ</h1>", unsafe_allow_html=True)
    
    if not df_global.empty:
        st.download_button("📥 DESCARGAR ASISTENCIA", df_global.to_csv(index=False), "asistencia.csv")
    
    with st.expander("📖 BANCO DE PREGUNTAS"):
        for k, v in banco.items(): st.write(f"**{k}:** {v['q']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        f_sel = st.selectbox("Elegir Pregunta:", [0, 1, 2, 3, 4, 99], index=0)
        if st.button("📢 LANZAR FASE"): escribir_f(f_sel, "0"); st.rerun()
    with col2:
        t_set = st.number_input("Segundos Reloj:", 5, 60, 25)
        if st.button("⏱️ ACTIVAR RELOJ"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with col3:
        if st.button("⚠️ REINICIAR"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0, 0); st.rerun()
    
    st.divider()
    st.markdown("### 📊 Ranking en tiempo real")
    st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False))

# --- PANEL ALUMNO ---
else:
    if t_limite > ahora:
        st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        time.sleep(1); st.rerun()

    st.write(f"👤 {st.session_state.user['g']} {st.session_state.user['a']}")

    if fase_serv in banco:
        if st.session_state.f_ok != fase_serv:
            p = banco[fase_serv]
            st.markdown(f"## {p['q']}")
            bloqueo = not (t_limite > ahora)
            rta = st.radio("Veredicto:", p["o"], key=f"q{fase_serv}", disabled=bloqueo)
            if st.button("ENVIAR RESPUESTA", disabled=bloqueo):
                if rta == p["k"]:
                    pts = 10 + min(int(t_limite - ahora), 10)
                    df_up = cargar_datos()
                    df_up.loc[df_up['E'] == st.session_state.user['e'], 'P'] += pts
                    df_up.to_csv("d.csv", index=False)
                    st.success(f"✅ ¡Correcto! +{pts} pts")
                else: st.error("❌ Incorrecto")
                st.session_state.f_ok = fase_serv
                time.sleep(1); st.rerun()
            if bloqueo: st.warning("⚖️ Esperando que el Juez habilite el reloj...")
        else:
            st.info("⚖️ Recibido. Aguarde la siguiente fase...")
            time.sleep(3); st.rerun()

    elif fase_serv == 99:
        st.balloons()
        st.markdown("<h1 class='titulo-oro'>🚀 SENTENCIA FINAL 🚀</h1>", unsafe_allow_html=True)
        res = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if res:
            img = "https://raw.githubusercontent.com/fede-999/images/main/ganadora_mujer.png" if res[0][4] == "Dra." else "https://raw.githubusercontent.com/fede-999/images/main/ganador_hombre.png"
            st.image(img, use_column_width=True)
            st.markdown(f"<div class='podio-oro'>🥇 ORO: {res[0][1]}</div>", unsafe_allow_html=True)
            if len(res) > 1: st.markdown(f"<div class='podio-plata'>🥈 PLATA: {res[1][1]}</div>", unsafe_allow_html=True)
            if len(res) > 2: st.markdown(f"<div class='podio-bronce'>🥉 BRONCE: {res[2][1]}</div>", unsafe_allow_html=True)
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/human/sounds/applause-01.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)
    else:
        st.info("⚖️ Tribunal en receso...")
        time.sleep(3); st.rerun()
