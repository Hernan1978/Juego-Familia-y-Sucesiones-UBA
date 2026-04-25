import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA RADICAL ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    # Nueva imagen de fondo (Biblioteca clásica)
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070" 
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* CAJA CONTENEDORA OSCURA */
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.8); 
            padding: 3rem;
            border-radius: 20px;
            border: 3px solid #D4AF37;
        }}
        /* LETRAS BLANCAS Y GRANDES */
        h1, h2, h3, p, label, .stMarkdown, .stSelectbox label {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 8px #000000 !important;
            font-family: 'Georgia', serif;
        }}
        /* AGRANDAR OPCIONES DE RESPUESTA */
        div[data-testid="stMarkdownContainer"] p {{
            font-size: 1.5rem !important;
            font-weight: bold !important;
        }}
        /* BOTÓN DE ENVIAR (GRANDE Y ROJO) */
        .stButton>button {{
            background-color: #C0392B !important;
            color: white !important;
            font-size: 1.8rem !important;
            height: 4rem !important;
            width: 100%;
            border-radius: 15px;
            border: 1px solid white;
        }}
        /* ESTILO PARA LOS INPUTS */
        .stTextInput input {{
            font-size: 1.2rem !important;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido un testamento ológrafo firmado pero escrito a máquina?", "op": ["Sí", "No", "Solo si hay testigos"], "ok": "No"},
    4: {"q": "¿El cónyuge hereda sobre los bienes gananciales en concurrencia con hijos?", "op": ["Sí", "No", "Solo la mitad"], "ok": "No"},
    5: {"q": "¿Se puede pactar sobre una herencia futura?", "op": ["Nunca", "Solo en casos excepcionales (Art. 1010)", "Siempre"], "ok": "Solo en casos excepcionales (Art. 1010)"}
}

# --- 3. LOGIN ÚNICO (Session State) ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("⚖️ REGISTRO DE LETRADOS - UBA")
    st.write("### Identifíquese para ingresar a la sala de audiencias.")
    
    with st.container():
        m = st.text_input("Email Institucional:")
        a = st.text_input("Alias para el Ranking:")
        if st.button("INGRESAR AL JUICIO"):
            if m and a and "@" in m:
                st.session_state.usuario = {"mail": m, "alias": a}
                st.rerun()
            else:
                st.error("Complete los datos correctamente.")
    st.stop()

# --- 4. CONTROL DEL PROFESOR ---
def set_fase(n):
    with open("fase.txt", "w") as f: f.write(str(n))

def get_fase():
    if not os.path.exists("fase.txt"): return 0
    with open("fase.txt", "r") as f: return int(f.read())

with st.sidebar:
    st.header("🛂 PANEL DE JUEZ")
    clave = st.text_input("Clave Docente:", type="password")
    if clave == "derecho2024":
        opc = ["Espera"] + [f"Pregunta {i}" for i in banco.keys()] + ["Podio Final"]
        sel = st.selectbox("Cambiar fase:", opc)
        if st.button("Lanzar"):
            if "Espera" in sel: set_fase(0)
            elif "Podio" in sel: set_fase(99)
            else: set_fase(int(sel.split(" ")[1]))
            st.rerun()

# --- 5. DINÁMICA DEL JUEGO ---
fase_actual = get_fase()

if fase_actual == 0:
    st.header(f"🏛️ Sala de Espera: {st.session_state.usuario['alias']}")
    st.write("### El Tribunal está deliberando. Aguarde el inicio del examen.")
    time.sleep(2)
    st.rerun()

elif fase_actual in banco:
    pregunta = banco[fase_actual]
    st.header(f"RONDA {fase_actual}")
    st.write(f"## {pregunta['q']}")
    
    # Usamos un identificador único para que no se mezcle
    eleccion = st.radio("Seleccione su respuesta:", pregunta['op'], key=f"r_{fase_actual}")
    
    if st.button("ENVIAR VEREDICTO"):
        puntos = 100 if eleccion == pregunta['ok'] else 0
        df = pd.DataFrame([[st.session_state.usuario['mail'], st.session_state.usuario['alias'], puntos]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Veredicto registrado correctamente!")

elif fase_actual == 99:
    st.balloons()
    st.header("🏆 SENTENCIA FINAL: EL PODIO")
    if os.path.exists("data.csv"):
        datos = pd.read_csv("data.csv")
        ranking = datos.groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        st.table(ranking)
    else:
        st.write("No hay registros en esta sesión.")mport streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    # CAMBIA ESTE LINK POR LA FOTO QUE QUIERAS
    fondo_url = "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=2070" 
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* CUADRO DE PREGUNTAS: Negro para que el blanco resalte 100% */
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.85); 
            padding: 3rem;
            border-radius: 20px;
            border: 2px solid #D4AF37; /* Borde dorado tipo diplomático */
        }}
        /* TEXTOS EN BLANCO PURO */
        h1, h2, h3, p, label, .stMarkdown {{
            color: #FFFFFF !important;
            font-family: 'Arial', sans-serif;
        }}
        .stRadio label {{
            font-size: 1.4rem !important;
            font-weight: bold !important;
        }}
        /* BOTÓN ROJO LLAMATIVO */
        .stButton>button {{
            background-color: #E63946 !important;
            color: white !important;
            font-size: 1.5rem !important;
            width: 100%;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS (Agregá las que quieras acá) ---
banco_preguntas = {
    1: {"q": "¿Cuál es la porción legítima de los descendientes?", "op": ["1/2", "2/3", "4/5"], "ok": "2/3"},
    2: {"q": "¿Plazo para aceptar una herencia?", "op": ["5 años", "10 años", "20 años"], "ok": "10 años"},
    3: {"q": "¿Es válido el testamento ológrafo a máquina?", "op": ["Sí", "No", "Solo con firma"], "ok": "No"},
    4: {"q": "¿La nuera viuda sin hijos hereda a los suegros?", "op": ["Sí", "No", "Depende"], "ok": "No"},
    5: {"q": "¿El cónyuge concurre con los ascendientes?", "op": ["Sí", "No", "Solo si no hay bienes"], "ok": "Sí"}
}

# --- 3. LÓGICA DE LOGIN ÚNICO ---
if 'logueado' not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.title("⚖️ Registro de Letrados")
    st.subheader("Ingresá tus datos una sola vez para comenzar")
    mail = st.text_input("Email Institucional:")
    alias = st.text_input("Tu Alias:")
    
    if st.button("ENTRAR AL JUICIO"):
        if mail and alias and "@" in mail:
            st.session_state.mail = mail
            st.session_state.alias = alias
            st.session_state.logueado = True
            st.rerun()
        else:
            st.error("Por favor, ingresá un mail válido y un alias.")
    st.stop()

# --- 4. CONTROL DEL PROFESOR (BARRA LATERAL) ---
def set_estado(n):
    with open("estado.txt", "w") as f: f.write(str(n))

def get_estado():
    if not os.path.exists("estado.txt"): return 0
    with open("estado.txt", "r") as f: return int(f.read())

with st.sidebar:
    st.header("🛂 Mando Docente")
    passw = st.text_input("Clave:", type="password")
    if passw == "derecho2024":
        opciones = ["Espera"] + [f"Pregunta {i}" for i in banco_preguntas.keys()] + ["Podio"]
        fase_sel = st.selectbox("Cambiar a:", opciones)
        if st.button("Lanzar"):
            if "Espera" in fase_sel: set_estado(0)
            elif "Podio" in fase_sel: set_estado(99)
            else: set_estado(int(fase_sel.split(" ")[1]))
            st.rerun()

# --- 5. JUEGO EN VIVO ---
fase = get_estado()

if fase == 0:
    st.header(f"🏛️ ¡Bienvenido, {st.session_state.alias}!")
    st.write("El tribunal está sesionando. Esperá a que el profesor lance la primera pregunta...")
    time.sleep(3)
    st.rerun()

elif fase in banco_preguntas:
    p = banco_preguntas[fase]
    st.header(f"Ronda {fase}")
    st.subheader(p["q"])
    
    respuesta = st.radio("Seleccioná tu fundamento:", p["op"], key=f"p_{fase}")
    
    if st.button("ENVIAR VEREDICTO"):
        puntos = 100 if respuesta == p["ok"] else 0
        df = pd.DataFrame([[st.session_state.mail, st.session_state.alias, puntos]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Voto registrado! Esperá a la siguiente ronda.")

elif fase == 99:
    st.balloons()
    st.header("🏆 Podio Final")
    if os.path.exists("data.csv"):
        res = pd.read_csv("data.csv").groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        st.table(res)
    else:
        st.write("No hay datos.")
import pandas as pd
import os
import time

# --- 1. ESTÉTICA (Letras Blancas / Fondo Oscuro) ---
st.set_page_config(page_title="LexPlay: UBA Derecho", layout="wide")

def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{fondo_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.75); 
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }}
        h1, h2, h3, label, .stMarkdown p {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        .stRadio label {{
            color: #FFFFFF !important;
            font-size: 1.2rem !important;
        }}
        .stButton>button {{
            background-color: #FF4B4B !important;
            color: white !important;
            font-weight: bold;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. BANCO DE PREGUNTAS (CARGALAS ACÁ) ---
# Podés agregar todas las que quieras siguiendo el formato
banco_preguntas = {
    1: {
        "q": "¿Cuál es la porción legítima de los descendientes en el CCyC?",
        "op": ["1/2", "2/3", "4/5"],
        "ok": "2/3"
    },
    2: {
        "q": "¿Qué plazo tiene el heredero para aceptar o renunciar a la herencia?",
        "op": ["5 años", "10 años", "20 años"],
        "ok": "10 años"
    },
    3: {
        "q": "¿Es válido el testamento ológrafo escrito a máquina pero firmado a mano?",
        "op": ["Sí, es válido", "No, debe ser íntegramente de puño y letra", "Sólo si hay testigos"],
        "ok": "No, debe ser íntegramente de puño y letra"
    }
}

# --- 3. FUNCIONES DE CONTROL ---
def set_estado(n):
    with open("estado.txt", "w") as f: f.write(str(n))

def get_estado():
    if not os.path.exists("estado.txt"): return 0
    with open("estado.txt", "r") as f: return int(f.read())

# --- 4. PANEL DEL PROFESOR (BARRA LATERAL) ---
with st.sidebar:
    st.header("🛂 Control Docente")
    pwd = st.text_input("Clave", type="password")
    if pwd == "derecho2024":
        # Dinámicamente creamos las opciones según tu banco de preguntas
        opciones_fase = ["Registro"] + [f"Pregunta {i}" for i in banco_preguntas.keys()] + ["Podio Final"]
        fase_sel = st.selectbox("Ir a:", opciones_fase)
        
        if st.button("CAMBIAR FASE PARA TODOS"):
            if "Registro" in fase_sel: set_estado(0)
            elif "Podio" in fase_sel: set_estado(99)
            else: set_estado(int(fase_sel.split(" ")[1]))
            st.rerun()

# --- 5. INTERFAZ DEL ALUMNO ---
st.title("⚖️ Desafío Familia y Sucesiones")

email = st.text_input("📧 Email:")
alias = st.text_input("🎭 Alias:")

if not email or not alias:
    st.warning("Ingresá tus datos para participar.")
    st.stop()

fase_actual = get_estado()

# FASE 0: ESPERA
if fase_actual == 0:
    st.info(f"¡Hola {alias}! Esperá a que el profesor inicie el juego...")
    time.sleep(2)
    st.rerun()

# FASES DE PREGUNTAS
elif fase_actual in banco_preguntas:
    p = banco_preguntas[fase_actual]
    st.header(f"Ronda {fase_actual}")
    st.subheader(p["q"])
    
    rta = st.radio("Elegí tu respuesta:", p["op"])
    
    if st.button("Enviar Respuesta"):
        puntos = 100 if rta == p["ok"] else 0
        df = pd.DataFrame([[email, alias, puntos]], columns=["Email", "Alias", "Puntos"])
        df.to_csv("data.csv", mode='a', header=not os.path.exists("data.csv"), index=False)
        st.success("¡Voto enviado! Esperá a la siguiente ronda.")

# FASE 99: PODIO
elif fase_actual == 99:
    st.balloons()
    st.header("🏆 Resultados Finales")
    if os.path.exists("data.csv"):
        ranking = pd.read_csv("data.csv").groupby("Alias")["Puntos"].sum().sort_values(ascending=False)
        st.table(ranking)
    else:
        st.write("No hay votos registrados.")
