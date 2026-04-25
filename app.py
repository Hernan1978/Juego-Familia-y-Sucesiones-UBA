import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.85);
            padding: 3rem;
            border-radius: 20px;
            border: 2px solid #D4AF37;
        }}
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stMarkdownContainer"] p, .stRadio label {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px #000000 !important;
            font-size: 1.4rem !important;
            font-weight: bold !important;
        }}
        .stButton>button {{
            background-color: #C0392B !important;
            color: white !important;
            font-size: 1.5rem !important;
            width: 100%;
            height: 4rem;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 0.9) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo escrito a máquina pero firmado?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"},
    4: {"q": "¿El cónyuge hereda sobre los gananciales con hijos?", "op": ["Sí", "No", "Solo la mitad"], "ok": "No"},
    5: {"q": "¿Es posible el pacto sobre herencia futura (Art. 1010)?", "op": ["Nunca", "Sí, excepcionalmente", "Siempre"], "ok": "Sí, excepcionalmente"},
    6: {"q": "¿La indignidad se purga con 3 años de posesión?", "op": ["Sí", "No", "Son 10 años"], "ok": "Sí"}
}

# --- 3. FUNCIONES DE PERSISTENCIA ---
def set_fase(n):
    with open("fase.txt", "w") as f:
        f.write(str(n))

def get_fase():
    if not os.path.exists("fase.txt"):
        return 0
    try:
        with open("fase.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0

# --- 4. LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS")
    m = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR"):
        if m and a:
            st.session_state.usuario = {"mail": m, "alias": a}
            st.rerun()
        else:
            st.error("Completar datos")
    st.stop()

# --- 5. PANEL DOCENTE (Barra Lateral) ---
with st.sidebar:
    st.header("🛂 MANDO")
    clave = st.text_input("Clave:", type="password")
    if clave == "derecho2024":
        opciones = ["Registro"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio"]
        sel = st.selectbox("Cambiar a:", opciones)
        if st.button("LANZAR FASE"):
            if "Registro" in sel: set_fase(0)
            elif "Podio" in sel: set_fase(99)
            else: set_fase(int(sel.split(" ")[1]))
            st.rerun()

# --- 6. JUEGO ---
fase = get_fase()

if fase == 0:
    st.header(f"🏛️ Esperando inicio... {st.session_state.usuario['alias']}")
    time.sleep(3)
    st.rerun()

elif fase in banco:
    p = banco[fase]
    st.header(f"Ronda {fase}")
    st.write(f"### {p['q']}")
    rta = st.radio("Respuesta:", p['op'], key=f"r{fase}")
    if st.button("ENVIAR"):
        pts = 100 if rta == p['ok'] else 0
        df = pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], pts]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("Voto registrado")

elif fase == 99:
    st.balloons()
    st.header("🏆 PODIO FINAL")
    if os.path.exists("data.csv"):
        datos = pd.read_csv("data.csv")
        st.table(datos.groupby("Alias")["Puntos"].sum().sort_values(ascending=False))
    else:
        st.write("Sin datos")
            background-color: #C0392B !important; 
            color: white !important; 
            font-size: 1.5rem !important; 
            width: 100%; 
            height: 4rem;
            border-radius: 10px;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 0.9) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo escrito a máquina pero firmado?", "op": ["Sí", "No", "Solo con testigos"], "ok": "No"},
    4: {"q": "¿El cónyuge hereda sobre los gananciales con hijos?", "op": ["Sí", "No", "Solo la mitad"], "ok": "No"},
    5: {"q": "¿Es posible el pacto sobre herencia futura (Art. 1010)?", "op": ["Nunca", "Sí, excepcionalmente", "Siempre"], "ok": "Sí, excepcionalmente"},
    6: {"q": "¿La indignidad se purga con 3 años de posesión?", "op": ["Sí", "No", "Son 10 años"], "ok": "Sí"}
}

# --- 3. LÓG
