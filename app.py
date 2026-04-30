import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

SOUNDS = {
    "exito": "https://www.myinstants.com/media/sounds/correct-answer.mp3",
    "error": "https://www.myinstants.com/media/sounds/eso-tuvo-que-doler-oficina.mp3",
    "ganador": "https://www.myinstants.com/media/sounds/tada_6.mp3"
}

def play_audio(url):
    st.components.v1.html(f"<audio autoplay><source src='{url}' type='audio/mp3'></audio>", height=0)

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        /* Contenedor con más opacidad para lectura */
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.92) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; margin-top: 40px !important; 
            border-radius: 20px !important; border: 2px solid #D4AF37;
        }}

        /* TEXTOS MEJORADOS: Sombreado para que resalten */
        h1, h2, h3, h4, p, label, span, .stMarkdown {{ 
            color: #FFFFFF !important; 
            font-weight: 800 !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        
        .titulo-oro {{ color: #D4AF37 !important; font-size: 2.5rem !important; text-align: center; margin-bottom: 20px; }}
        
        /* Estilo para los botones */
        .stButton>button {{ 
            background-color: #D4AF37 !important; color: #000000 !important; 
            font-weight: 900 !important; font-size: 1.2rem !important;
            border: 2px solid #FFFFFF !important;
        }}

        .reloj-juez {{ 
            position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; 
            padding: 20px 40px; border-radius: 15px; font-size: 4.5rem; border: 4px solid #D4AF37; z-index: 9999; 
        }}
        
        .usuario-fijo {{
            background: rgba(212, 175, 55, 0.2); padding: 10px; border-radius: 10px;
            border: 1px solid #D4AF37; margin-bottom: 20px; text-align: right;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE ARCHIVOS ---
def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E","A","F","P"])
    try: return pd.read_csv("d.csv", on_bad_lines='skip')
    except: return pd.DataFrame(columns=["E","A","F","P"])

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMINISTRADOR ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DE CONTROL DEL JUEZ</h1>", unsafe_allow_html=True)
    clave = st.text_input("Clave Maestra:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Cambiar Etapa:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("ACTUALIZAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Tiempo (seg):", 5, 60, 25)
            if st.button("🚀 LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()
        
        # Monitor de Votos con Nombres
        if 0 < fase < 10:
            st.write("---")
            alumnos_inscriptos = df_global[df_global["F"] == 0]["A"].unique()
            quienes_votaron = df_global[df_global["F"] == fase]["A"].unique()
            faltan = [a for a in alumnos_inscriptos if a not in quienes_votaron]
            
            st.subheader(f"Estado de la Audiencia (Ronda {fase})")
            col_v, col_f = st.columns(2)
            with col_v:
                st.success(f"Votaron ({len(quienes_votaron)})")
                for v in quienes_votaron: st.write(f"✅ {v}")
            with col_f:
                st.warning(f"Faltan ({len(faltan)})")
                for f in faltan: st.write(f"⏳ {f}")

# --- 4. ACCESO ALUMNO ---
if 'u' not in st.session_state: st.session_state.u = None

if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ TRIBUNAL LEXPLAY UBA</h1>", unsafe_allow_html=True)
    mail = st.text_input("Email Institucional (@derecho.uba.ar):")
    nombre = st.text_input("Nombre y Apellido Completo:")
    if st.button("INGRESAR A LA SALA"):
        if mail and nombre:
            pd.DataFrame([[mail, nombre, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": mail, "a": nombre}
            st.rerun()
    st.stop()

# --- 5. INTERFAZ DE PARTICIPANTE ---
st.markdown(f"<div class='usuario-fijo'>👤 Participante: <b>{st.session_state.u['a']}</b></div>", unsafe_allow_html=True)

ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
reloj_on = (t_limite > ahora)

if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.write("Aguarde a que el Juez abra el debate.")
elif fase == 10:
    st.header("📊 RESULTADOS PARCIALES")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    st.balloons()
    play_audio(SOUNDS["ganador"])
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        res = total.index.tolist()
        if len(res) >= 1: st.markdown(f"<p style='color:gold; font-size:3rem; text-align:center;'>🥇 {res[0]}</p>", unsafe_allow_html=True)
        if len(res) >= 2: st.markdown(f"<p style='color:silver; font-size:2rem; text-align:center;'>🥈 {res[1]}</p>", unsafe_allow_html=True)
else:
    # RONDA DE PREGUNTAS
    if reloj_on and not ya_voto:
        st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

    banco = {
        1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
        2: {"q": "¿Cuál es el plazo para aceptar la herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
        3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
    }
    
    st.write(f"### {banco[fase]['q']}")
    
    # La variable rta siempre existe para evitar errores
    rta = st.radio("Seleccione su dictamen:", banco[fase]['o'], disabled=ya_voto or not reloj_on)
    
    # BOTÓN DE ACCIÓN REFORZADO
    if ya_voto:
        st.success("✅ Veredicto registrado. Aguarde a que el Juez cierre la ronda.")
    else:
        # El botón solo se habilita si el reloj está corriendo
        if st.button("DICTAMINAR", disabled=not reloj_on):
            t_restante = int(t_limite - ahora)
            pts = (100 + (t_restante * 2)) if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            play_audio(SOUNDS["exito"] if pts > 0 else SOUNDS["error"])
            st.rerun()

# Refresco para detectar cambios del Juez
time.sleep(1); st.rerun()
