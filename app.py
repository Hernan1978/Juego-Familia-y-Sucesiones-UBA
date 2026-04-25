import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTILO ---
st.set_page_config(layout="wide")
def style():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
    <style>
    header {{ visibility: hidden; }}
    .stApp {{ background-image: url("{img}"); background-size: cover; }}
    .main .block-container {{
        background: rgba(0,0,0,0.85);
        padding: 2rem !important;
        border: 3px solid #D4AF37;
        border-radius: 20px;
    }}
    .reloj {{
        position: fixed; top: 20px; right: 20px;
        background: #C0392B; color: white;
        padding: 15px; border: 2px solid #D4AF37;
        border-radius: 50px; font-size: 2rem; z-index: 999;
    }}
    h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px black; }}
    .stButton>button {{ background: #C0392B !important; color: white !important; border: 1px solid #D4AF37; }}
    </style>
    """, unsafe_allow_html=True)
style()

# --- 2. ARCHIVOS ---
def rd():
    if os.path.exists("f.txt"):
        return open("f.txt").read().strip()
    return "0"

def wr(v):
    with open("f.txt","w") as x:
        x.write(str(v))

if "t" not in st.session_state:
    st.session_state.t = 0

f_val = rd()
f = int(f_val) if f_val.isdigit() else 0

# --- 3. PANEL JUEZ (RESTAURADO ?admin=true) ---
if st.query_params.get("admin") == "true":
    with st.sidebar:
        st.title("⚖️ MANDO JUEZ")
        if st.button("🗑️ REINICIAR TODO"):
            if os.path.exists("d.csv"): os.remove("d.csv")
            wr("0"); st.session_state.t = 0; st.rerun()
        
        ops = ["Sala de Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Podio Final"]
        sel = st.selectbox("Cambiar fase:", ops)
        if st.button("LANZAR FASE"):
            nv = 0 if "Sala" in sel else (99 if "Podio" in sel else int(sel.split(" ")[1]))
            wr(str(nv)); st.session_state.t = 0; st.rerun()
            
        if 0 < f < 99:
            if st.button("⏱️ INICIAR 20 SEGUNDOS"):
                st.session_state.t = time.time() + 21
                st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state:
    st.session_state.u = None

if not st.session_state.u:
    st.title("⚖️ REGISTRO DE LETRADOS")
    e, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("INGRESAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv", index=False)
        df_l = pd.DataFrame([[e, a, 0, 0]], columns=["E","A","F","P"])
        df_l.to_csv("d.csv", mode='a', header=False, index=False)
        st.session_state.u = {"e":e, "a":a}; st.rerun()
    st.stop()

# --- 5. LÓGICA ---
v_ok = False
if os.path.exists("d.csv"):
    dx = pd.read_csv("d.csv")
    m_u = st.session_state.u["e"]
    v_ok = not dx[(dx.E==m_u)&(dx.F==f)].empty

now = time.time()
ok = False
if 0 < f < 99 and not v_ok:
    if st.session_state.t > now:
        r = int(st.session_state.t - now)
        st.markdown(f'<div class="reloj">⌛ {r}s</div>', unsafe_allow_html=True)
        ok = True

# --- 6. VISTAS ---
if f == 0:
    st.header("🏛️ Sala de Espera")
    st.write(f"Bienvenido Dr. {st.session_state.u['a']}")
elif f == 99:
    st.header("🏆 Podio Final")
    if os.path.exists("d.csv"):
        dz = pd.read_csv("d.csv")
        st.table(dz[dz.F>0].groupby("A").P.sum().sort_values(ascending=False))
else:
    if v_ok:
        st.success("✅ Veredicto enviado")
    else:
        qs = {1: ["¿Legítima?", "2/3", "1/2"], 2: ["¿Plazo?", "10a", "5a"], 3: ["¿Máquina?", "No", "Si"]}
        st.header(f"Ronda {f}"); st.write(f"### {qs[f][0]}")
        rt = st.radio("Veredicto:", qs[f][1:])
        if st.button("ENVIAR", disabled=not ok):
            pts = 100 if rt==qs[f][1] else 0
            nr = [[st.session_state.u["e"], st.session_state.u["a"], f, pts]]
            df3 = pd.DataFrame(nr, columns=["E","A","F","P"])
            df3.to_csv("d.csv", mode='a', header=False, index=False)
            st.rerun()

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    dm = pd.read_csv("d.csv")
    al = dm[dm.F==0].A.unique()
    cs = st.columns(4)
    for i, n in enumerate(al):
        stt = "✅" if not dm[(dm.A==n)&(dm.F==f)].empty else "👤"
        cs[i%4].write(f"{stt} {n}")

if st.session_state.t > now or f==0:
    time.sleep(1); st.rerun()
