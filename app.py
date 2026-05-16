import streamlit as st
import pandas as pd
import time
import requests

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(page_title="LexPlay UBA", layout="wide")

# 🚨 REEMPLAZÁ con tu nueva URL de Google Apps Script 🚨
URL_APPS_SCRIPT = "https://docs.google.com/spreadsheets/d/1ZcXOkFeMgHZFchQfDKxPWaH516b7sO9LIiO9MibvP5Q/edit?usp=sharing"

CLAVE_DOCENTE = "derecho2024"

# URLs de audio en GitHub
AUDIO = {
    "bienvenida": "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/bienvenida.mp3",
    "exito":      "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/exito.mp3",
    "error":      "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/error.mp3",
    "ganador":    "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/ganador.mp3",
}

IMG_BASE = "https://raw.githubusercontent.com/Hernan1978/Juego-Familia-y-Sucesiones-UBA/main/"

# Colores Kahoot-style para las opciones (máx 4)
COLORES_OPCIONES = ["#E21B3C", "#1368CE", "#26890C", "#FFA602"]
ICONOS_OPCIONES  = ["▲", "◆", "●", "■"]

# ============================================================
# ESTILOS
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
    cursor: pointer; border: 3px solid rgba(255,255,255,0.4);
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    transition: transform 0.1s;
    min-height: 80px;
}
.kahoot-btn:hover { transform: scale(1.02); }
.participante-chip {
    display: inline-block; background: rgba(212,175,55,0.3);
    border: 2px solid #D4AF37; border-radius: 20px;
    padding: 6px 16px; margin: 4px; color: #CCFF00 !important;
    font-weight: 700; font-size: 0.95rem;
}
.panel-card {
    background: rgba(0,0,0,0.75); border: 2px solid #D4AF37;
    border-radius: 15px; padding: 20px; margin: 10px 0;
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
# FUNCIONES AUXILIARES
# ============================================================
def audio(key):
    url = AUDIO.get(key, "")
    if url:
        st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

def tictac_js():
    """Genera un tictac con la Web Audio API del navegador (sin archivo externo)"""
    st.markdown("""
    <script>
    (function(){
        if(window._tictacInterval) return;
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function tick(){
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.connect(g); g.connect(ctx.destination);
            o.frequency.value = 880;
            g.gain.setValueAtTime(0.3, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
            o.start(ctx.currentTime); o.stop(ctx.currentTime + 0.1);
        }
        tick();
        window._tictacInterval = setInterval(tick, 1000);
        setTimeout(()=>{ clearInterval(window._tictacInterval); window._tictacInterval=null; }, 30000);
    })();
    </script>
    """, unsafe_allow_html=True)

def fetch_remoto():
    try:
        res = requests.get(URL_APPS_SCRIPT, timeout=6)
        return res.json()
    except:
        return None

def limpiar_cache():
    pass  # sin cache, no hay nada que limpiar

def llamar_api(payload):
    limpiar_cache()
    try:
        res = requests.post(URL_APPS_SCRIPT, json=payload, timeout=7)
        return res.json()
    except:
        return {"ok": False}

def cargar_datos():
    """Carga datos desde Google. Compatible con formato nuevo (sistema/alumnos/preguntas)
    y formato viejo (lista plana con columna E/F/P)."""
    data = fetch_remoto()

    if data is None:
        # Sin conexión: usar caché local
        return (
            st.session_state.get("_cache_sistema",   {"fase": 0, "tiempo": 0}),
            st.session_state.get("_cache_alumnos",   []),
            st.session_state.get("_cache_preguntas", [])
        )

    # ── Formato NUEVO: {"sistema":{...}, "alumnos":[...], "preguntas":[...]} ──
    if isinstance(data, dict) and "sistema" in data:
        sistema_raw = data.get("sistema", {})
        # Normalizar claves por si vienen en mayúsculas
        sistema = {
            "fase":   int(sistema_raw.get("fase",   sistema_raw.get("FASE",   0))),
            "tiempo": float(sistema_raw.get("tiempo", sistema_raw.get("TIEMPO", 0.0)))
        }
        st.session_state._cache_sistema   = sistema
        st.session_state._cache_alumnos   = data.get("alumnos",   [])
        st.session_state._cache_preguntas = data.get("preguntas", [])

    # ── Formato VIEJO: lista plana de filas con columnas E, F, P, A, G ──
    elif isinstance(data, list) and len(data) > 0:
        try:
            df = pd.DataFrame(data)
            df.columns = [str(c).strip().upper() for c in df.columns]
            df["E_STR"] = df["E"].astype(str).str.strip().str.upper()

            # Fila SISTEMA
            fila_sis = df[df["E_STR"] == "SISTEMA"]
            fase_v   = int(fila_sis["F"].iloc[0])   if not fila_sis.empty else 0
            tiempo_v = float(fila_sis["P"].iloc[0]) if not fila_sis.empty else 0.0
            st.session_state._cache_sistema = {"fase": fase_v, "tiempo": tiempo_v}

            # Alumnos (todo excepto SISTEMA)
            df_al = df[df["E_STR"] != "SISTEMA"]
            alumnos_v = []
            for _, row in df_al.iterrows():
                alumnos_v.append({
                    "EMAIL":  str(row.get("E", "")),
                    "NOMBRE": str(row.get("A", "")),
                    "TITULO": str(row.get("G", "Dr.")),
                    "PUNTOS": float(row.get("P", 0))
                })
            st.session_state._cache_alumnos   = alumnos_v
            st.session_state._cache_preguntas = st.session_state.get("_cache_preguntas", [])
        except Exception as ex:
            st.session_state.setdefault("_cache_sistema",   {"fase": 0, "tiempo": 0})
            st.session_state.setdefault("_cache_alumnos",   [])
            st.session_state.setdefault("_cache_preguntas", [])

    return (
        st.session_state.get("_cache_sistema",   {"fase": 0, "tiempo": 0}),
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
# SESSION STATE
# ============================================================
for k, v in {
    "user": None, "f_voto": -1, "enviado": False,
    "ultimo_refresh": 0.0, "audio_reproducido": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# PANTALLA DE LOGIN
# ============================================================
if st.session_state.user is None:
    if st.session_state.audio_reproducido != "bienvenida":
        audio("bienvenida")
        st.session_state.audio_reproducido = "bienvenida"

    st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#CCFF00;font-size:1.1rem;font-weight:700;text-shadow:2px 2px 4px #000;'>Derecho de Familia y Sucesiones</p>", unsafe_allow_html=True)

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
# CARGAR DATOS GLOBALES
# ============================================================
sistema, alumnos_raw, preguntas_raw = cargar_datos()

fase_serv = int(sistema.get("fase", 0))
t_limite  = float(sistema.get("tiempo", 0))
ahora     = time.time()

df_alumnos = alumnos_a_df(alumnos_raw)
banco      = preguntas_a_banco(preguntas_raw)

fases_opciones = {0: "⏸ Sala de Espera"}
for k in sorted(banco.keys()):
    fases_opciones[k] = f"❓ Pregunta {k}"
fases_opciones[88] = "📊 Resultados Parciales"
fases_opciones[99] = "🏆 PODIO FINAL"

# ============================================================
# AUTO-REFRESCO VIA JAVASCRIPT
# Streamlit no puede refrescarse solo en background.
# Usamos JS para hacer window.location.reload() automatico.
# El intervalo cambia segun si el reloj esta corriendo o no.
# ============================================================
def inject_autoreload(intervalo_ms):
    st.markdown(
        f"""
        <script>
        (function(){{
            if (window._lexReloadTimer) clearInterval(window._lexReloadTimer);
            window._lexReloadTimer = setInterval(function(){{
                window.location.reload();
            }}, {intervalo_ms});
        }})();
        </script>
        """,
        unsafe_allow_html=True
    )

if st.session_state.user.get("tipo") == "alumno":
    reloj_activo = (t_limite > ahora) and (fase_serv in banco) and not st.session_state.enviado
    if reloj_activo:
        inject_autoreload(2000)   # cada 2s cuando corre el reloj
    else:
        inject_autoreload(4000)   # cada 4s en espera / entre preguntas

# ============================================================
# ██████  PANEL DOCENTE
# ============================================================
if st.session_state.user["tipo"] == "juez":
    st.markdown("<h1 class='titulo-oro'>⚖️ PANEL DOCENTE</h1>", unsafe_allow_html=True)

    # — Fila de botones de control —
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        op_fase = st.selectbox("📋 Cambiar a:", options=list(fases_opciones.keys()),
                               format_func=lambda x: fases_opciones[x], key="sel_fase")
        if st.button("📢 ENVIAR"):
            llamar_api({"accion": "escribir_sistema", "fase": op_fase, "tiempo": 0.0})
            limpiar_cache()
            st.rerun()

    with c2:
        t_set = st.number_input("⏱ Segundos:", min_value=5, max_value=120, value=30)
        if st.button("▶️ INICIAR RELOJ"):
            llamar_api({"accion": "escribir_sistema", "fase": fase_serv, "tiempo": ahora + t_set})
            limpiar_cache()
            st.rerun()

    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 REFRESCAR"):
            limpiar_cache()
            st.rerun()

    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 PARCIALES"):
            llamar_api({"accion": "escribir_sistema", "fase": 88, "tiempo": 0.0})
            limpiar_cache()
            st.rerun()

    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏆 PODIO FINAL"):
            llamar_api({"accion": "escribir_sistema", "fase": 99, "tiempo": 0.0})
            limpiar_cache()
            st.rerun()

    with c6:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚠️ RESET TODO"):
            llamar_api({"accion": "reset_alumnos"})
            limpiar_cache()
            st.session_state.clear()
            st.rerun()

    st.markdown("---")

    # — Pregunta actual visible para el docente —
    if fase_serv in banco:
        p = banco[fase_serv]
        st.markdown(f"<div class='pregunta-card'>❓ {p['q']}<br><small style='color:#D4AF37'>✅ Correcta: {p['k']}</small></div>", unsafe_allow_html=True)

    # — Estado actual —
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### 📋 Lista de Preguntas")
        if banco:
            for kid, pdata in sorted(banco.items()):
                activa = "🟢 " if kid == fase_serv else "⚪ "
                st.markdown(
                    f"<div style='background:rgba(0,0,0,0.6);border-radius:8px;padding:8px 14px;margin:4px 0;"
                    f"color:#FFF;text-align:left;border-left:4px solid {'#26890C' if kid==fase_serv else '#555'};'>"
                    f"{activa}<b>P{kid}:</b> {pdata['q'][:60]}{'...' if len(pdata['q'])>60 else ''}"
                    f"</div>", unsafe_allow_html=True
                )
        else:
            st.info("No hay preguntas cargadas en el Sheet (Hoja PREGUNTAS).")

    with col_b:
        st.markdown("### 👥 Participantes")
        if not df_alumnos.empty:
            df_show = df_alumnos[["TITULO","NOMBRE","PUNTOS"]].sort_values("PUNTOS", ascending=False).copy()
            df_show.index = range(1, len(df_show)+1)
            st.table(df_show)
        else:
            st.info("Aún no hay participantes.")

    # — Botón salir —
    st.markdown("---")
    if st.button("🚪 CERRAR SESIÓN DOCENTE"):
        st.session_state.clear()
        st.rerun()

# ============================================================
# ████████  PANTALLA ALUMNO
# ============================================================
else:
    user = st.session_state.user

    # Reset enviado si cambió la fase
    if st.session_state.f_voto != fase_serv:
        st.session_state.enviado = False

    ya_envio = st.session_state.enviado

    # ── PODIO FINAL ──────────────────────────────────────────
    if fase_serv == 99:
        if st.session_state.audio_reproducido != "ganador":
            audio("ganador")
            st.session_state.audio_reproducido = "ganador"
        st.balloons(); st.snow()

        podio = df_alumnos.sort_values("PUNTOS", ascending=False).head(3)

        if not podio.empty:
            ganador = podio.iloc[0]
            img_file = "alumna_festejo_uba.png" if ganador["TITULO"] == "Dra." else "alumno_festejo_uba.png"
            st.image(IMG_BASE + img_file, use_container_width=True)
            st.markdown(f"<h1 class='titulo-oro'>🏆 {ganador['TITULO']} {ganador['NOMBRE']} 🏆</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='box-oro'>🥇 ORO: {ganador['NOMBRE']}<br><span style='font-size:1.5rem'>{int(ganador['PUNTOS'])} puntos</span></div><br>", unsafe_allow_html=True)
            if len(podio) > 1:
                s = podio.iloc[1]
                st.markdown(f"<div class='box-plata'>🥈 PLATA: {s['NOMBRE']} — {int(s['PUNTOS'])} pts</div><br>", unsafe_allow_html=True)
            if len(podio) > 2:
                t = podio.iloc[2]
                st.markdown(f"<div class='box-bronce'>🥉 BRONCE: {t['NOMBRE']} — {int(t['PUNTOS'])} pts</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.clear()
            st.rerun()

    # ── RESULTADOS PARCIALES ─────────────────────────────────
    elif fase_serv == 88:
        st.markdown("<h2>📊 Resultados Parciales</h2>", unsafe_allow_html=True)
        podio_p = df_alumnos.sort_values("PUNTOS", ascending=False)
        if not podio_p.empty:
            for i, (_, row) in enumerate(podio_p.iterrows()):
                medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}°"
                color = ["#D4AF37","#C0C0C0","#CD7F32"][i] if i < 3 else "#444"
                st.markdown(
                    f"<div style='background:rgba(0,0,0,0.7);border-left:6px solid {color};"
                    f"border-radius:10px;padding:12px 20px;margin:6px auto;width:70%;color:#FFF;"
                    f"font-size:1.2rem;font-weight:700;text-align:left;'>"
                    f"{medal} {row['TITULO']} {row['NOMBRE']} — {int(row['PUNTOS'])} pts</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("Aún no hay puntuaciones.")

    # ── PREGUNTA ACTIVA ──────────────────────────────────────
    elif fase_serv in banco:
        p = banco[fase_serv]
        reloj_on = t_limite > ahora

        # Pregunta
        st.markdown(f"<div class='pregunta-card'>❓ {p['q']}</div>", unsafe_allow_html=True)

        # Estado del reloj
        if t_limite == 0:
            st.markdown("<div class='espera-box'>⚖️ El Tribunal habilitará la votación en instantes...<br><small>Preparate para responder</small></div>", unsafe_allow_html=True)
            voto_bloqueado = True

        elif reloj_on and not ya_envio:
            secs = int(t_limite - ahora)
            st.markdown(f"<div style='text-align:center'><div class='reloj-container'>⏱️ {secs}s</div></div>", unsafe_allow_html=True)
            tictac_js()
            voto_bloqueado = False

        elif not reloj_on and not ya_envio:
            st.markdown("<div style='text-align:center'><div class='reloj-container' style='color:gray;border-color:gray;animation:none'>⌛ TIEMPO AGOTADO</div></div>", unsafe_allow_html=True)
            voto_bloqueado = True

        else:
            voto_bloqueado = True

        # Botones de respuesta estilo Kahoot
        if not ya_envio:
            cols = st.columns(2)
            for i, opcion in enumerate(p["o"]):
                col = cols[i % 2]
                with col:
                    color = COLORES_OPCIONES[i % len(COLORES_OPCIONES)]
                    icono = ICONOS_OPCIONES[i % len(ICONOS_OPCIONES)]
                    # Botón visual
                    if not voto_bloqueado:
                        if st.button(f"{icono}  {opcion}", key=f"op_{fase_serv}_{i}",
                                     help=f"Opción {i+1}"):
                            # Procesar respuesta
                            if opcion == p["k"]:
                                audio("exito")
                                bonus = max(0, min(int(t_limite - ahora), 15))
                                pts = 10 + bonus
                                llamar_api({
                                    "accion": "sumar_puntos",
                                    "usuario": {"email": user["email"], "pts": pts}
                                })
                                st.session_state._respuesta_correcta = True
                                st.session_state._pts_ganados = pts
                            else:
                                audio("error")
                                st.session_state._respuesta_correcta = False
                                st.session_state._pts_ganados = 0

                            st.session_state.enviado = True
                            st.session_state.f_voto = fase_serv
                            limpiar_cache()
                            st.rerun()
                    else:
                        # Botón deshabilitado pero visible
                        st.markdown(
                            f"<div class='kahoot-btn' style='background:{color};opacity:0.5;'>"
                            f"{icono} {opcion}</div>",
                            unsafe_allow_html=True
                        )
        else:
            # Ya votó — mostrar resultado
            correcto = st.session_state.get("_respuesta_correcta", False)
            pts_g    = st.session_state.get("_pts_ganados", 0)
            if correcto:
                st.markdown(
                    f"<div style='background:rgba(38,137,12,0.85);border-radius:15px;padding:20px;"
                    f"color:#FFF;font-size:1.6rem;font-weight:800;margin:10px auto;width:70%;'>"
                    f"✅ ¡CORRECTO! +{pts_g} puntos 🎉</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='background:rgba(226,27,60,0.85);border-radius:15px;padding:20px;"
                    f"color:#FFF;font-size:1.6rem;font-weight:800;margin:10px auto;width:70%;'>"
                    f"❌ Respuesta incorrecta<br><small>La correcta era: {p['k']}</small></div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                "<div style='color:#CCFF00;font-size:1.1rem;font-weight:700;margin-top:10px;"
                "text-shadow:2px 2px 4px #000;'>⏳ Esperando que el resto responda...</div>",
                unsafe_allow_html=True
            )

        # Tabla de participantes en vivo (debajo de las opciones)
        st.markdown("---")
        st.markdown("### 👥 En Vivo")
        if not df_alumnos.empty:
            df_show = df_alumnos[["TITULO","NOMBRE","PUNTOS"]].sort_values("PUNTOS", ascending=False).copy()
            df_show.index = range(1, len(df_show)+1)
            st.table(df_show)

    # ── SALA DE ESPERA ───────────────────────────────────────
    else:
        st.markdown("<h1 class='titulo-oro'>🏛️ LEXPLAY UBA</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div class='espera-box'>"
            "⚖️ El Tribunal está deliberando...<br>"
            "<span style='font-size:1.1rem;color:#FFF;font-weight:400'>Enseguida comenzamos. ¡Preparate!</span>"
            "</div>",
            unsafe_allow_html=True
        )

        # Chips de participantes conectados
        st.markdown("<br><p style='color:#D4AF37;font-size:1.2rem;font-weight:800;text-shadow:2px 2px 4px #000;'>👥 Participantes conectados:</p>", unsafe_allow_html=True)
        if not df_alumnos.empty:
            chips_html = ""
            for _, row in df_alumnos.iterrows():
                chips_html += f"<span class='participante-chip'>⚖️ {row['TITULO']} {row['NOMBRE']}</span>"
            st.markdown(f"<div style='text-align:center'>{chips_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#FFF;'>Aún no hay participantes registrados...</p>", unsafe_allow_html=True)

        st.markdown(
            "<br><p style='color:#888;font-size:0.85rem;'>La página se actualiza automáticamente cada 8 segundos</p>",
            unsafe_allow_html=True
        )
