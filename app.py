import streamlit as st
import pandas as pd
import time
import requests
from streamlit_autorefresh import st_autorefresh

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# URL de Google Apps Script
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzIkrNfH2Ji_YnAXAL7Rw3cVghN97cVNtt80AAJulZ1if5QIRKu-v1QloCnZNwuyoYGlg/exec"

CLAVE_DOCENTE = "derecho2024"

AUDIO = {
    "bienvenida": "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/bienvenida.mp3",
    "exito":      "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/exito.mp3",
    "error":      "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/error.mp3",
    "ganador":    "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3",
}

IMG_BASE = "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/"
COLORES_OPCIONES = ["#E21B3C", "#1368CE", "#26890C", "#FFA602"]
ICONOS_OPCIONES  = ["▲", "◆", "●", "■"]

# ============================================================
# ESTILOS VISUALES
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap');
header, [data-testid="stHeader"] { display: none !important; }
.stApp {
    background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070");
    background-size: cover; background-attachment: fixed;
}
.stApp, .stMarkdown, p, h1, h2, h3, h4, span {
    font-family: 'Poppins', sans-serif; text-align: center;
}
h2, .stMarkdown h2 {
    color: #FFFFFF !important; font-size: 2.2rem !important; font-weight: 800 !important;
    text-shadow: 3px 3px 10px #000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000 !important;
}
.titulo-oro {
    color: #FFFFFF !important; font-size: 3.5rem !important; font-weight: 800;
    text-transform: uppercase;
    text-shadow: 0 0 10px #D4AF37, 0 0 20px #D4AF37, 3px 3px 5px #000 !important;
}
label, [data-testid="stWidgetLabel"] p, .stSelectbox label,
.stNumberInput label, .stRadio label, [data-testid="stMarkdownContainer"] p {
    color: #CCFF00 !important; font-weight: 800 !important;
    font-size: 1.1rem !important; text-shadow: 2px 2px 4px #000 !important;
}
.reloj-container {
    background-color: rgba(0,0,0,0.85); color: #FF4B4B; font-size: 5rem;
    font-weight: 800; padding: 15px 40px; border-radius: 20px;
    border: 5px solid #FF4B4B; display: inline-block; margin: 15px 0;
    text-shadow: 0 0 15px #FF4B4B; animation: pulso 1s infinite;
}
@keyframes pulso { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
[data-testid="stTable"] td, [data-testid="stTable"] th,
.stDataFrame p, [data-testid="stExpander"] p {
    color: #FFFFFF !important; font-weight: 600 !important;
    text-shadow: 1px 1px 2px #000 !important;
}
[data-testid="stTable"], .stTable {
    background-color: rgba(0,0,0,0.65) !important; border-radius: 12px;
}
.stButton>button {
    background-color: #D4AF37 !important; color: #000 !important;
    font-weight: 800 !important; border: 2px solid #000 !important;
    width: 100%; font-size: 1rem !important; border-radius: 10px !important;
    padding: 10px !important;
}
.box-oro {
    background: linear-gradient(145deg,#D4AF37,#B8860B); color:#FFF !important;
    padding:25px; border-radius:15px; width:85%; font-size:2.2rem; font-weight:800;
    border:4px solid #FFF; text-shadow:2px 2px 5px #000 !important; margin:auto;
}
.box-plata {
    background: linear-gradient(145deg,#C0C0C0,#808080); color:#FFF !important;
    padding:18px; border-radius:12px; width:75%; font-size:1.7rem; font-weight:700;
    margin:10px auto;
}
.box-bronce {
    background: linear-gradient(145deg,#CD7F32,#8B4513); color:#FFF !important;
    padding:15px; border-radius:10px; width:65%; font-size:1.4rem; font-weight:700;
    margin:10px auto;
}
.espera-box {
    background: rgba(0,0,0,0.75); border: 3px solid #D4AF37; border-radius: 20px;
    padding: 30px; margin: 20px auto; width: 80%;
    color: #CCFF00 !important; font-size: 1.6rem; font-weight: 800;
    text-shadow: 2px 2px 6px #000;
    animation: brillar 2s infinite;
}
@keyframes brillar {
    0%,100%{border-color:#D4AF37; box-shadow:0 0 10px #D4AF37;}
    50%{border-color:#FFF; box-shadow:0 0 30px #D4AF37;}
}
.kahoot-btn {
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.4rem; font-weight: 800;
    padding: 20px; border-radius: 15px; margin: 8px 0;
    border: 3px solid rgba(255,255,255,0.4);
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    min-height: 80px;
}
.participante-chip {
    display: inline-block; background: rgba(212,175,55,0.3);
    border: 2px solid #D4AF37; border-radius: 20px;
    padding: 6px 16px; margin: 4px; color: #CCFF00 !important;
    font-weight: 700; font-size: 0.95rem;
}
.pregunta-card {
    background: rgba(0,0,0,0.82); border: 3px solid #D4AF37;
    border-radius: 20px; padding: 25px; margin: 15px auto; width: 90%;
    color: #FFFFFF; font-size: 1.8rem; font-weight: 800;
    text-shadow: 2px 2px 6px #000;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIAL STATE & CONTROLES
# ============================================================
if "user" not in st.session_state: st.session_state.user = None
if "f_voto" not in st.session_state: st.session_state.f_voto = -1
if "enviado" not in st.session_state: st.session_state.enviado = False
if "audio_reproducido" not in st.session_state: st.session_state.audio_reproducido = ""

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def audio(key):
    url = AUDIO.get(key, "")
    if url:
        st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

def fetch_remoto():
    try:
        res = requests.get(URL_APPS_SCRIPT, timeout=3)
        return res.json()
    except:
        return None

def llamar_api(payload):
    try:
        res = requests.post(URL_APPS_SCRIPT, json=payload, timeout=4)
        return res.json()
    except:
        return {"ok": False}

def cargar_datos():
    data = fetch_remoto()
    if data is None:
        return (
            st.session_state.get("_cache_sistema",   {"fase": 0, "tiempo": 0.0}),
            st.session_state.get("_cache_alumnos",   []),
            st.session_state.get("_cache_preguntas", [])
        )

    if isinstance(data, dict) and "sistema" in data:
        sistema_raw = data.get("sistema", {})
        sistema = {
            "fase":   int(sistema_raw.get("fase", 0)),
            "tiempo": float(sistema_raw.get("tiempo", 0.0))
        }
        st.session_state._cache_sistema   = sistema
        st.session_state._cache_alumnos   = data.get("alumnos",   [])
        st.session_state._cache_preguntas = data.get("preguntas", [])

    elif isinstance(data, list) and len(data) > 0:
        try:
            df = pd.DataFrame(data)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            fila_sis = df[df["E"].astype(str).str.strip().str.upper() == "SISTEMA"]
            fase_v   = int(fila_sis["F"].iloc[0])   if not fila_sis.empty else 0
            tiempo_v = float(fila_sis["P"].iloc[0]) if not fila_sis.empty else 0.0
            st.session_state._cache_sistema = {"fase": fase_v, "tiempo": tiempo_v}

            df_al = df[df["E"].astype(str).str.strip().str.upper() != "SISTEMA"]
            alumnos_v = []
            for _, row in df_al.iterrows():
                alumnos_v.append({
                    "EMAIL":  str(row.get("E", "")),
                    "NOMBRE": str(row.get("A", "")),
                    "TITULO": str(row.get("G", "Dr.")),
                    "PUNTOS": float(row.get("P", 0))
                })
            st.session_state._cache_alumnos   = alumnos_v
        except:
            pass

    return (
        st.session_state.get("_cache_sistema",   {"fase": 0, "tiempo": 0.0}),
        st.session_state.get("_cache_alumnos",   []),
        st.session_state.get("_cache_preguntas", [])
    )

def alumnos_a_df(alumnos):
    if not alumnos:
        return pd.DataFrame(columns=["EMAIL","NOMBRE","TITULO","PUNTOS"])
    df = pd.DataFrame(alumnos)
    df.columns = [c.strip().upper() for c in df.columns]
    for col in ["EMAIL","NOMBRE","TITULO","PUNTOS"]:
        if col not in df.columns: df[col] = ""
    df["PUNTOS"] = pd.to_numeric(df["PUNTOS"], errors="coerce").fillna(0)
    return df

def preguntas_a_banco(preguntas):
    banco = {}
    for p in preguntas:
        try:
            pid  = int(p.get("ID", 0))
            preg = str(p.get("PREGUNTA", "")).strip()
            ops  = [str(p.get(f"OP{i}", "")).strip() for i in range(1, 5)]
            ops  = [o for o in ops if o]
            corr = str(p.get("CORRECTA", "")).strip()
            if pid and preg and ops and corr:
                banco[pid] = {"q": preg, "o": ops, "k": corr}
        except:
            pass
    return banco

# ============================================================
# PANTALLA LOGIN
# ============================================================
if st.session_state.user is None:
    if st.session_state.audio_reproducido != "bienvenida":
        audio("bienvenida")
        st.session_state.audio_reproducido = "bienvenida"

    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        m = st.text_input("✉️ Email académico o Clave Docente:")
        n = st.text_input("👤 Nombre Completo:")
        g = st.radio("🎓 Título:", ["Dr.", "Dra."], horizontal=True)

        if st.button("⚖️ INGRESAR AL TRIBUNAL"):
            m, n = m.strip(), n.strip()
            if m == CLAVE_DOCENTE:
                st.session_state.user = {"tipo": "juez"}
                st.rerun()
            elif "@" in m and n:
                st.session_state.user = {"tipo": "alumno", "email": m, "nombre": n, "titulo": g}
                llamar_api({
                    "accion": "nuevo_usuario",
                    "usuario": {"EMAIL": m, "NOMBRE": n, "TITULO": g}
                })
                st.rerun()
            else:
                st.error("⚠️ Ingresá un email válido y tu nombre completo.")
    st.stop()

# ============================================================
# CARGAR ESTADOS GLOBALES (SÓLO DESPUÉS DEL LOGIN)
# ============================================================
sistema, alumnos_raw, preguntas_raw = cargar_datos()
fase_serv = int(sistema.get("fase", 0))
t_limite  = float(sistema.get("tiempo", 0.0))
ahora     = time.time()

df_alumnos = alumnos_a_df(alumnos_raw)
banco      = preguntas_a_banco(preguntas_raw)

fases_opciones = {0: "⏸ Sala de Espera"}
for k in sorted(banco.keys()):
    fases_opciones[k] = f"❓ Pregunta {k}"
fases_opciones[88] = "📊 Resultados Parciales"
fases_opciones[99] = "🏆 PODIO FINAL"

# ============================================================
# MOTOR DE AUTOMATIZACIÓN INTELIGENTE (LIMITA EL TITILEO)
# ============================================================
if st.session_state.user is not None:
    # Si es alumno, la pantalla SOLO refresca si NO ha votado todavía.
    # En cuanto vota, el autorefresh se desactiva por completo para congelar el reloj.
    if st.session_state.user.get("tipo") == "alumno":
        if st.session_state.f_voto != fase_serv:
            st.session_state.enviado = False

        if not st.session_state.enviado:
            st_autorefresh(interval=3000, key="refresco_alumno_activo")
    else:
        # El panel docente sí se actualiza de manera constante
        st_autorefresh(interval=4000, key="refresco_docente")

# ============================================================
# PANEL DOCENTE
# ============================================================
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        op_fase = st.selectbox("📋 Cambiar a:", options=list(fases_opciones.keys()), format_func=lambda x: fases_opciones[x], key="sel_fase")
        if st.button("📢 ENVIAR"):
            llamar_api({"accion": "escribir_sistema", "fase": op_fase, "tiempo": 0.0})
            st.rerun()
    with c2:
        t_set = st.number_input("⏱ Segundos:", min_value=5, max_value=120, value=30)
        if st.button("▶️ INICIAR RELOJ"):
            llamar_api({"accion": "escribir_sistema", "fase": fase_serv, "tiempo": time.time() + t_set})
            st.rerun()
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 REFRESCAR"): st.rerun()
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 PARCIALES"):
            llamar_api({"accion": "escribir_sistema", "fase": 88, "tiempo": 0.0})
            st.rerun()
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏆 PODIO FINAL"):
            llamar_api({"accion": "escribir_sistema", "fase": 99, "tiempo": 0.0})
            st.rerun()
    with c6:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚠️ RESET TODO"):
            llamar_api({"accion": "reset_alumnos"})
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
    if fase_serv in banco:
        p = banco[fase_serv]
        st.markdown(f"<div class='pregunta-card'>❓ {p['q']}<br><small style='color:#D4AF37'>✅ Correcta: {p['k']}</small></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("### 📋 Lista de Preguntas")
        for kid, pdata in sorted(banco.items()):
            activa = "🟢 " if kid == fase_serv else "⚪ "
            st.markdown(f"<div style='background:rgba(0,0,0,0.6);border-radius:8px;padding:8px 14px;margin:4px 0;color:#FFF;text-align:left;'>{activa}<b>P{kid}:</b> {pdata['q'][:60]}...</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("### 👥 Participantes")
        if not df_alumnos.empty:
            st.table(df_alumnos[["TITULO","NOMBRE","PUNTOS"]].sort_values("PUNTOS", ascending=False))

# ============================================================
# PANEL ALUMNO
# ============================================================
else:
    user = st.session_state.user
    ya_envio = st.session_state.enviado

    if fase_serv == 99:
        if st.session_state.audio_reproducido != "ganador":
            audio("ganador")
            st.session_state.audio_reproducido = "ganador"
        st.balloons()
        podio = df_alumnos.sort_values("PUNTOS", ascending=False).head(3)
        if not podio.empty:
            ganador = podio.iloc[0]
            st.markdown(f"<h1 class='titulo-oro'>🏆 {ganador['TITULO']} {ganador['NOMBRE']} 🏆</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {ganador['NOMBRE']} ({int(ganador['PUNTOS'])} pts)</div><br>", unsafe_allow_html=True)

    elif fase_serv == 88:
        st.markdown("<h2>📊 Resultados Parciales</h2>", unsafe_allow_html=True)
        podio_p = df_alumnos.sort_values("PUNTOS", ascending=False)
        for i, (_, row) in enumerate(podio_p.iterrows()):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}°"
            st.markdown(f"<div style='background:rgba(0,0,0,0.7);color:#FFF;padding:12px;margin:5px auto;width:70%;border-radius:10px;text-align:left;'>{medal} {row['TITULO']} {row['NOMBRE']} — {int(row['PUNTOS'])} pts</div>", unsafe_allow_html=True)

    elif fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora

        st.markdown(f"<div class='pregunta-card'>❓ {p['q']}</div>", unsafe_allow_html=True)

        if t_limite == 0:
            st.markdown("<div class='espera-box'>⚖️ El Tribunal habilitará la votación en instantes...</div>", unsafe_allow_html=True)
            voto_bloqueado = True
        elif reloj_on and not ya_envio:
            secs = int(t_limite - ahora)
            st.markdown(f"<div style='text-align:center'><div class='reloj-container'>⏱️ {secs}s</div></div>", unsafe_allow_html=True)
            voto_bloqueado = False
        else:
            voto_bloqueado = True

        if not ya_envio:
            cols = st.columns(2)
            for i, opcion in enumerate(p["o"]):
                col = cols[i % 2]
                with col:
                    color = COLORES_OPCIONES[i % len(COLORES_OPCIONES)]
                    icono = ICONOS_OPCIONES[i % len(ICONOS_OPCIONES)]
                    
                    if not voto_bloqueado:
                        if st.button(f"{icono}  {opcion}", key=f"btn_{fase_serv}_{i}"):
                            # CONGELAMOS EL ESTADO INMEDIATAMENTE ANTES DE HACER LA PETICIÓN WEB
                            st.session_state.enviado = True
                            st.session_state.f_voto = fase_serv
                            
                            if opcion == p["k"]:
                                audio("exito")
                                pts = 10 + max(0, min(int(t_limite - ahora), 15))
                                llamar_api({"accion": "sumar_puntos", "usuario": {"email": user["email"], "pts": pts}})
                                st.session_state._respuesta_correcta = True
                                st.session_state._pts_ganados = pts
                            else:
                                audio("error")
                                st.session_state._respuesta_correcta = False
                                st.session_state._pts_ganados = 0
                            
                            st.rerun()
                    else:
                        st.markdown(f"<div class='kahoot-btn' style='background:{color};opacity:0.5;'>{icono} {opcion}</div>", unsafe_allow_html=True)
        else:
            # PANTALLA ESTÁTICA POST-VOTO (SIN TEMPORIZADOR NI TITILEO)
            correcto = st.session_state.get("_respuesta_correcta", False)
            pts_g    = st.session_state.get("_pts_ganados", 0)
            if correcto:
                st.markdown(f"<div style='background:rgba(38,137,12,0.85);color:#FFF;padding:20px;border-radius:15px;font-size:1.6rem;'>✅ ¡CORRECTO! +{pts_g} pts 🎉</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:rgba(226,27,60,0.85);color:#FFF;padding:20px;border-radius:15px;font-size:1.6rem;'>❌ INCORRECTO<br><small>Era: {p['k']}</small></div>", unsafe_allow_html=True)
            
            st.markdown("<br><p style='color:#CCFF00;font-size:1.2rem;font-weight:700;'>⏳ Dictamen enviado. Esperando al resto del Tribunal...</p>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 👥 En Vivo")
        if not df_alumnos.empty:
            st.table(df_alumnos[["TITULO","NOMBRE","PUNTOS"]].sort_values("PUNTOS", ascending=False))

    else:
        st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
        st.markdown("<div class='espera-box'>⚖️ El Tribunal está deliberando... Enseguida comenzamos.</div>", unsafe_allow_html=True)
        
        if not df_alumnos.empty:
            chips_html = "".join([f"<span class='participante-chip'>⚖️ {r['TITULO']} {r['NOMBRE']}</span>" for _, r in df_alumnos.iterrows()])
            st.markdown(f"<div style='text-align:center'>{chips_html}</div>", unsafe_allow_html=True)
