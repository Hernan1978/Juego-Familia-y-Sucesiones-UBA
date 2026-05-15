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

# --- 2. ESTILOS ACTUALIZADOS (TODO A NEGRO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    
    /* Texto general en blanco para contraste con fondo oscuro */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { font-family: 'Poppins', sans-serif; text-align: center; }
    .main .block-container { background: rgba(10, 25, 41, 0.92); padding: 3rem; border-radius: 12px; border-top: 5px solid #D4AF37; max-width: 1100px; margin: auto; }
    
    /* --- FORZADO DE COLOR NEGRO (#000000) --- */
    /* Tablas, desplegables y sus contenidos */
    [data-testid="stTable"], .stDataFrame, [data-testid="stExpander"], .stTable, 
    div[data-testid="stExpander"] div, .stSelectbox label, .stNumberInput label { 
        background-color: white !important; color: #000000 !important;
    }
    
    /* Texto dentro del desplegable (Expander) */
    [data-testid="stExpander"] p, [data-testid="stExpander"] b, [data-testid="stExpander"] span, 
    [data-testid="stExpander"] summary, [data-testid="stExpander"] div {
        color: #000000 !important; font-weight: 700 !important;
    }

    /* Títulos de tablas y celdas */
    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame p, .stTable p, label {
        color: #000000 !important; font-weight: 700 !important;
    }

    /* Botón de Descarga Excel - Texto Negro */
    [data-testid="stDownloadButton"] button, [data-testid="stDownloadButton"] button p {
        color: #000000 !important; font-weight: 800 !important;
    }

    /* Podio Estilos */
    .podio-container { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-top: 20px; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #FFFFFF !important; padding: 20px; border-radius: 8px; width: 85%; font-size: 2.5rem; font-weight: 700; border: 3px solid white; text-shadow: 2px 2px 4px #000; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #FFFFFF !important; padding: 15px; border-radius: 8px; width: 75%; font-size: 1.8rem; font-weight: 600; text-shadow: 1px 1px 2px #000; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #FFFFFF !important; padding: 12px; border-radius: 8px; width: 65%; font-size: 1.5rem; font-weight: 600; text-shadow: 1px 1px 2px #000; }
    
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; font-weight: 700; text-transform: uppercase; margin: 0; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 700 !important; border: 1px solid #000; }
    
    .btn-exit>div>button { background-color: #ff4b4b !important; color: white !important; border: none !important; }
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #E31837; color: white !important; padding: 20px; border-radius: 8px; font-size: 3rem; font-weight: 700; border: 2px solid #D4AF37; z-index: 9999; }
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
fases_nombres = {0: "Inicio", 1: "Pregunta 1", 2: "Pregunta 2", 3: "Pregunta 3", 4: "Pregunta 4", 88: "RESULTADOS PARCIALES", 99: "RESULTADO FINAL"}

if st.session_state.user["tipo"] == "juez":
    c_tit, c_exit = st.columns([0.8, 0.2])
    with c_tit: st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    with c_exit: 
        st.markdown('<div class="btn-exit">', unsafe_allow_html=True)
        if st.button("🚪 SALIR"):
            st.session_state.user = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # DESPLEGABLE CON TEXTO NEGRO FORZADO
    with st.expander("📚 PREGUNTAS Y ASISTENCIAS", expanded=False):
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("<b>Preguntas del Banco:</b>", unsafe_allow_html=True)
            for k,v in banco.items(): st.write(f"**{k}.** {v['q']}")
        with c_p2:
            st.markdown("<b>Alumnos en Sala:</b>", unsafe_allow_html=True)
            st.table(df_global[['G', 'A']])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_fase = st.selectbox("Fase:", options=list(fases_nombres.keys()), format_func=lambda x: fases_nombres[x])
        if st.button("📢 ACTUALIZAR"): escribir_f(op_fase, "0"); st.rerun()
    with c2:
        t_set = st.number_input("Segs:", 5, 60, 25)
        if st.button("⏱️ RELOJ"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with c3:
        if st.button("🔄 REFRESCAR"): st.rerun()
    with c4:
        if st.button("⚠️ REINICIAR"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0, 0); st.rerun()
    
    df_ranking = df_global[['G', 'A', 'P']].sort_values(by='P', ascending=False)
    st.table(df_ranking)
    
    # BOTÓN DE DESCARGA CON TEXTO NEGRO
    csv = df_ranking.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 DESCARGAR EXCEL (CSV)",
        data=csv,
        file_name='resultados_lexplay.csv',
        mime='text/csv',
    )

else:
    # Interfaz Alumno y Resultados Finales (Fase 99)
    if fase_serv == 99:
        st.balloons(); st.snow()
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            img_file = "alumna_festejo_uba.png" if podio[0][4] == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro' style='font-size:4rem;'>🏆 {podio[0][4]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
            st.markdown("<div class='podio-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]}</div>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("⚖️ En espera de instrucciones del docente...")
        time.sleep(3); st.rerun()
