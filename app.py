import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA MEJORADA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def aplicar_estilo():
    # Fondo: Biblioteca Clásica (podes cambiar el link aquí)
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Roboto+Mono:wght@700&display=swap');

        header, [data-testid="stHeader"], [data-testid="stSidebar"] {{ visibility: hidden; position: absolute; }}
        .stApp {{ background-image: url("{img}"); background-size: cover; background-attachment: fixed; }}
        
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.9) !important; 
            padding: 3rem !important; 
            border: 5px double #D4AF37 !important; 
            margin-top: 20px !important;
            border-radius: 20px !important;
        }}

        /* RELOJ GIGANTE */
        .reloj-pantalla {{
            position: fixed !important; top: 10px !important; right: 10px !important;
            background-color: #C0392B !important; color: white !important;
            padding: 20px 40px !important; border-radius: 10px !important;
            border: 4px solid #D4AF37 !important; z-index: 99999 !important;
            font-size: 3.5rem !important; font-family: 'Roboto Mono', monospace;
            box-shadow: 0 0 20px rgba(192, 57, 43, 0.8);
        }}

        /* TÍTULOS ESTILO JURÍDICO */
        h1, h2, h3 {{ 
            font-family: 'Cinzel', serif !important;
            color: #D4AF37 !important; 
            text-shadow: 3px 3px 6px #000000 !important;
            text-align: center;
        }}

        .stButton>button {{ 
            background: linear-gradient(to bottom, #C0392B, #8E2015) !important;
            color: white !important; border: 2px solid #D4AF37 !important; 
            font-size: 1.2rem !important; font-weight: bold !important;
            border-radius: 8px !important; height: 4rem !important;
        }}
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- 2. LÓGICA DE DATOS ---
def leer_f():
    if os.path.exists("f.txt"):
        try:
            with open("f.txt", "r") as x: return x.read().strip().split(",")
        except: pass
    return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x: x.write(f"{fase},{t_limite}")

def cargar_datos():
    if os.path.exists("d.csv"):
        try: return pd.read_csv("d.csv")
        except: pass
    return pd.DataFrame(columns=["E","A","F","P"])

fase_str, t_limite_str = leer_f()
fase = int(fase_str)
t_limite = float(t_limite_str)
df_global = cargar_datos()

# --- 3. PANEL JUEZ CON QR Y RANKING ---
if st.query_params.get("admin") == "true":
    with st.expander("⚖️ MANDO SUPERIOR DEL JUEZ"):
        if st.text_input("Clave de Seguridad:", type="password") == "derecho2024":
            c1, c2, c3 = st.columns(3)
            with c1:
                ops = ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"]
                idx = 0 if fase==0 else (4 if fase==99 else fase)
                sel = st.selectbox("Fase:", ops, index=idx)
                if st.button("🔄 ACTUALIZAR ETAPA"):
                    nv = 0 if "Esp" in sel else (99 if "Pod" in sel else int(sel.split(" ")[1]))
                    escribir_f(nv, 0); st.rerun()
            with c2:
                dur = st.number_input("Segundos de Ronda:", 5, 120, 30)
                if st.button("⏱️ ¡LARGAR RELOJ!"):
                    escribir_f(fase, time.time() + dur); st.rerun()
            with c3:
                # BOTÓN QR
                st.write("Link para Alumnos:")
                url_base = "https://juego-familia-y-sucesiones-uba.streamlit.app"
                st.code(url_base)
                if st.button("🗑️ LIMPIAR TODO"):
                    if os.path.exists("d.csv"): os.remove("d.csv")
                    escribir_f(0, 0); st.rerun()

# --- 4. REGISTRO ---
if 'u' not in st.session_state: st.session_state.u = None
if not st.session_state.u:
    st.title("🏛️ DESAFÍO JURÍDICO UBA")
    st.write("### Identifíquese para ingresar a la audiencia")
    e, a = st.text_input("Email Institucional:"), st.text_input("Alias (Nombre):")
    if st.button("INGRESAR AL RECINTO"):
        if e and a:
            pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=not os.path.exists("d.csv"), index=False)
            st.session_state.u = {"e": e, "a": a}; st.rerun()
    st.stop()

# --- 5. LÓGICA DE JUEGO ---
ahora = time.time()
v_ok = not df_global[(df_global["E"] == st.session_state.u["e"]) & (df_global["F"] == fase)].empty if not df_global.empty else False
activo = (0 < fase < 99) and (t_limite > ahora) and not v_ok

if activo:
    seg = int(t_limite - ahora)
    st.markdown(f'<div class="reloj-pantalla">{seg}</div>', unsafe_allow_html=True)
    # Sonido de tic-tac si quedan menos de 10 seg (Opcional, requiere URL de audio)

# --- 6. PANTALLAS ---
if fase == 0:
    st.header("⚖️ Sala de Espera del Tribunal")
    st.write(f"Bienvenido Dr/a. **{st.session_state.u['a']}**. La audiencia comenzará en breve.")
    
elif fase == 99:
    st.header("🏆 SENTENCIA FINAL: EL PODIO")
    st.balloons()
    if not df_global.empty:
        ranking = df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(5)
        st.table(ranking)

else:
    st.header(f"RONDA N° {fase}")
    if v_ok:
        st.success("✅ Su voto ha sido registrado. Espere los resultados parciales.")
        # RANKING PARCIAL (LO QUE PEDISTE)
        st.write("---")
        st.write("### 📊 Liderazgo Parcial:")
        if not df_global.empty:
            parcial = df_global[df_global["F"] > 0].groupby("A")["P"].sum().sort_values(ascending=False).head(3)
            st.dataframe(parcial, use_container_width=True)
    else:
        banco = {
            1: {"q": "¿Cuál es la porción legítima de los descendientes?", "o": ["2/3", "1/2"], "k": "2/3"},
            2: {"q": "¿Cuál es el plazo máximo para aceptar la herencia?", "o": ["10 años", "5 años"], "k": "10 años"},
            3: {"q": "¿Es válido el testamento ológrafo hecho a máquina?", "o": ["No", "Sí"], "k": "No"}
        }
        st.write(f"### {banco[fase]['q']}")
        rta = st.radio("Seleccione su veredicto:", banco[fase]['o'])
        if st.button("ENVIAR VOTACIÓN", disabled=not activo):
            pts = 100 if rta == banco[fase]['k'] else 0
            pd.DataFrame([[st.session_state.u["e"], st.session_state.u["a"], fase, pts]], columns=["E","A","F","P"]).to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR DOCENTE ---
st.write("---")
if not df_global.empty:
    al = df_global[df_global["F"] == 0]["A"].unique()
    cols = st.columns(6)
    for i, n in enumerate(al):
        voto = "✅" if not df_global[(df_global["A"] == n) & (df_global["F"] == fase)].empty else "👤"
        cols[i % 6].write(f"{voto} {n}")

time.sleep(1); st.rerun()
