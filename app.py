import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    cols = ["E", "A", "F", "P", "G"]
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=cols)
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=cols)

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

# --- 2. ESTILOS (BIBLIOTECA + LETRAS BLANCAS) ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { 
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); 
        background-size: cover; background-attachment: fixed; 
    }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { 
        color: #FFFFFF !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px #000000 !important; 
        text-align: center; 
    }
    .main .block-container { 
        background: rgba(0, 0, 0, 0.85) !important; 
        padding: 2.5rem !important; 
        border-radius: 20px !important; 
        border: 2px solid #D4AF37; 
        max-width: 950px !important; 
        margin: auto; 
    }
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; text-transform: uppercase; }
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: #000000 !important; 
        font-weight: 900 !important; 
        width: 100%; border: 1px solid #FFFFFF; 
    }
    .podio { 
        font-size: 2.5rem; margin: 10px; padding: 15px; 
        border-radius: 15px; border: 2px solid #D4AF37; 
        background: rgba(212, 175, 55, 0.2); width: 85%; margin: auto; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS Y PREGUNTAS ---
df_global = cargar_datos()
f_data = leer_f()
fase_servidor, t_limite = int(f_data[0]), float(f_data[1])
ahora = time.time()

banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. PANEL DEL JUEZ ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if st.text_input("Clave Maestro:", type="password") == "derecho2024":
        if not df_global.empty:
            st.write(f"👥 **Participantes:** {', '.join(df_global['A'].unique())}")
            st.download_button("📥 DESCARGAR ASISTENCIA", df_global.to_csv(index=False), "asistencia.csv")
        
        with st.expander("📖 BANCO DE PREGUNTAS"):
            for k, v in banco.items(): st.write(f"**{k}.** {v['q']} (R: {v['k']})")

        col1, col2, col3 = st.columns(3)
        with col1:
            f_sel = st.selectbox("Lanzar Fase:", [0, 1, 2, 3, 4, 99], index=0)
            if st.button("CAMBIAR FASE"): escribir_f(f_sel, 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos Reloj:", 5, 60, 25)
            if st.button("INICIAR RELOJ"): escribir_f(fase_servidor, ahora + t_set); st.rerun()
        with col3:
            if st.button("REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f(0, 0); st.rerun()
    st.stop()

# --- 5. ACCESO ALUMNOS ---
if 'u' not in st.session_state: st.session_state.u = None
if 'respondido_fase' not in st.session_state: st.session_state.respondido_fase = -1

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email Académico:")
    n = st.text_input("Nombre y Apellido:")
    g = st.radio("Título:", ["Dr.", "Dra."])
    if st.button("INGRESAR"):
        if m and n:
            if not os.path.exists("d.csv"):
                with open("d.csv", "w") as f: f.write("E,A,F,P,G\n")
            with open("d.csv", "a") as f: f.write(f"{m},{n},0,0,{g}\n")
            st.session_state.u = {"e": m, "a": n, "g": g}; st.rerun()
    st.stop()

# --- 6. JUEGO ---
st.write(f"👤 {st.session_state.u['g']} {st.session_state.u['a']}")

if t_limite > ahora:
    st.markdown(f'<div style="position:fixed; top:30px; right:30px; background:#C0392B; color:white; padding:20px; border-radius:15px; font-size:4rem; border:4px solid #D4AF37; z-index:1000;">{int(t_limite-ahora)}</div>', unsafe_allow_html=True)
    time.sleep(1); st.rerun()

if fase_servidor in banco:
    if st.session_state.respondido_fase != fase_servidor:
        p = banco[fase_servidor]
        st.markdown(f"## {p['q']}")
        rta = st.radio("Veredicto:", p["o"], key=f"f{fase_servidor}")
        if st.button("ENVIAR RESPUESTA"):
            if rta == p["k"]:
                bono = int(max(0, t_limite - ahora))
                puntos = 10 + min(bono, 10)
                df_up = cargar_datos()
                df_up.loc[df_up['E'] == st.session_state.u['e'], 'P'] += puntos
                df_up.to_csv("d.csv", index=False)
                st.success(f"✅ ¡Correcto! +{puntos} pts")
            else: st.error("❌ Incorrecto")
            st.session_state.respondido_fase = fase_servidor
            time.sleep(1.5); st.rerun()
    else:
        st.info("⚖️ Respuesta registrada. Espere la siguiente fase...")
        time.sleep(2); st.rerun()

elif fase_servidor == 99:
    # --- SENTENCIA FINAL ---
    st.balloons()
    st.markdown("<h1 class='titulo-oro'>🚀 SENTENCIA FINAL 🚀</h1>", unsafe_allow_html=True)
    
    if not df_global.empty:
        # Calculamos el ganador real
        res = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        ganador_nombre = res[0][1]
        ganador_titulo = res[0][4]
        
        # MOSTRAR IMAGEN SEGÚN GÉNERO
        if ganador_titulo == "Dra.":
            # Imagen de la mujer festejando con cohetes
            st.image("https://raw.githubusercontent.com/fede-999/images/main/ganadora_mujer.png", use_column_width=True)
        else:
            # Imagen del hombre festejando con cohetes
            st.image("https://raw.githubusercontent.com/fede-999/images/main/ganador_hombre.png", use_column_width=True)
        
        # PODIO CON MEDALLAS
        st.markdown(f"<div class='podio'>🥇 1er Puesto: {ganador_nombre} (ORO)</div>", unsafe_allow_html=True)
        if len(res) > 1: st.markdown(f"<div class='podio' style='border-color:silver;'>🥈 2do Puesto: {res[1][1]} (PLATA)</div>", unsafe_allow_html=True)
        if len(res) > 2: st.markdown(f"<div class='podio' style='border-color:#CD7F32;'>🥉 3er Puesto: {res[2][1]} (BRONCE)</div>", unsafe_allow_html=True)
        
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/human/sounds/applause-01.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)

if fase_servidor != 99 and not df_global.empty:
    st.divider()
    st.markdown("### 📊 Competencia en Vivo")
    st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False).rename(columns={'A':'Dr/a.','P':'Pts'}))
