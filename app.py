import streamlit as st
import pandas as pd
import time
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# 🚨 URL DE GOOGLE APPS SCRIPT 🚨
URL_PUENTE_GOOGLE = "https://script.google.com/macros/s/AKfycbyN0oVHgwwGj45tF4zdOihsRfikAsNcG51ibWkZPmSukMKVvfaDzaNPAzm4WUqAp-82/exec"

# --- 2. FUNCIÓN AUDIO ---
def reproducir_audio(url):
    audio_html = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 3. FUNCIÓN DE DATOS (con caché corto para reducir llamadas a Google) ---
@st.cache_data(ttl=3)  # Caché de 3 segundos: evita llamadas repetidas en el mismo ciclo
def fetch_remoto():
    try:
        res = requests.get(URL_PUENTE_GOOGLE, timeout=5)
        return res.json()
    except:
        return None

def gestionar_datos(accion="leer", fase=None, tiempo=None, nuevo_usuario=None):
    df_fallback = pd.DataFrame(
        [["SISTEMA", "CONTROL", 0, 0.0, "0"]],
        columns=["E", "A", "F", "P", "G"]
    )

    if accion == "leer":
        data = fetch_remoto()
        if data:
            try:
                df = pd.DataFrame(data)
            except:
                df = st.session_state.get("db_local", df_fallback)
        else:
            df = st.session_state.get("db_local", df_fallback)

    else:
        # Invalidar caché al escribir para que el próximo leer traiga datos frescos
        fetch_remoto.clear()
        try:
            payload = {
                "accion": accion,
                "fase": fase,
                "tiempo": tiempo,
                "usuario": nuevo_usuario
            }
            res = requests.post(URL_PUENTE_GOOGLE, json=payload, timeout=6)
            df = pd.DataFrame(res.json())
        except:
            df = st.session_state.get("db_local", df_fallback)

    # Normalizar columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    for col in ["E", "A", "F", "P", "G"]:
        if col not in df.columns:
            df[col] = ""

    df["E_STR"] = df["E"].astype(str).str.strip().str.upper()

    # Aplicar cambios locales según acción
    if accion == "escribir_sistema" and "SISTEMA" in df["E_STR"].values:
        df.loc[df["E_STR"] == "SISTEMA", "F"] = int(fase)
        df.loc[df["E_STR"] == "SISTEMA", "P"] = float(tiempo)

    elif accion == "nuevo_usuario" and nuevo_usuario:
        email_nuevo = nuevo_usuario["E"].strip().upper()
        if email_nuevo not in df["E_STR"].values:
            df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)

    elif accion == "sumar_puntos" and nuevo_usuario:
        mask = df["E_STR"] == str(nuevo_usuario["e"]).strip().upper()
        df.loc[mask, "P"] = (
            pd.to_numeric(df.loc[mask, "P"], errors="coerce").fillna(0)
            + float(nuevo_usuario["pts"])
        )

    df_final = df.drop(columns=["E_STR"]) if "E_STR" in df.columns else df
    st.session_state.db_local = df_final
    return df_final

