import streamlit as st
import pandas as pd
import os
import time
import base64

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# --- 2. FUNCIONES BASE ---
def cargar_datos_seguro():
    # Si no existe o está vacío, devuelve un DF vacío con las columnas necesarias
    if not os.path.exists("d.csv") or os.stat("d.csv").st_size == 0:
        return pd.DataFrame(columns=["E", "A", "F", "P"])
    try:
        return pd.read_csv("d.csv")
    except:
        return pd.DataFrame(columns=["E", "A", "F", "P"])

# --- 3. ESTILOS ---
st.markdown("""<style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; }
    .main .block-container { background: rgba(0, 0, 0, 0.93) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3rem !important; text-transform: uppercase; text-align: center; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; }
    </style>""", unsafe_allow_html=True)

# --- 4. PANEL DEL JUEZ (ACCESO CLAVE) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "derecho2024":
        df = cargar_datos_seguro()
        # Visualización protegida
        if 'A' in df.columns and not df.empty:
            st.write(f"### 👥 Alumnos presentes: {', '.join(df['A'].astype(str).unique())}")
            st.download_button("📥 Descargar Lista", df.to_csv(index=False), "asistencia.csv")
        else:
            st.write("### 👥 Aún no hay alumnos ingresados.")
        
        if st.button("⚠️ REINICIAR"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            st.rerun()
    st.stop()

# --- 5. ACCESO ALUMNOS ---
if st.session_state.get('u') is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m_in = st.text_input("Email Académico:")
    n_in = st.text_input("Nombre y Apellido:")
    if st.button("INGRESAR") and "@" in m_in and n_in:
        # Creamos el archivo si no existe con encabezados
        if not os.path.exists("d.csv"):
            with open("d.csv", "w") as f: f.write("E,A,F,P\n")
        with open("d.csv", "a") as f: f.write(f"{m_in},{n_in},0,0\n")
        st.session_state.u = {"e": m_in, "a": n_in}; st.rerun()
    st.stop()

# --- 6. JUEGO ---
st.write(f"👤 Dr/a. {st.session_state.u['a']}")
st.success("¡Bienvenido al sistema!")
