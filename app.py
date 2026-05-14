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

# --- 2. ESTILOS (SE MANTIENEN IGUAL) ---
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 2px 2px 4px #000000 !important; text-align: center; }
    .main .block-container { background: rgba(0, 0, 0, 0.8) !important; padding: 2.5rem !important; border-radius: 20px !important; border: 2px solid #D4AF37; max-width: 950px !important; margin: auto; }
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; text-transform: uppercase; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: 900 !important; width: 100%; border: 1px solid #FFFFFF; }
    .podio { font-size: 2.5rem; margin: 10px; padding: 15px; border-radius: 15px; border: 2px solid #D4AF37; background: rgba(212, 175, 55, 0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS Y PREGUNTAS ---
df_global = cargar_datos()
f_data = leer_f()
fase, t_limite = int(f_data[0]), float(f_data[1])
ahora = time.time()

banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 4. PANEL DEL JUEZ (BOTONES CORREGIDOS) ---
if st.query_params.get("admin") == "true":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DEL JUEZ</h1>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "derecho2024":
        
        with st.expander("📖 BANCO DE PREGUNTAS"):
            for k, v in banco.items(): st.write(f"**{k}.** {v['q']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            f_sel = st.selectbox("Fase:", [0, 1, 2, 3, 4, 99], index=0)
            if st.button("CAMBIAR FASE"):
                escribir_f(f_sel, ahora + 30) # Se habilita tiempo por defecto al cambiar
                st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, ahora + t_set)
                st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f(0, 0)
                st.rerun()

        st.divider()
        c1, c2 = st.columns(2)
        if c1.button("📊 RESULTADOS PARCIALES"):
            if not df_global.empty: st.table(df_global[['A', 'P']].sort_values(by='P', ascending=False))
        if c2.button("🏆 MOSTRAR PODIO FINAL"):
            escribir_f(99, 0)
            st.rerun()
    st.stop()

# --- 5. ACCESO ALUMNOS ---
if 'u' not in st.session_state: st.session_state.u = None
if st.session_state.u is None:
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    m = st.text_input("Email Académico:")
    n = st.text_input("Nombre y Apellido:")
    g = st.radio("Género:", ["Dr.", "Dra."])
    if st.button("INGRESAR") and m and n:
        if not os.path.exists("d.csv"):
            with open("d.csv", "w") as f: f.write("E,A,F,P,G\n")
        with open("d.csv", "a") as f: f.write(f"{m},{n},0,0,{g}\n")
        st.session_state.u = {"e": m, "a": n, "g": g}
        st.rerun()
    st.stop()

# --- 6. JUEGO CON PUNTOS POR VELOCIDAD ---
if fase in banco:
    st.write(f"👤 {st.session_state.u['g']} {st.session_state.u['a']}")
    
    restante = t_limite - ahora
    if restante > 0:
        st.markdown(f'<div style="position:fixed; top:30px; right:30px; background:#C0392B; color:white; padding:20px; border-radius:15px; font-size:4rem; border:4px solid #D4AF37;">{int(restante)}</div>', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()
    
    p = banco[fase]
    st.markdown(f"## {p['q']}")
    rta = st.radio("Veredicto:", p["o"], key=f"r{fase}")
    
    if st.button("ENVIAR RESPUESTA"):
        if rta == p["k"]:
            # CÁLCULO DE PUNTOS: 10 base + bono por rapidez
            # Si responde en el segundo 1 del reloj, suma 20. Si el tiempo terminó, suma 10.
            bono = int(max(0, restante)) 
            puntos_obtenidos = 10 + min(bono, 10)
            
            st.success(f"✅ ¡CORRECTO! Sumaste {puntos_obtenidos} puntos.")
            
            # Actualizar CSV
            df_actual = cargar_datos()
            df_actual.loc[df_actual['E'] == st.session_state.u['e'], 'P'] += puntos_obtenidos
            df_actual.to_csv("d.csv", index=False)
        else:
            st.error("❌ INCORRECTO")

elif fase == 99:
    st.balloons()
    st.markdown("<h1 class='titulo-oro'>🚀 SENTENCIA FINAL 🚀</h1>", unsafe_allow_html=True)
    if not df_global.empty:
        res = df_global.sort_values(by="P", ascending=False).head(3).values.tolist()
        st.markdown(f"<div class='podio'>🥇 1er Puesto: {res[0][1]}</div>", unsafe_allow_html=True)
        if len(res) > 1: st.markdown(f"<div class='podio'>🥈 2do Puesto: {res[1][1]}</div>", unsafe_allow_html=True)
        if len(res) > 2: st.markdown(f"<div class='podio'>🥉 3er Puesto: {res[2][1]}</div>", unsafe_allow_html=True)
        
        # Imagen según género del 1ero
        img = "https://img.freepik.com/foto-gratis/hombre-celebrando-victoria_23-2148107020.jpg" if res[0][4] == "Dr." else "https://img.freepik.com/foto-gratis/mujer-celebrando-victoria_23-2148107030.jpg"
        st.image(img, use_column_width=True)
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/human/sounds/applause-01.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)
