import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# Función de carga sin cache para asegurar frescura de datos
def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    return pd.read_csv("d.csv")

def leer_f():
    if not os.path.exists("f.txt"): return ["0", "0"]
    try:
        with open("f.txt", "r") as x:
            return x.read().strip().split(",")
    except: return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x:
        x.write(f"{fase},{t_limite}")
    st.cache_data.clear() # Limpieza total para que el docente refresque

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center; }
    .main .block-container { background: rgba(0, 0, 0, 0.85) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 900px !important; margin: auto; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; }
    .reloj-float { position: fixed; top: 10px; right: 10px; background: #C0392B; color: white !important; padding: 15px; border-radius: 10px; font-size: 2.5rem; border: 3px solid #D4AF37; z-index: 9999; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; height: 3em; }
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
if 'f_ok' not in st.session_state: st.session_state.f_ok = -1

if st.session_state.user is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Clave o Email:")
    n = st.text_input("Nombre:")
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

# --- 5. DATA ACTUAL ---
df_global = cargar_datos()
f_info = leer_f()
fase_serv, t_limite = int(f_info[0]), float(f_info[1])
ahora = time.time()

# --- PANEL JUEZ ---
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        f_sel = st.selectbox("Elegir Fase:", [0, 1, 2, 3, 4, 88, 99], 
                             format_func=lambda x: {0:"Espera", 1:"P1", 2:"P2", 3:"P3", 4:"P4", 88:"PARCIAL", 99:"FINAL"}[x])
        if st.button("📢 CAMBIAR PREGUNTA"): escribir_f(f_sel, "0"); st.rerun()
        
        t_set = st.number_input("Segundos:", 5, 60, 20)
        if st.button("⏱️ ACTIVAR RELOJ"): escribir_f(fase_serv, str(time.time() + t_set)); st.rerun()
        
    with col2:
        if st.button("🔄 REFRESCAR RANKING"): st.rerun()
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(10))
        st.download_button("📥 ASISTENCIA", df_global.to_csv(index=False), "asistencia.csv")

# --- PANEL ALUMNO ---
else:
    # Sincronización de fase
    if st.session_state.f_ok != fase_serv and fase_serv not in [88, 99]:
        st.session_state.f_ok = -2

    ha_votado = (st.session_state.f_ok == fase_serv)
    reloj_activo = t_limite > ahora and not ha_votado

    if reloj_activo:
        st.markdown(f'<div class="reloj-float">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)
        st.components.v1.html('<audio autoplay loop><source src="https://www.soundjay.com/clock/sounds/clock-ticking-4.mp3" type="audio/mp3"></audio>', height=0)

    if fase_serv in banco:
        p = banco[fase_serv]
        st.write(f"👤 {st.session_state.user['g']} {st.session_state.user['a']}")
        st.markdown(f"## {p['q']}")
        
        opcion = st.radio("Veredicto:", p["o"], key=f"ans_{fase_serv}", disabled=ha_votado)
        
        if st.button("ENVIAR RESPUESTA", disabled=not (t_limite > ahora) or ha_votado):
            if opcion == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df_u = cargar_datos()
                df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False)
                st.success(f"¡Correcto! +{pts}")
            else: st.error("Incorrecto")
            st.session_state.f_ok = fase_serv
            st.rerun()

        # Solo refresca si el reloj está corriendo. Si no, espera tranquilo.
        if reloj_activo:
            time.sleep(1)
            st.rerun()
        elif not ha_votado:
            time.sleep(2)
            st.rerun()

    elif fase_serv == 88:
        st.markdown("### 📊 POSICIONES PARCIALES")
        st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).head(5))
        time.sleep(3); st.rerun()

    elif fase_serv == 99:
        st.balloons()
        st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/human/sounds/applause-01.mp3" type="audio/mp3"></audio>', height=0)
        res = df_global.sort_values(by="P", ascending=False).head(1).values.tolist()
        if res:
            img = "https://raw.githubusercontent.com/fede-999/images/main/ganadora_mujer.png" if res[0][4] == "Dra." else "https://raw.githubusercontent.com/fede-999/images/main/ganador_hombre.png"
            st.image(img, width=300)
            st.markdown(f"<h2 style='color:#D4AF37'>🥇 {res[0][1]}</h2>", unsafe_allow_html=True)
    else:
        st.info("Esperando inicio...")
        time.sleep(2); st.rerun()

    if st.button("🚪 SALIR"):
        st.session_state.user = None
        st.rerun()
