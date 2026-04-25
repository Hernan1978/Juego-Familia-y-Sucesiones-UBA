import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070" 
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        .main .block-container {{ background-color: rgba(0, 0, 0, 0.85); padding: 3rem; border-radius: 20px; border: 2px solid #D4AF37; }}
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stMarkdownContainer"] p {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px #000000;
            font-size: 1.3rem !important;
        }}
        .stButton>button {{ background-color: #C0392B !important; color: white !important; font-size: 1.5rem !important; width: 100%; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo firmado pero escrito a máquina?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"},
    4: {"q": "¿El cónyuge hereda sobre los gananciales en concurrencia con hijos?", "op": ["Sí", "No", "La mitad"], "ok": "No"},
    5: {"q": "¿Pacto sobre herencia futura: Art. 1010 es la excepción?", "op": ["Nunca", "Sí, es posible", "Siempre"], "ok": "Sí, es posible"},
    6: {"q": "¿La indignidad se purga con 3 años de posesión?", "op": ["Sí", "No", "Son 10 años"], "ok": "Sí"}
}

# --- 3. LOGIN ÚNICO ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m = st.text_input("Email Institucional:")
    a = st.text_input("Alias para el Ranking:")
    if st.button("INGRESAR AL JUICIO"):
        if m and a and "@" in m:
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
        else:
            st.error("Datos incompletos.")
    st.stop()

# --- 4. CONTROL ---
def set_fase(n):
    with open("fase.txt", "w") as f: f.write(str(n))

def get_fase():
    if not os.path.exists("fase.txt"): return 0
    with open("fase.txt", "r") as f:
        try: return int(f.read())
        except: return 0

with st.sidebar:
    st.header("🛂 MANDO")
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        opc = ["Registro"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio Final"]
        sel = st.selectbox("Fase:", opc)
        if st.button("LANZAR"):
            if "Registro" in sel: set_fase(0)
            elif "Podio" in sel: set_fase(99)
            else: set_fase(int(sel.split(" ")[1]))
            st.rerun()

# --- 5. JUEGO ---
f = get_fase()
if f == 0:
    st.header(f"🏛️ Sala de Espera: {st.session_state.usuario['alias']}")
    st.write("Aguarde el inicio del debate.")
    time.sleep(3)
    st.rerun()
elif f in banco:
    preg = banco[f]
    st.header(f"Ronda {f}")
    st.write(f"### {preg['q']}")
    rta = st.radio("Respuesta:", preg['op'], key=f"r{f}")
    if st.button("ENVIAR VEREDICTO"):
        p = 100 if rta == preg['ok'] else 0
        df = pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], p]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Voto registrado!")
elif f == 99:
    st.balloons()
    st.header("🏆 PODIO FINAL")
    if os.path.exists("data.csv"):
        datos = pd.read_csv("data.csv")
        st.table(datos.groupby("Alias")["Puntos"].sum().sort_values(ascending=False))
    else:
        st.write("No hay registros.")
