import streamlit as st
import pandas as pd
import os
import time

# --- 1. ESTILO ---
st.set_page_config(page_title="LexPlay", layout="wide")
def style():
    img = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
    <style>
    header {{visibility:hidden;}}
    .stApp {{background-image:url("{img}");background-size:cover;}}
    .main .block-container {{
        background:rgba(0,0,0,0.85);padding:2rem;
        border-radius:15px;border:2px solid #D4AF37;
    }}
    .reloj {{
        position:fixed;top:20px;right:20px;background:#C0392B;
        color:white;padding:10px 20px;border-radius:30px;
        border:2px solid #D4AF37;z-index:99;font-size:2rem;
    }}
    h1,h2,h3,p,label {{color:white !important;}}
    .stButton>button {{background:#C0392B !important;color:white !important;}}
    </style>""", unsafe_allow_html=True)
style()

# --- 2. DATA ---
def rd(n): return open(n,"r").read().strip() if os.path.exists(n) else "0"
def wr(n,v): open(n,"w").write(str(v))

f = int(rd("f.txt"))
tm = rd("t.txt","OFF")

# --- 3. JUEZ ---
if st.query_params.get("admin")=="true":
    with st.sidebar:
        pw = st.text_input("Clave:",type="password")
        if pw=="derecho2024":
            if st.button("BORRAR"):
                if os.path.exists("d.csv"): os.remove("d.csv")
                wr("f.txt","0"); wr("t.txt","OFF"); st.rerun()
            sel = st.selectbox("Fase:",["0","1","2","3","99"],index=0)
            if st.button("IR"):
                wr("f.txt",sel); wr("t.txt","OFF"); st.rerun()
            if f in [1,2,3]:
                if st.button("TIEMPO"):
                    wr("t.txt",str(time.time()+20)); st.rerun()

# --- 4. USER ---
if 'u' not in st.session_state: st.session_state.u=None
if not st.session_state.u:
    st.title("REGISTRO")
    e, a = st.text_input("Email:"), st.text_input("Alias:")
    if st.button("ENTRAR") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv",index=False)
        df=pd.read_csv("d.csv")
        if df[(df.E==e)&(df.F==0)].empty:
            pd.DataFrame([[e,a,0,0]],columns=["E","A","F","P"]).to_csv("d.csv",mode='a',header=False,index=False)
        st.session_state.u={"e":e,"a":a}; st.rerun()
    st.stop()

# --- 5. LÓGICA ---
v = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    v = not df_v[(df_v.E==st.session_state.u['e'])&(df_v.F==f)].empty

act = False
if f in [1,2,3] and not v and tm!="OFF":
    r = int(float(tm)-time.time())
    if r>0:
        st.markdown(f'<div class="reloj">⌛ {r}s</div>',unsafe_allow_html=True)
        act = True
    else: wr("t.txt","OFF"); st.rerun()

# --- 6. VISTAS ---
if f==0: st.header("Sala de Espera")
elif f==99:
    st.header("PODIO")
    if os.path.exists("d.csv"):
        st.table(pd.read_csv("d.csv").groupby("A").P.sum())
else:
    if v: st.success("
