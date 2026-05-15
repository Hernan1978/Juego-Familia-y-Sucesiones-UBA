import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    try: 
        return pd.read_csv("d.csv")
    except: 
        return pd.DataFrame(columns=["E", "A", "F", "P", "G"])

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
    
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF; font-family: 'Poppins', sans-serif; text-align: center; }
    .main .block-container { background: rgba(10, 25, 41, 0.92); padding: 3rem; border-radius: 12px; border-top: 5px solid #D4AF37; max-width: 1100px; margin: auto; }
    
    /* PANEL DOCENTE: TEXTO NEGRO EN TABLAS Y SELECTORES */
    [data-testid="stTable"], .stDataFrame, [data-testid="stExpander"], .stTable, div[data-testid="stExpander"] div, .stSelectbox label { 
        background-color: white !important; color: #000000 !important;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame p, .stTable p, .stSelectbox p, label, [data-testid="stExpander"] b {
        color: #000000 !important; font-weight: 700 !important;
    }

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

# --- INTERFAZ JUEZ ---
if st.session_state.user["tipo"] == "juez":
    c_tit, c_exit = st.columns([0.8, 0.2])
    with c_tit: st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    with c_exit: 
        st.markdown('<div class="btn-exit">', unsafe_allow_html=True)
        if st.button("🚪 SALIR"):
            st.session_state.user = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
        op_fase = st.selectbox("Cambiar Fase:", options=list(fases_nombres.keys()), format_func=lambda x: fases_nombres[x])
        if st.button("📢 ACTUALIZAR"): escribir_f(op_fase, "0"); st.rerun()
    with c2:
        t_set = st.number_input("Segundos:", 5, 60, 25)
        if st.button("⏱️ RELOJ"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with c3:
        if st.button("🔄 REFRESCAR"): st.rerun()
    with c4:
        if st.button("⚠️ REINICIAR"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0, 0); st.rerun()
    
    # SECCIÓN DE TABLA Y DESCARGA
    df_ranking = df_global[['G', 'A', 'P']].sort_values(by='P', ascending=False)
    st.table(df_ranking)
    
    # BOTÓN DE DESCARGA EXCEL (CSV)
    csv = df_ranking.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 DESCARGAR RESULTADOS (EXCEL)",
        data=csv,
        file_name='resultados_lexplay_uba.csv',
        mime='text/csv',
    )

# --- INTERFAZ ALUMNO / RESULTADOS ---
else:
    st.markdown('<div class="btn-exit" style="text-align: right;">', unsafe_allow_html=True)
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.user = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora
        ya_envio = st.session_state.get('enviado', False)
        if st.session_state.f_voto != fase_serv: st.session_state.enviado = False
        
        st.markdown(f"## {p['q']}")
        opcion = st.radio("Dictamen:", p["o"], key=f"r_{fase_serv}", disabled=ya_envio or not reloj_on)
        if reloj_on and not ya_envio:
            st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        if st.button("ENVIAR SENTENCIA", disabled=(not reloj_on or ya_envio)):
            if opcion == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df_u = cargar_datos(); df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False)
                st.success("✅ REGISTRADO")
            else: st.error("❌ INCORRECTO")
            st.session_state.enviado = True
            st.session_state.f_voto = fase_serv
            time.sleep(1); st.rerun()
        time.sleep(2); st.rerun()

    elif fase_serv == 88:
        st.markdown("<h2 style='color:#D4AF37;'>📊 RESULTADOS PARCIALES</h2>", unsafe_allow_html=True)
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(10))
        time.sleep(3); st.rerun()

    elif fase_serv == 99:
        st.balloons(); st.snow()
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            img_file = "alumna_festejo_uba.png" if podio[0][4] == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 style='color:#D4AF37; font-size:4rem;'>🏆 {podio[0][4]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
            st.markdown("<div class='podio-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]}</div>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("⚖️ En espera de instrucciones del docente...")
        time.sleep(3); st.rerun()
