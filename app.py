import streamlit as st
import pandas as pd
import os
import time

# --- ESTILO ---
st.set_page_config(layout="wide")
def style():
    st.markdown("""
    <style>
    header {visibility:hidden;}
    .stApp {background: #1a1a1a;}
    .main .block-container {
        background: #000;
        border: 2px solid #D4AF37;
        color: white;
    }
    .reloj {
        position:fixed; top:20px;
        right:20px; background:#C0392B;
        color:white; padding:10px;
        font-size:2rem; z-index:99;
        border-radius:10px;
    }
    </style>""", unsafe_allow_html=True)
style()

# --- FUNCIONES ---
def rd(n):
    if os.path.exists(n):
        return open(n,"r").read().strip()
    return "0"

def wr(n,v):
    with open(n,"w") as f:
        f.write(str(v))

f = int(rd("f.txt"))
t_l = rd("t.txt","OFF")

# --- JUEZ ---
if st.query_params.get("admin")=="true":
    with st.sidebar:
        pw = st.text_input("Pw:",type="password")
        if pw=="derecho2024":
            if st.button("RESET"):
                if os.path.exists("d.csv"):
                    os.remove("d.csv")
                wr("f.txt","0")
                wr("t.txt","OFF")
                st.rerun()
            s = st.selectbox("F:",["0","1","2","3","99"])
            if st.button("IR"):
                wr("f.txt",s)
                wr("t.txt","OFF")
                st.rerun()
            if f in [1,2,3]:
                if st.button("TIEMPO"):
                    wr("t.txt",str(time.time()+20))
                    st.rerun()

# --- LOGIN ---
if 'u' not in st.session_state:
    st.session_state.u=None
if not st.session_state.u:
    st.title("REGISTRO")
    e = st.text_input("Email:")
    a = st.text_input("Alias:")
    if st.button("OK") and e and a:
        if not os.path.exists("d.csv"):
            pd.DataFrame(columns=["E","A","F","P"]).to_csv("d.csv",index=False)
        df=pd.read_csv("d.csv")
        pd.DataFrame([[e,a,0,0]],columns=["E","A","F","P"]).to_csv("d.csv",mode='a',header=False,index=False)
        st.session_state.u={"e":e,"a":a}
        st.rerun()
    st.stop()

# --- LOGICA ---
v = False
if os.path.exists("d.csv"):
    df_v = pd.read_csv("d.csv")
    v = not df_v[(df_v.E==st.session_state.u['e'])&(df_v.F==f)].empty

act = False
if f in [1,2,3] and not v and t_l!="OFF":
    r = int(float(t_l)-time.time())
    if r>0:
        st.markdown(f'<div class="reloj">{r}s</div>',unsafe_allow_html=True)
        act = True
    else:
        wr("t.txt","OFF")
        st.rerun()

# --- VISTAS ---
if f==0:
    st.write("ESPERE AL JUEZ")
elif f==99:
    st.write("FIN")
    if os.path.exists("d.csv"):
        st.table(pd.read_csv("d.csv").groupby("A").P.sum())
else:
    if v:
        st.write("ENVIADO")
    else:
        qs = {1:["Preg 1","A","B"],2:["Preg 2","C","D"],3:["Preg 3","E","F"]}
        st.write(qs[f][0])
        an = st.radio("Op:",qs[f][1:])
        if st.button("VOTAR",disabled=not act):
            p = 100 if an==qs[f][1] else 0
            pd.DataFrame([[st.session_state.u['e'],st.session_state.u['a'],f,p]],columns=["E","A","F","P"]).to_csv("d.csv",mode='a',header=False,index=False)
            st.rerun()

# --- LISTA ---
if os.path.exists("d.csv"):
    df_p = pd.read_csv("d.csv")
    al = df_p[df_p.F==0].A.unique()
    for n in al:
        st.write(f"USER: {n}")

if t_l!="OFF" or f==0:
    time.sleep(1)
    st.rerun()
