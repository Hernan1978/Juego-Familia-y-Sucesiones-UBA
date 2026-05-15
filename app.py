import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    try: 
        df = pd.read_csv("d.csv")
        return df
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
    
    [data-testid="stTable"], .stDataFrame, [data-testid="stDataFrame"], [data-testid="stExpander"] { background-color: white !important; border-radius: 8px !important; }
    [data-testid="stTable"] td, [data-testid="stTable"] th, [data-testid="stTable"] tr, .stDataFrame div, .stDataFrame span, .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] span, [data-testid="stExpander"] label {
        color: #000000 !important; font-weight: 700 !important; text-shadow: none !important;
    }

    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; font-weight: 700; text-transform: uppercase; }
    .podio-container { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-top: 20px; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #000 !important; padding: 20px; border-radius: 8px; width: 80%; font-size: 2rem; font-weight: 700; border: 2px solid white; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #000 !important; padding: 15px; border-radius: 8px; width: 70%; font-size: 1.5rem; font-weight: 600; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #000 !important; padding: 12px; border-radius: 8px; width: 60%; font-size: 1.2rem; font-weight: 600; }
    .mensaje-final { color: #FFD700 !important; font-size: 2.2rem !important; font-weight: 800 !important; text-shadow: 2px 2px 10px #000000 !important; margin-top: 30px; padding: 20px; border-top: 3px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None

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

# --- 5. DATOS ACTUALES ---
df_global = cargar_datos()
f_info = leer_f()
fase_serv, t_limite = int(f_info[0]), float(f_info[1])
ahora = time.time()

# --- PANEL JUEZ ---
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL TRIBUNAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        f_sel = st.selectbox("Fase:", [0, 1, 2, 3, 4, 88, 99], index=0)
        if st.button("📢 CAMBIAR FASE"): escribir_f(f_sel, "0"); st.rerun()
    with col2:
        t_set = st.number_input("Tiempo (seg):", 5, 60, 25)
        if st.button("⏱️ INICIAR TIEMPO"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
    with col3:
        if st.button("🔄 REFRESCAR"): st.rerun()
    st.table(df_global[['G', 'A', 'P']].sort_values(by='P', ascending=False))

# --- PANEL ALUMNO ---
else:
    if fase_serv in banco:
        st.write(f"👤 {st.session_state.user['g']} {st.session_state.user['a']}")
        p = banco[fase_serv]
        st.markdown(f"### {p['q']}")
        opcion = st.radio("Respuesta:", p["o"])
        if st.button("ENVIAR SENTENCIA") and ahora < t_limite:
            if opcion == p["k"]:
                pts = 10 + int(t_limite - ahora)
                df_u = cargar_datos()
                df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False)
                st.success(f"¡Correcto! +{pts} puntos")
            else: st.error("Respuesta incorrecta")
            time.sleep(1); st.rerun()
        if ahora < t_limite:
            st.markdown(f"⏱️ **TIEMPO: {int(t_limite - ahora)}s**")
            time.sleep(1); st.rerun()
        else:
            st.warning("Esperando siguiente fase..."); time.sleep(2); st.rerun()

    elif fase_serv == 88:
        st.markdown("<h2 class='titulo-oro'>📊 RESULTADOS PARCIALES</h2>", unsafe_allow_html=True)
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(10))
        time.sleep(3); st.rerun()

    elif fase_serv == 99:
        st.balloons(); st.snow()
        st.markdown("<h1 class='titulo-oro'>🏆 SENTENCIA FINAL 🏆</h1>", unsafe_allow_html=True)
        
        # --- LÓGICA DE FOTO FORZADA ---
        podio = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        
        # Determinamos la foto por el ganador (o por defecto Dra. si no hay datos)
        if len(podio) > 0 and podio[0][4] == "Dr.":
            foto_url = "https://raw.githubusercontent.com/fede-999/images/main/alumno_festejo_uba.png"
        else:
            foto_url = "https://raw.githubusercontent.com/fede-999/images/main/alumna_festejo_uba.png"
        
        st.image(foto_url, use_container_width=True)

        # MOSTRAR EL PODIO SI HAY DATOS
        if len(podio) > 0:
            st.markdown(f"<div class='podio-container'><div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]} ({int(podio[1][3])} PTS)</div>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]} ({int(podio[2][3])} PTS)</div></div>", unsafe_allow_html=True)

        # FRASE FINAL SIEMPRE VISIBLE
        st.markdown("<div class='mensaje-final'>¡EDUCACIÓN PÚBLICA, DE CALIDAD Y GRATUITA!</div>", unsafe_allow_html=True)
        
    else:
        st.info("⚖️ Esperando al Tribunal..."); time.sleep(2); st.rerun()
