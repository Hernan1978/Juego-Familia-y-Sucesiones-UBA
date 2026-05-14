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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&family=Lato:wght@300;400&display=swap');
    
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-family: 'Poppins', sans-serif; text-align: center; }
    
    .main .block-container { background: rgba(10, 25, 41, 0.92) !important; padding: 3rem !important; border-radius: 12px !important; border-top: 5px solid #D4AF37; max-width: 1000px !important; margin: auto; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
    
    /* AJUSTE SOLICITADO: Visibilidad del Control de Audiencia */
    [data-testid="stExpander"] { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 8px; }
    [data-testid="stExpander"] p, [data-testid="stExpander"] label, [data-testid="stExpander"] span { color: #000000 !important; text-shadow: none !important; }
    .stDataFrame, [data-testid="stTable"] { background-color: white !important; border-radius: 8px; }
    
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2rem; }
    
    .podio-container { display: flex; flex-direction: column; align-items: center; gap: 15px; margin-top: 30px; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #000 !important; padding: 25px; border-radius: 8px; width: 85%; font-size: 2.2rem; font-weight: 700; border: 1px solid #FFF; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #000 !important; padding: 18px; border-radius: 8px; width: 75%; font-size: 1.6rem; font-weight: 600; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #000 !important; padding: 15px; border-radius: 8px; width: 65%; font-size: 1.3rem; font-weight: 600; }
    
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #E31837; color: white !important; padding: 20px 30px; border-radius: 8px; font-size: 3rem; font-weight: 700; border: 2px solid #D4AF37; z-index: 9999; }
    
    .mensaje-final { color: #D4AF37 !important; font-size: 1.6rem !important; font-style: italic; font-family: 'Lato', sans-serif; margin-top: 40px; border-top: 1px solid rgba(212, 175, 55, 0.3); padding-top: 30px; }
    
    .stButton>button { background-color: #D4AF37 !important; color: #0A1929 !important; font-weight: 700 !important; border: none !important; height: 3.5em; border-radius: 4px !important; }
    .stButton>button:hover { background-color: #F1D592 !important; }
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
    m = st.text_input("Email Académico o Clave:")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR AL TRIBUNAL"):
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

# --- 5. LÓGICA DE DATOS ---
df_global = cargar_datos()
f_info = leer_f()
fase_serv, t_limite = int(f_info[0]), float(f_info[1])
ahora = time.time()

# --- PANEL JUEZ ---
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ ESTRADOS DEL JUEZ</h1>", unsafe_allow_html=True)
    with st.expander("👥 CONTROL DE AUDIENCIA Y BANCO", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.dataframe(df_global[['G', 'A']].rename(columns={'G':'Tit','A':'Nombre'}), use_container_width=True)
            st.download_button("📥 DESCARGAR ACTA (CSV)", df_global.to_csv(index=False), "lexplay_resultados.csv")
        with col_b:
            for k, v in banco.items(): st.write(f"**Cuestión {k}:** {v['q']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        f_sel = st.selectbox("Fase de la Sesión:", [0, 1, 2, 3, 4, 88, 99], format_func=lambda x: {0:"Espera", 1:"Pregunta 1", 2:"Pregunta 2", 3:"Pregunta 3", 4:"Pregunta 4", 88:"RESULTADOS PARCIALES", 99:"RESULTADOS FINALES"}[x])
        if st.button("📢 ACTUALIZAR FASE"): escribir_f(f_sel, "0"); st.rerun()
    with col2:
        t_set = st.number_input("Tiempo (Seg):", 5, 60, 25)
        if st.button("⏱️ INICIAR CRONÓMETRO"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with col3:
        if st.button("⚠️ REINICIAR SISTEMA"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            escribir_f(0,0); st.rerun()
    if st.button("🔄 REFRESCAR VISTA"): st.cache_data.clear(); st.rerun()
    st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False))

# --- PANEL ALUMNO ---
else:
    if st.session_state.f_ok != fase_serv and fase_serv not in [88, 99]: st.session_state.f_ok = -2 
    ha_votado = (st.session_state.f_ok == fase_serv)
    reloj_activo = t_limite > ahora and not ha_votado
    if reloj_activo:
        st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        st.components.v1.html('<iframe src="https://www.soundjay.com/clock/sounds/clock-ticking-4.mp3" allow="autoplay" style="display:none"></iframe>', height=0)
    if fase_serv in banco:
        p = banco[fase_serv]; st.write(f"👤 {st.session_state.user['g']} {st.session_state.user['a']}")
        st.markdown(f"### {p['q']}")
        opcion = st.radio("Seleccione su veredicto:", p["o"], key=f"ans_{fase_serv}", disabled=ha_votado)
        if st.button("DICTAMINAR SENTENCIA", disabled=not (t_limite > ahora) or ha_votado):
            if opcion == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df_u = cargar_datos(); df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False); st.success(f"✅ ¡Correcto! +{pts} Puntos")
            else: st.error("❌ Error en el Veredicto")
            st.session_state.f_ok = fase_serv; st.rerun()
        if reloj_activo: time.sleep(1); st.rerun()
        else: time.sleep(1.5); st.rerun()
    elif fase_serv == 88:
        st.markdown("<h2 class='titulo-oro'>📊 ESCALA PARCIAL</h2>", unsafe_allow_html=True)
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(10))
        time.sleep(3); st.rerun()
    elif fase_serv == 99:
        st.balloons(); st.snow()
        st.components.v1.html('<iframe src="https://www.soundjay.com/human/sounds/applause-01.mp3" allow="autoplay" style="display:none"></iframe>', height=0)
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            st.markdown("<h1 class='titulo-oro'>🏆 SENTENCIA FINAL 🏆</h1>", unsafe_allow_html=True)
            img = "https://raw.githubusercontent.com/fede-999/images/main/ganadora_mujer.png" if podio[0][4] == "Dra." else "https://raw.githubusercontent.com/fede-999/images/main/ganador_hombre.png"
            st.image(img, width=320)
            st.markdown(f"<div class='podio-container'><div class='box-oro'>🥇 ORO: {podio[0][1]}<br>{int(podio[0][3])} PTS</div>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]} ({int(podio[1][3])} PTS)</div>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]} ({int(podio[2][3])} PTS)</div></div>", unsafe_allow_html=True)
            st.markdown("<div class='mensaje-final'>La sesión ha concluido. El Tribunal agradece su participación.<br>¡Felicitaciones a los ganadores!</div>", unsafe_allow_html=True)
    else:
        st.info("⚖️ El Tribunal está deliberando... Espere instrucciones."); time.sleep(2); st.rerun()
    st.divider()
    if st.button("🚪 CERRAR SESIÓN"): st.session_state.user = None; st.rerun()
