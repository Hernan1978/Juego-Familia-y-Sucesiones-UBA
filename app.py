import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# GESTIÓN DE DATOS UNIFICADA
def gestionar_datos(accion="leer", fase=None, tiempo=None):
    archivo = "d.csv"
    columnas = ["E", "A", "F", "P", "G"]
    
    if not os.path.exists(archivo):
        df = pd.DataFrame([["SISTEMA", "CONTROL", 0, 0.0, "0"]], columns=columnas)
        df["P"] = df["P"].astype(float) # Forzar decimales
        df.to_csv(archivo, index=False)
    else:
        try:
            df = pd.read_csv(archivo)
            df["P"] = df["P"].astype(float) # Asegurar que P sea decimal
            if "SISTEMA" not in df["E"].values:
                extra = pd.DataFrame([["SISTEMA", "CONTROL", 0, 0.0, "0"]], columns=columnas)
                df = pd.concat([df, extra], ignore_index=True)
        except:
            df = pd.DataFrame([["SISTEMA", "CONTROL", 0, 0.0, "0"]], columns=columnas)
            df["P"] = df["P"].astype(float)

    if accion == "escribir":
        # Usar .at para evitar problemas de tipos en celdas específicas
        idx_sistema = df[df["E"] == "SISTEMA"].index[0]
        df.at[idx_sistema, "F"] = int(fase)
        df.at[idx_sistema, "P"] = float(tiempo)
        df.to_csv(archivo, index=False)
        return df
    return df

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { 
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
        background-size: cover; background-attachment: fixed; 
    }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, span { font-family: 'Poppins', sans-serif; text-align: center; }
    h2, .stMarkdown h2 {
        color: #FFFFFF !important; font-size: 2.5rem !important; font-weight: 800 !important;
        text-shadow: 3px 3px 10px #000000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000 !important;
    }
    .titulo-oro { 
        color: #FFFFFF !important; font-size: 3.8rem !important; font-weight: 800; text-transform: uppercase; 
        text-shadow: 0 0 10px #D4AF37, 0 0 20px #D4AF37, 3px 3px 5px #000 !important; 
    }
    label, [data-testid="stWidgetLabel"] p, .stSelectbox label, .stNumberInput label, .stRadio label, [data-testid="stMarkdownContainer"] p {
        color: #CCFF00 !important; font-weight: 800 !important; font-size: 1.2rem !important;
        text-shadow: 2px 2px 4px #000 !important;
    }
    .reloj-container {
        background-color: rgba(0, 0, 0, 0.8); color: #FF4B4B; font-size: 4rem; font-weight: 800;
        padding: 10px 30px; border-radius: 15px; border: 4px solid #FF4B4B; display: inline-block;
        margin: 20px 0; text-shadow: 0 0 10px #FF4B4B;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] b {
        color: #FFFFFF !important; font-weight: 600 !important; text-shadow: 1px 1px 2px #000000 !important;
    }
    [data-testid="stTable"], .stTable, [data-testid="stExpander"] { background-color: rgba(0, 0, 0, 0.6) !important; border-radius: 10px; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 800 !important; border: 2px solid #000 !important; width: 100%; }
    
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #FFF !important; padding: 25px; border-radius: 15px; width: 85%; font-size: 2.5rem; font-weight: 800; border: 4px solid #FFF; text-shadow: 2px 2px 5px #000 !important; margin: auto; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #FFF !important; padding: 15px; border-radius: 12px; width: 75%; font-size: 1.8rem; font-weight: 700; margin: auto; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #FFF !important; padding: 12px; border-radius: 10px; width: 65%; font-size: 1.5rem; font-weight: 700; margin: auto; }
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
            df = gestionar_datos()
            if m not in df['E'].values:
                with open("d.csv", "a") as f:
                    f.write(f"{m},{n},0,0.0,{g}\n")
        st.rerun()
    st.stop()

# --- 5. LÓGICA ---
df_global = gestionar_datos()
info_sistema = df_global[df_global["E"] == "SISTEMA"].iloc[0]
fase_serv = int(info_sistema["F"])
t_limite = float(info_sistema["P"])
ahora = time.time()
fases_nombres = {0: "Inicio", 1: "P1", 2: "P2", 3: "P3", 4: "P4", 88: "Parcial", 99: "FINAL"}

if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)
    
    with st.expander("📚 VER PREGUNTAS Y AUDIENCIA", expanded=False):
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("<b>Banco:</b>", unsafe_allow_html=True)
            for k,v in banco.items(): st.write(f"**{k}.** {v['q']}")
        with c_p2:
            st.markdown("<b>Alumnos en Sala:</b>", unsafe_allow_html=True)
            st.table(df_global[df_global["E"] != "SISTEMA"][['G', 'A']])

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_fase = st.selectbox("Cambiar Pregunta:", options=list(fases_nombres.keys()), format_func=lambda x: fases_nombres[x], key="sel_fase")
        if st.button("📢 ACTUALIZAR FASE", key="btn_fase"):
            gestionar_datos("escribir", fase=op_fase, tiempo=0.0)
            st.rerun()
    with c2:
        t_set = st.number_input("Segundos:", 5, 60, 25, key="num_tiempo")
        if st.button("⏱️ INICIAR RELOJ", key="btn_reloj"):
            gestionar_datos("escribir", fase=fase_serv, tiempo=time.time() + t_set)
            st.rerun()
    with c3:
        if st.button("🔄 REFRESCAR", key="btn_refrescar"): st.rerun()
    with c4:
        if st.button("⚠️ RESET", key="btn_reset"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            st.rerun()
    
    st.table(df_global[df_global["E"] != "SISTEMA"][['G', 'A', 'P']].sort_values(by='P', ascending=False))

else:
    # --- PANTALLA ALUMNO ---
    if fase_serv == 99:
        st.balloons(); st.snow()
        podio = df_global[df_global["E"] != "SISTEMA"].sort_values(by="P", ascending=False).head(3).values.tolist()
        if podio:
            genero_ganador = podio[0][4]
            img_file = "alumna_festejo_uba.png" if genero_ganador == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro'>🏆 {podio[0][4]} {podio[0][1]} 🏆</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {podio[0][1]} ({int(podio[0][3])} PTS)</div><br>", unsafe_allow_html=True)
            if len(podio) > 1: st.markdown(f"<div class='box-plata'>🥈 PLATA: {podio[1][1]}</div><br>", unsafe_allow_html=True)
            if len(podio) > 2: st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {podio[2][1]}</div>", unsafe_allow_html=True)
            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.user = None
                st.rerun()
    elif fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora
        ya_envio = st.session_state.get('enviado', False)
        if st.session_state.f_voto != fase_serv: st.session_state.enviado = False
        
        st.markdown(f"## {p['q']}")
        
        if t_limite == 0:
            st.warning("⚖️ El Tribunal aún no ha habilitado la votación. Espere...")
            voto_bloqueado = True
        elif reloj_on and not ya_envio:
            secs_restantes = int(t_limite - ahora)
            st.markdown(f"<div style='text-align:center;'><div class='reloj-container'>⏱️ {secs_restantes}s</div></div>", unsafe_allow_html=True)
            voto_bloqueado = False
            time.sleep(1)
            st.rerun()
        elif not ya_envio and not reloj_on:
            st.markdown("<div style='text-align:center;'><div class='reloj-container' style='color:gray; border-color:gray;'>⌛ TIEMPO AGOTADO</div></div>", unsafe_allow_html=True)
            voto_bloqueado = True
        else:
            voto_bloqueado = True

        opcion = st.radio("Dictamen:", p["o"], disabled=voto_bloqueado or ya_envio)
        
        if st.button("ENVIAR SENTENCIA", disabled=voto_bloqueado or ya_envio):
            if opcion == p["k"]:
                pts = 10 + min(int(t_limite - ahora), 10)
                df_u = gestionar_datos()
                df_u.loc[df_u['E'] == st.session_state.user['e'], 'P'] += pts
                df_u.to_csv("d.csv", index=False)
                st.success("✅ REGISTRADO")
            else: st.error("❌ INCORRECTO")
            st.session_state.enviado = True
            st.session_state.f_voto = fase_serv
            st.rerun()
        
        if ya_envio:
            st.info("✅ Sentencia enviada correctamente.")
            time.sleep(2)
            st.rerun()
            
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        time.sleep(2)
        st.rerun()
