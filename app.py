import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

SOUNDS = {
    "reloj": "https://www.soundjay.com/clock/sounds/clock-ticking-2.mp3",
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
        .main .block-container {{ 
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(15px); padding: 3rem !important; margin-top: 40px !important; 
            border-radius: 20px !important; border: 1px solid rgba(212, 175, 55, 0.4);
        }}
        h1, h2, h3, h4, p, label, span {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        .stButton>button {{ background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; height: 3.5rem; }}
        .reloj-juez {{ position: fixed; top: 30px; right: 30px; background: #C0392B; color: white !important; padding: 20px 40px; border-radius: 15px; font-size: 4.5rem; border: 4px solid #D4AF37; z-index: 9999; }}
        .oro {{ color: #FFD700 !important; font-size: 5rem !important; text-transform: uppercase; text-shadow: 0 0 15px gold; }}
        .plata {{ color: #C0C0C0 !important; font-size: 3rem !important; }}
        .bronce {{ color: #CD7F32 !important; font-size: 2.5rem !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. GESTIÓN DE ARCHIVOS (ANTI-ERRORES) ---
COLUMNAS = ["E", "A", "F", "P"]

def leer_f():
    if os.path.exists("f.txt"):
        with open("f.txt", "r") as x: return x.read().strip().split(",")
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if not os.path.exists("d.csv"):
        return pd.DataFrame(columns=COLUMNAS)
    try:
        # Cargamos y nos aseguramos de que no haya líneas corruptas
        df = pd.read_csv("d.csv", on_bad_lines='skip')
        # Si por alguna razón faltan columnas, devolvemos un DF vacío con las columnas correctas
        if not all(col in df.columns for col in COLUMNAS):
            return pd.DataFrame(columns=COLUMNAS)
        return df
    except:
        return pd.DataFrame(columns=COLUMNAS)

f_str, t_str = leer_f()
fase, t_limite = int(f_str), float(t_str)
df_global = cargar_datos()
ahora = time.time()

# --- 3. PANEL ADMIN ---
if st.query_params.get("admin") == "true":
    st.markdown("### ⚖️ MONITOR DEL JUEZ")
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with c2:
            dur = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 LARGAR RELOJ"):
                escribir_f(fase, time.time() + dur); st.rerun()
        with c3:
            st.write("")
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                if os.path.exists("f.txt"): os.remove("f.txt")
                st.rerun()

        if 0 < fase < 10:
            st.write("---")
            if not df_global.empty:
                alumnos = df_global[df_global["F"] == 0]["A"].unique()
                votos = df_global[df_global["F"] == fase]["A"].unique()
                faltan = [a for a in alumnos if a not in votos]
                st.subheader(f"Votos: {len(votos)} / {len(alumnos)}")
                col1, col2 = st.columns(2)
                col1.success("VOTARON:\n" + "\n".join(votos))
                col2.warning("FALTAN:\n" + "\n".join(faltan))
    st.write("---")

# --- 4. ACCESO ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.title("🏛️ LEXPLAY UBA")
    m_in = st.text_input("Email:")
    n_in = st.text_input("Nombre:")
    if st.button("INGRESAR"):
        if m_in and n_in:
            # Escribimos con encabezado si el archivo no existe
            headers = not os.path.exists("d.csv")
            df_nuevo = pd.DataFrame([[m_in, n_in, 0, 0]], columns=COLUMNAS)
            df_nuevo.to_csv("d.csv", mode='a', header=headers, index=False)
            st.session_state.u = {"e": m_in, "a": n_in}
            st.rerun()
    st.stop()

# --- 5. LÓGICA ---
# Verificación blindada de voto
ya_voto = False
if not df_global.empty and "E" in df_global.columns:
    ya_voto = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty

reloj_on = (t_limite > ahora)

if reloj_on and not ya_voto:
    st.markdown(f'<div class="reloj-juez">{int(t_limite - ahora)}</div>', unsafe_allow_html=True)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera")
    st.info(f"Dr/a. {st.session_state.u['a']}, aguarde al Juez.")

elif fase == 10:
    st.header("📊 POSICIONES PARCIALES")
    if not df_global.empty:
        top = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(10)
        st.table(top)

elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    st.balloons(); play_audio(SOUNDS["ganador"])
    if not df_global.empty:
        total = df_global.groupby("A")["P"].sum().sort_values(ascending=False).head(3)
        idx = total.index.tolist()
        if len(idx) >= 1: st.markdown(f"<div style='text-align:center;'><p class='oro'>🥇 {idx[0].upper()}</p></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if len(idx) >= 2: c1.markdown(f"<div style='text-align:center;'><p class='plata'>🥈 {idx[1]}</p></div>", unsafe_allow_html=True)
        if len(idx) >= 3: c2.markdown(f"<div style='text-align:center;'><p class='bronce'>🥉 {idx[2]}</p></div>", unsafe_allow_html=True)

else:
    st.header(f"RONDA N° {fase}")
    if ya_voto:
        st.success("✅ Veredicto enviado. Espere al Juez.")
    else:
        banco = {
            1: {"q": "¿Cuál es la legítima de los descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
            2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
            3: {"q": "¿Válido testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Veredicto:", banco[fase]['o'], key=f"r{fase}")
        
        if st.button("DICTAMINAR", disabled=not (reloj_on and not ya_voto)):
            t_rest = int(t_limite - ahora)
            pts = (100 + (t_rest * 2)) if rta == banco[fase]['k'] else 0
            # Guardado usando Pandas para asegurar consistencia de columnas
            pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, pts]], columns=COLUMNAS).to_csv("d.csv", mode='a', header=False, index=False)
            play_audio(SOUNDS["exito"] if pts > 0 else SOUNDS["error"])
            st.rerun()

time.sleep(1); st.rerun()
