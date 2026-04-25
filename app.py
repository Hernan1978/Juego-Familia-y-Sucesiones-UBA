import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTÉTICA ORIGINAL (RESTAURADA) ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* Ocultar basura de Streamlit */
        header, [data-testid="stHeader"] {{ visibility: hidden; }}
        
        /* Fondo de pantalla completo */
        .stApp {{ 
            background-image: url("{img}"); 
            background-size: cover; 
            background-attachment: fixed; 
        }}
        
        /* PANEL CENTRAL: El cuadro negro semitransparente */
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85) !important; 
            padding: 3rem !important; 
            border-radius: 20px !important; 
            border: 3px solid #D4AF37 !important; 
            margin-top: 50px !important;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }}

        /* RELOJ: Rojo UBA arriba a la derecha */
        .reloj-pantalla {{
            position: fixed !important; 
            top: 20px !important; 
            right: 20px !important;
            background-color: #C0392B !important; 
            color: white !important;
            padding: 15px 25px !important; 
            border-radius: 50px !important;
            border: 3px solid #D4AF37 !important; 
            z-index: 999999 !important;
            font-family: 'Courier New', monospace !important; 
            font-size: 2.2rem !important;
            font-weight: bold !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7);
        }}

        /* TEXTOS: Blancos con sombra negra para lectura perfecta */
        h1, h2, h3, p, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000 !important; 
            font-size: 1.3rem !important;
        }}
        h1 {{ font-size: 3rem !important; color: #D4AF37 !important; }}

        /* INPUTS: Fondo gris oscuro para que se vea el texto blanco */
        input {{ 
            background-color: #333333 !important; 
            color: white !important; 
            border: 1px solid #D4AF37 !important; 
        }}

        /* BOTÓN: Rojo UBA clásico */
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            font-size: 1.5rem !important; 
            font-weight: bold !important;
            border: 2px solid #D4AF37 !important; 
            border-radius: 10px !important;
            height: 4rem !important;
        }}
        .stButton>button:disabled {{ background-color: #444 !important; border-color: #222 !important; }}
        
        /* Sidebar (Panel Juez) */
        [data-testid="stSidebar"] {{ background-color: rgba(20, 20, 20, 0.95) !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE PERSISTENCIA ---
def leer_f(): return open("f.txt","r").read().strip() if os.path.exists("f.txt") else "0"
def escribir_f(v): open("f.txt","w").write(str(v))

if "t_limite" not in st.session_state: st.session_state.t_limite = 0
fase = int(leer_f())

# --- 3. PANEL JUEZ (ADMIN) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO DEL JUEZ")
        if st.text_input("Clave:", type="password") == "derecho2024":
            if st.button("🗑️ REINICIAR TODO"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                escribir_f("0"); st.session_state.t_limite = 0; st.rerun()
            st.write("---")
            sel = st.selectbox("Fase:", ["Sala de Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"], index=fase if fase < 4 else 4)
            if st.button("LANZAR FASE"):
                nv = 0 if "Sala" in sel else (99 if "Podio" in sel else int(sel.split(" ")[1]))
                escribir_f(str(nv)); st.session_state.t_limite = 0; st.rerun()
            if 0 < fase < 99:
                if st.button("⏱️ INICIAR 20 SEGUNDOS"):
                    st.session_state.t_limite = time.time() + 21; st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("⚖️ REGISTRO DE LETRADOS")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("INGRESAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
        pd.DataFrame([[e,a,0,0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
        st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE TIEMPO ---
voto_ok = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    voto_ok = not df_v[(df_v.E == st.session_state.u['e']) & (df_v.F == fase)].empty

ahora = time.time()
activo = False
if 0 < fase < 99 and not voto_ok and st.session_state.t_limite > ahora:
    restante = int(st.session_state.t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">⌛ {restante}s</div>', unsafe_allow_html=True)
    activo = True

# --- 6. CONTENIDO PRINCIPAL ---
if fase == 0:
    st.header("🏛️ Sala de Espera")
    st.write(f"Bienvenido, **Dr. {st.session_state.u['a']}**. El debate comenzará a la brevedad.")
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL")
    if os.path.exists("d.csv"):
        df_res = pd.read_csv("d.csv")
        st.table(df_res[df_res.F > 0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if voto_ok:
        st.success("✔️ Su veredicto ha sido enviado. Espere la siguiente ronda.")
    else:
        qs = {1: ["¿Porción legítima de los descendientes?", "2/3", "1/2"], 
              2: ["¿Plazo máximo para aceptar la herencia?", "10 años", "5 años"], 
              3: ["¿Es válido un testamento ológrafo escrito a máquina?", "No", "Sí"]}
        st.header(f"RONDA {fase}")
        st.write(f"### {qs[fase][0]}")
        res = st.radio("Veredicto:", qs[fase][1:])
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            puntos = 100 if res == qs[fase][1] else 0
            pd.DataFrame([[st.session_state.u['e'], st.session_state.u['a'], fase, puntos]], 
                         columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False,