# --- 4. ESTILOS VISUALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, span { font-family: 'Poppins', sans-serif; text-align: center; }
    h2, .stMarkdown h2 {
        color: #FFFFFF !important; font-size: 2.5rem !important; font-weight: 800 !important;
        text-shadow: 3px 3px 10px #000000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000 !important;
    }
    .titulo-oro {
        color: #FFFFFF !important; font-size: 3.8rem !important; font-weight: 800;
        text-transform: uppercase;
        text-shadow: 0 0 10px #D4AF37, 0 0 20px #D4AF37, 3px 3px 5px #000 !important;
    }
    label, [data-testid="stWidgetLabel"] p, .stSelectbox label,
    .stNumberInput label, .stRadio label, [data-testid="stMarkdownContainer"] p {
        color: #CCFF00 !important; font-weight: 800 !important;
        font-size: 1.2rem !important; text-shadow: 2px 2px 4px #000 !important;
    }
    .reloj-container {
        background-color: rgba(0,0,0,0.8); color: #FF4B4B; font-size: 4rem;
        font-weight: 800; padding: 10px 30px; border-radius: 15px;
        border: 4px solid #FF4B4B; display: inline-block; margin: 20px 0;
        text-shadow: 0 0 10px #FF4B4B;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th,
    .stDataFrame p, [data-testid="stExpander"] p, [data-testid="stExpander"] b {
        color: #FFFFFF !important; font-weight: 600 !important;
        text-shadow: 1px 1px 2px #000000 !important;
    }
    [data-testid="stTable"], .stTable, [data-testid="stExpander"] {
        background-color: rgba(0,0,0,0.6) !important; border-radius: 10px;
    }
    .stButton>button {
        background-color: #D4AF37 !important; color: #000000 !important;
        font-weight: 800 !important; border: 2px solid #000 !important; width: 100%;
    }
    .box-oro {
        background: linear-gradient(145deg, #D4AF37, #B8860B); color: #FFF !important;
        padding: 25px; border-radius: 15px; width: 85%; font-size: 2.5rem;
        font-weight: 800; border: 4px solid #FFF; text-shadow: 2px 2px 5px #000 !important;
        margin: auto;
    }
    .box-plata {
        background: linear-gradient(145deg, #C0C0C0, #808080); color: #FFF !important;
        padding: 15px; border-radius: 12px; width: 75%; font-size: 1.8rem;
        font-weight: 700; margin: auto;
    }
    .box-bronce {
        background: linear-gradient(145deg, #CD7F32, #8B4513); color: #FFF !important;
        padding: 12px; border-radius: 10px; width: 65%; font-size: 1.5rem;
        font-weight: 700; margin: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BANCO DE PREGUNTAS ---
banco = {
    1: {"q": "¿Cuál es la legítima de descendientes?", "o": ["1/2", "2/3", "3/4"], "k": "2/3"},
    2: {"q": "¿Plazo para aceptar herencia?", "o": ["5 años", "10 años", "20 años"], "k": "10 años"},
    3: {"q": "¿Es válido testamento ológrafo a máquina?", "o": ["No", "Sí"], "k": "No"},
    4: {"q": "¿Qué tipo de proceso es la sucesión?", "o": ["Contencioso", "Voluntario", "Ejecutivo"], "k": "Voluntario"}
}

# --- 6. INICIALIZAR SESSION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None
if "f_voto" not in st.session_state:
    st.session_state.f_voto = -1
if "enviado" not in st.session_state:
    st.session_state.enviado = False
if "ultimo_refresh" not in st.session_state:
    st.session_state.ultimo_refresh = 0.0

# --- 7. PANTALLA DE LOGIN ---
if st.session_state.user is None:
    reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/bienvenida.mp3")
    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)

    m = st.text_input("Email de Acceso (Alumnos) o Clave (Docente):")
    n = st.text_input("Nombre Completo:")
    g = st.radio("Título:", ["Dr.", "Dra."])

    if st.button("INGRESAR"):
        m = m.strip()
        n = n.strip()
        if m == "derecho2024":
            st.session_state.user = {"tipo": "juez"}
            st.rerun()
        elif "@" in m and n:
            st.session_state.user = {"tipo": "alumno", "e": m, "a": n, "g": g}
            gestionar_datos(
                "nuevo_usuario",
                nuevo_usuario={"E": m, "A": n, "F": 0, "P": 0.0, "G": g}
            )
            st.rerun()
        else:
            st.error("Ingresá un Email válido y tu nombre completo.")
    st.stop()

# --- 8. DATOS GLOBALES Y FASE ACTUAL ---
df_global = gestionar_datos("leer")

try:
    info_sistema = df_global[
        df_global["E"].astype(str).str.strip().str.upper() == "SISTEMA"
    ].iloc[0]
    fase_serv = int(info_sistema["F"])
    t_limite = float(info_sistema["P"])
except Exception:
    fase_serv = 0
    t_limite = 0.0

ahora = time.time()
fases_nombres = {0: "Inicio", **{int(k): f"P{k}" for k in banco.keys()}, 88: "Parcial", 99: "FINAL"}

# --- 9. AUTO-REFRESCO CONTROLADO (sin congelar botones) ---
# Solo refresca si el usuario es alumno, hay una pregunta activa con reloj corriendo
# y pasaron al menos 3 segundos desde el último refresco
if st.session_state.user.get("tipo") == "alumno":
    reloj_activo = (t_limite > ahora) and (fase_serv in banco)
    tiempo_desde_refresh = ahora - st.session_state.ultimo_refresh

    if reloj_activo and tiempo_desde_refresh > 3:
        st.session_state.ultimo_refresh = ahora
        time.sleep(0.1)  # Pequeña pausa para que Streamlit procese acciones pendientes
        st.rerun()

# ============================================================
# --- 10. PANEL DOCENTE ---
# ============================================================
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        op_fase = st.selectbox(
            "Cambiar Pregunta:",
            options=list(fases_nombres.keys()),
            format_func=lambda x: fases_nombres[x],
            key="sel_fase"
        )
        if st.button("📢 ACTUALIZAR FASE"):
            gestionar_datos("escribir_sistema", fase=op_fase, tiempo=0.0)
            st.rerun()

    with c2:
        t_set = st.number_input("Segundos:", min_value=5, max_value=60, value=25)
        if st.button("⏱️ INICIAR RELOJ"):
            gestionar_datos("escribir_sistema", fase=fase_serv, tiempo=ahora + t_set)
            st.rerun()

    with c3:
        if st.button("🔄 REFRESCAR"):
            fetch_remoto.clear()
            st.rerun()

    with c4:
        if st.button("⚠️ RESET"):
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
    df_alumnos = df_global[
        df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"
    ][["G", "A", "P"]].sort_values(by="P", ascending=False)
    st.table(df_alumnos)

# ============================================================
# --- 11. PANTALLA ALUMNO ---
# ============================================================
else:
    # Resetear "enviado" cuando cambia la fase
    if st.session_state.f_voto != fase_serv:
        st.session_state.enviado = False

    ya_envio = st.session_state.enviado

    # --- PANTALLA FINAL ---
    if fase_serv == 99:
        reproducir_audio("https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3")
        st.balloons()
        st.snow()

        df_podio = df_global[
            df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"
        ].copy()
        df_podio["P"] = pd.to_numeric(df_podio["P"], errors="coerce").fillna(0)
        podio = df_podio.sort_values(by="P", ascending=False).head(3)

        if not podio.empty:
            primer_lugar = podio.iloc[0]
            titulo_ganador = str(primer_lugar.get("G", "Dr."))
            nombre_ganador = str(primer_lugar.get("A", ""))
            pts_ganador = int(primer_lugar.get("P", 0))

            img_file = "alumna_festejo_uba.png" if titulo_ganador == "Dra." else "alumno_festejo_uba.png"
            img_url = f"https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/{img_file}"
            st.image(img_url, use_container_width=True)

            st.markdown(
                f"<h1 class='titulo-oro'>🏆 {titulo_ganador} {nombre_ganador} 🏆</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='box-oro'>🥇 ORO: {nombre_ganador} ({pts_ganador} PTS)</div><br>",
                unsafe_allow_html=True
            )
            if len(podio) > 1:
                segundo = podio.iloc[1]
                st.markdown(
                    f"<div class='box-plata'>🥈 PLATA: {segundo['A']} ({int(segundo['P'])} PTS)</div><br>",
                    unsafe_allow_html=True
                )
            if len(podio) > 2:
                tercero = podio.iloc[2]
                st.markdown(
                    f"<div class='box-bronce'>🥉 BRONCE: {tercero['A']} ({int(tercero['P'])} PTS)</div>",
                    unsafe_allow_html=True
                )

        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.clear()
            st.rerun()

    # --- PANTALLA DE PREGUNTA ---
    elif fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora

        st.markdown(f"## {p['q']}")

        # Determinar estado del reloj y bloqueo
        if t_limite == 0:
            st.warning("⚖️ El Tribunal aún no ha habilitado la votación. Espere...")
            voto_bloqueado = True

        elif reloj_on and not ya_envio:
            secs_restantes = int(t_limite - ahora)
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<div class='reloj-container'>⏱️ {secs_restantes}s</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            voto_bloqueado = False

        elif not reloj_on and not ya_envio:
            st.markdown(
                "<div style='text-align:center;'>"
                "<div class='reloj-container' style='color:gray; border-color:gray;'>⌛ TIEMPO AGOTADO</div>"
                "</div>",
                unsafe_allow_html=True
            )
            voto_bloqueado = True

        else:
            # ya_envio == True
            voto_bloqueado = True

        # Opciones de respuesta
        opcion = st.radio(
            "Dictamen:",
            p["o"],
            disabled=(voto_bloqueado or ya_envio),
            key=f"radio_fase_{fase_serv}"
        )

        # Botón enviar
        if not voto_bloqueado and not ya_envio:
            if st.button("ENVIAR SENTENCIA"):
                if opcion == p["k"]:
                    reproducir_audio(
                        "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/exito.mp3"
                    )
                    # Puntos: 10 base + bonus por velocidad (máx 10)
                    bonus = max(0, min(int(t_limite - ahora), 10))
                    pts = 10 + bonus
                    gestionar_datos(
                        "sumar_puntos",
                        nuevo_usuario={"e": st.session_state.user["e"], "pts": pts}
                    )
                    st.success(f"✅ ¡CORRECTO! +{pts} puntos")
                else:
                    reproducir_audio(
                        "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/error.mp3"
                    )
                    st.error("❌ INCORRECTO")

                st.session_state.enviado = True
                st.session_state.f_voto = fase_serv
                st.rerun()

        elif ya_envio:
            st.info("✔️ Ya enviaste tu respuesta para esta pregunta.")

        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        df_alumnos = df_global[
            df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"
        ][["G", "A", "P"]].sort_values(by="P", ascending=False)
        st.table(df_alumnos)

    # --- SALA DE ESPERA ---
    else:
        st.info("⚖️ Tribunal deliberando... espere.")
        st.markdown("---")
        st.markdown("### 👥 PARTICIPANTES EN VIVO")
        df_alumnos = df_global[
            df_global["E"].astype(str).str.strip().str.upper() != "SISTEMA"
        ][["G", "A", "P"]].sort_values(by="P", ascending=False)
        st.table(df_alumnos)
