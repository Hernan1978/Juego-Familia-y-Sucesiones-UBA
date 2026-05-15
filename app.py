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
    try:
        with open("f.txt", "r") as x:
            cont = x.read().strip().split(",")
            return cont if len(cont) == 2 else ["0", "0"]
    except: return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x:
        x.write(f"{fase},{t_limite}")
        x.flush()
        os.fsync(x.fileno())

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-family: 'Poppins', sans-serif; text-align: center; }
    .main .block-container { background: rgba(10, 25, 41, 0.92) !important; padding: 3rem !important; border-radius: 12px !important; border-top: 5px solid #D4AF37; max-width: 1000px !important; margin: auto; }
    
    [data-testid="stTable"], .stDataFrame, [data-testid="stExpander"] { background-color: white !important; border-radius: 8px !important; }
    [data-testid="stTable"] td, [data-testid="stTable"] th, [data-testid="stTable"] tr, 
    .stDataFrame td, .stDataFrame th, .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] label {
        color: #000000 !important; font-weight: 800 !important;
    }

    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; font-weight: 700; text-transform: uppercase; }
    .podio-container { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-top: 20px; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #000 !important; padding: 20px; border-radius: 8px; width: 80%; font-size: 2rem; font-weight: 700; border: 2px solid white; }
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #E31837; color: white !important; padding: 20px; border-radius: 8px; font-size: 3rem; font-weight: 700; border: 2px solid #D4AF37; z-index: 9999; }
    .mensaje-final { color: #FFD700 !important; font-size: 2rem !important; font-weight: 800 !important; text-shadow: 2px 2px 10px #000000 !important; margin-top: 30px; padding: 20px; border-top: 3px solid #D4AF37; }
    
    .stButton>button { background-color: #D4AF37 !important; color: #0A1929 !important; font-weight: 700 !important; width: 100%; }
    .stButton>button:disabled { background-color: #555555 !important; color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BANCO ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. ACCESO ---
if 'user' not in st.session_state: st.session_state.user = None
if 'f_voto' not in st.session_state: st.session_state.f_voto = -1

if st.session_state.user is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Clave de Acceso:")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m == "derecho2024": st.session_state.user = {"tipo": "juez"}
        elif m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            df = cargar_datos()
            if m not in df['E'].values:
                with open("d.csv", "a") as f:
                    if os.stat("d.csv").st_size == 0: f.write("E,A,F,P,G\n")
                    f.write(f"{m},{n},0,0,{g}\n")
        st.rerun()
    st.stop()

# --- 5. LÓGICA ---
df_global = cargar_datos()
f_info = leer_f()
fase_serv, t_limite = int(f_info[0]), float(f_info[1])
ahora = time.time()

if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        f_sel = st.selectbox("Fase:", [0, 1, 2, 3, 4, 88, 99])
        if st.button("📢 CAMBIAR"): escribir_f(f_sel, "0"); st.rerun()
    with col_c2:
        t_set = st.number_input("Segs:", 5, 60, 25)
        if st.button("⏱️ ACTIVAR"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with col_c3:
        if st.button("🔄 REFRESCAR"): st.rerun() # BOTÓN REFRESCO
    with col_c4:
        # BOTÓN DESCARGA EXCEL (CSV)
        st.download_button("📥 EXCEL", df_global.to_csv(index=False), "notas_uba.csv", "text/csv")

    if st.button("⚠️ REINICIAR TODO"):
        if os.path.exists("d.csv"): os.remove("d.csv")
        escribir_f(0, 0); st.rerun()
    
    st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False))

else:
    # EL ALUMNO ACTUALIZA SIEMPRE QUE LA FASE DEL SERVIDOR CAMBIE
    if st.session_state.f_voto != fase_serv:
        st.session_state.enviado = False

    if fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora
        ya_envio = st.session_state.get('enviado', False)
        
        st.markdown(f"## {p['q']}")
        opcion = st.radio("Respuesta:", p["o"], key=f"r_{fase_serv}", disabled=ya_envio or not reloj_on)
        
        if reloj_on:
            st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        
        # BOTÓN: Bloqueado si no hay reloj o si ya envió
        btn_bloqueado = not reloj_on or ya_envio
        if st.button("ENVIAR SENTENCIA", disabled=btn_bloqueado):
            if opcion == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df_u = cargar_datos(); df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False)
                st.success(f"✅ REGISTRADO: +{pts}")
            else: st.error("❌ INCORRECTO")
            st.session_state.enviado = True
            st.session_state.f_voto = fase_serv
            time.sleep(1); st.rerun()
            
        if reloj_on and not ya_envio:
            time.sleep(1); st.rerun()
        elif ya_envio:
            st.info("⚖️ Esperando nueva pregunta...")
            time.sleep(2); st.rerun() # Autorefresco para detectar cambio de fase

    elif fase_serv == 88:
        st.markdown("<h2 class='titulo-oro'>📊 RESULTADOS</h2>")
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(10))
        time.sleep(3); st.rerun()

    elif fase_serv == 99:
        st.balloons(); st.audio("https://www.myinstants.com/media/sounds/we-are-the-champions-copia.mp3", autoplay=True)
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            img = "https://raw.githubusercontent.com/fede-999/images/main/alumna_festejo_uba.png" if podio[0][4] == "Dra." else "https://raw.githubusercontent.com/fede-999/images/main/alumno_festejo_uba.png"
            st.image(img, use_container_width=True)
            st.markdown(f"<div class='podio-container'><div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='mensaje-final'>La sesión ha concluido. El Tribunal agradece su participación. ¡Felicitaciones a los ganadores!</div>", unsafe_allow_html=True)
    else:
        st.info("⚖️ En espera..."); time.sleep(2); st.rerun()
