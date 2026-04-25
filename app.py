import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ESTÉTICA (LOOK & FEEL) ---
st.set_page_config(page_title="LexPlay: Desafío Jurídico", layout="wide")

def aplicar_estilo():
    # URL de imagen de fondo (puedes cambiarla por una de un tribunal o biblioteca)
    fondo_url = "https://www.derecho.uba.ar/derechoaldia/notas/preguntas-frecuentes/+7888"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .stButton>button {{
            width: 100%;
            border-radius: 20px;
            height: 3em;
            background-color: #1A3A5A;
            color: white;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. FUNCIONES DE PERSISTENCIA ---
def set_estado(n):
    with open("estado.txt", "w") as f: f.write(str(n))

def get_estado():
    if not os.path.exists("estado.txt"): return 0
    with open("estado.txt", "r") as f: return int(f.read())

# --- 3. PANEL DE CONTROL (PARA EL PROFESOR) ---
with st.sidebar:
    st.header("🛂 Mando del Docente")
    pwd = st.text_input("Contraseña", type="password")
    
    if pwd == "derecho2024":
        st.subheader("Configuración")
        cant_preguntas = st.slider("Cantidad de preguntas a usar:", 1, 5, 3)
        
        opciones_fase = ["Registro (Espera)"] + [f"Pregunta {i+1}" for i in range(cant_preguntas)] + ["Podio Final"]
        fase_sel = st.selectbox("Cambiar a fase:", opciones_fase)
        
        if st.button("Lanzar Fase Sincrónica"):
            if "Registro" in fase_sel: set_estado(0)
            elif "Podio" in fase_sel: set_estado(99)
            else: set_estado(int(fase_sel.split(" ")[1]))
            st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ Reiniciar Juego (Borrar Datos)"):
            if os.path.exists("data.csv"): os.remove("data.csv")
            set_estado(0)
            st.rerun()

# --- 4. LÓGICA PRINCIPAL (ALUMNOS) ---
st.title("⚖️ LexPlay: Familia y Sucesiones")

# PASO A: IDENTIFICACIÓN
col1, col2 = st.columns(2)
email = col1.text_input("📧 Mail Institucional:")
alias = col2.text_input("🎭 Alias (Para el Ranking):")

if not email or not alias or "@" not in email:
    st.info("Por favor, ingresa tus datos para validar tu presencia en los estrados.")
    st.stop()

# PASO B: ESTADO DEL JUEGO
fase = get_estado()

# FASE 0: ESPERA
if fase == 0:
    st.warning(f"Hola {alias}, estamos esperando que el Juez abra la sesión...")
    # Ranking provisorio para que vean quiénes se van sumando
    if os.path.exists("data.csv"):
        st.subheader("Ranking Provisorio")
        df_prov = pd.read_csv("data.csv")
        st.dataframe(df_prov.groupby("Alias")["Puntos"].sum().sort_values(ascending=False))
    time.sleep(3)
    st.rerun()

# FASES DE PREGUNTAS (1 a 5)
elif 1 <= fase <= 5:
    # Definición de preguntas (puedes editar los textos aquí)
    banco_preguntas = {
        1: {"q": "¿Cuál es la legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
        2: {"q": "¿Plazo para impugnar la filiación?", "op": ["1 año", "2 años", "No prescribe"], "ok": "1 año"},
        3: {"q": "¿Es válida la herencia futura?", "op": ["Siempre", "Nunca", "Solo en pactos excepcionales"], "ok": "Solo en pactos excepcionales"},
        # Puedes seguir agregando hasta 5...
    }
    
    pregunta = banco_preguntas.get(fase, {"q": "Pregunta no configurada", "op": ["A", "B"], "ok": "A"})
    
    st.header(f"Pregunta {fase}")
    st.write(f"### {pregunta['q']}")
    
    # Aquí puedes insertar una imagen si quisieras con st.image()
    
    rta = st.radio("Seleccione su defensa:", pregunta["op"])
    
    if st.button("Dictar Sentencia (Enviar)"):
        puntos = 100 if rta == pregunta["ok"] else 0
        df = pd.DataFrame([[email, alias, puntos, fase]], columns=["Email", "Alias", "Puntos", "Ronda"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Voto registrado! Espera a que el profesor avance.")

# FASE 99: PODIO FINAL Y CELEBRACIÓN
elif fase == 99:
    st.header("🏆 Veredicto Final: El Podio")
    if os.path.exists("data.csv"):
        df_final = pd.read_csv("data.csv")
        ranking = df_final.groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        
        # Mostrar el ganador con efectos
        ganador_alias = ranking.index[0]
        st.balloons() # Globos animados cayendo
        st.snow()     # Efecto extra de celebración
        
        st.success(f"🥇 ¡EL GANADOR ES: {ganador_alias}!")
        
        # Mostrar tabla estilizada
        st.table(ranking)
    else:
        st.error("No se registraron datos en este juicio.")
    
    if st.button("Volver al inicio"):
        set_estado(0)
        st.rerun()
