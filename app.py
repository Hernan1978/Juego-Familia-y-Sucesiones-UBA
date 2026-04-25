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
    .stApp {{
        background-image: url("{img}");
        background-size: cover;
    }}
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
    h1, h2, h3, p, label {{
        color: white !important;
        text-shadow: 2px 2px black;
    }}
    .stButton>button {{
        background: #C0392B !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

style()

# --- 2. ARCHIVOS ---
def rd():
    try:
        if os.path.exists("f.txt"):
            return open("f.txt").read().strip()
    except:
        pass
    return "0"

def wr(v):
    with open("f.txt","w") as x:
        x.write(str(v))

if "t" not in st.session_state:
    st.session_state.t = 0

# --- 3. LOGICA ---
f_val = rd()
f = int(f_val) if f_val.isdigit() else 0

# ADMIN con ?a=1
if st.query_params.get("a")=="1":
    with st.sidebar:
        st.write("MANDO JUEZ")
        if st.button("BORRAR DATOS"):
            if os.path.exists("d.csv"):
                os.remove("d.csv")
            wr("0")
            st.session_state.t = 0
            st.rerun()
        
        op = ["0","1","2","3","99"]
        s = st.selectbox("Fase:", op)
        if st.button("CAMBIAR"):
            wr(s)
            st.session_state.t = 0
            st.rerun()
            
        if st.button("INICIAR 20s"):
            st.session_state.t = time.time() + 21
            st.rerun()

# --- 4. LOGIN ---
if 'u' not in st.session_state:
    st.session_state.u = None

if not st.session_state.u:
    st.title("REGISTRO")
    email = st.text_input("Email:")
    alias = st.text_input("Alias:")
    if st.button("ENTRAR") and email and alias:
        if not os.path.exists("d.csv"):
            pd.DataFrame(
                columns=["E","A","F","P"]
            ).to_csv("d.csv", index=False)
        
        df_log = pd.DataFrame(
            [[email, alias, 0, 0]], 
            columns=["E","A","F","P"]
        )
        df_log.to_csv(
            "d.csv", mode='a', 
            header=False, index=False
        )
        st.session_state.u = {"e":email, "a":alias}
        st.rerun()
    st.stop()

# --- 5. TIEMPO ---
v_hecho = False
if os.path.exists("d.csv"):
    try:
        dx = pd.read_csv("d.csv")
        m_u = st.session_state.u["e"]
        v_hecho = not dx[(dx.E==m_u)&(dx.F==f)].empty
    except:
        pass

now = time.time()
puede_votar = False
if 0 < f < 99 and not v_hecho:
    if st.session_state.t > now:
        seg = int(st.session_state.t - now)
        st.markdown(
            f'<div class="reloj">{seg}s</div>',
            unsafe_allow_html=True
        )
        puede_votar = True

# --- 6. VISTAS ---
if f == 0:
    st.header("SALA DE ESPERA")
    st.write("Aguarde al inicio...")
elif f == 99:
    st.header("PODIO")
    if os.path.exists("d.csv"):
        dz = pd.read_csv("d.csv")
        res = dz[dz.F>0].groupby("A").P.sum()
        st.table(res.sort_values(ascending=False))
else:
    if v_hecho:
        st.success("VOTO RECIBIDO")
    else:
        # Preguntas cortas
        qs = {
            1: ["Legitima?","2/3","1/2"],
            2: ["Plazo?","10a","5a"],
            3: ["Maquina?","No","Si"]
        }
        st.header(f"RONDA {f}")
        st.write(f"### {qs[f][0]}")
        rt = st.radio("Op:", qs[f][1:])
        
        if st.button("ENVIAR", disabled=not puede_votar):
            puntos = 100 if rt==qs[f][1] else 0
            u = st.session_state.u
            new_row = pd.DataFrame(
                [[u["e"], u["a"], f, puntos]], 
                columns=["E","A","F","P"]
            )
            new_row.to_csv(
                "d.csv", mode='a', 
                header=False, index=False
            )
            st.rerun()
        
        if not puede_votar:
            st.warning("Esperando reloj...")

# --- 7. MONITOR ---
st.write("---")
if os.path.exists("d.csv"):
    try:
        dm = pd.read_csv("d.csv")
        lista = dm[dm.F==0].A.unique()
        cols = st.columns(4)
        for i, n in enumerate(lista):
            check = not dm[(dm.A==n)&(dm.F==f)].empty
            icon = "✅" if check else "👤"
            cols[i%4].write(f"{icon} {n}")
    except:
        pass

# Refresco
if st.session_state.t > now or f==0:
    time.sleep(1)
    st.rerun()
