import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="LexPlay UBA", layout="wide")

def cargar_datos():
    if not os.path.exists("d.csv"): return pd.DataFrame(columns=["E", "A", "F", "P", "G"])
    try: return pd.read_csv("d.csv")
    except: return pd.DataFrame(columns=["E", "A", "F", "P", "G"])

def leer_f():
    if not os.path.exists("f.txt"): return ["0", "0"]
    try:
        with open("f.txt", "r") as x:
            cont = x.read().strip().split(",")
            return cont if len(cont) == 2 else ["0", "0"]
    except: return ["0", "0"]

def escribir_f(fase, t_limite):
    with open("f.txt", "w") as x:
        x.write(f"{fase},{t_limite}")
        x.flush()
        os.fsync(x.fileno())

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .stApp, .stMarkdown, p, h1, h2, h3, h4, label, span { color: #FFFFFF !important; font-family: 'Poppins', sans-serif; text-align: center; }
    .main .block-container { background: rgba(10, 25, 41, 0.92) !important; padding: 3rem !important; border-radius: 12px !important; border-top: 5px solid #D4AF37; max-width: 1000px !important; margin: auto; }
    
    /* TABLAS Y PANELES VISIBLES */
    [data-testid="stTable"], .stDataFrame, [data-testid="stDataFrame"] { background-color: white !important; border-radius: 8px; }
    [data-testid="stTable"] td, [data-testid="stTable"] th, [data-testid="stTable"] tr, .stDataFrame div, .stDataFrame span, .stDataFrame p { color: #000000 !important; font-weight: 600 !important; }
    [data-testid="stExpander"] { background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 8px; }
    [data-testid="stExpander"] * { color: #000000 !important; }
    
    .titulo-oro { color: #D4AF37 !important; font-size: 3.5rem !important; font-weight: 700; text-transform: uppercase; }
    
    /* PODIO CON LETRAS AMARILLAS */
    .podio-container { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-top: 20px; }
    .box-oro { background: linear-gradient(145deg, #D4AF37, #B8860B); color: #FFFF00 !important; padding: 20px; border-radius: 8px; width: 80%; font-size: 2rem; font-weight: 700; border: 2px solid white; }
    .box-plata { background: linear-gradient(145deg, #C0C0C0, #808080); color: #FFFF00 !important; padding: 15px; border-radius: 8px; width: 70%; font-size: 1.5rem; font-weight: 600; }
    .box-bronce { background: linear-gradient(145deg, #CD7F32, #8B4513); color: #FFFF00 !important; padding: 12px; border-radius: 8px; width: 60%; font-size: 1.2rem; font-weight: 600; }
    
    .reloj-float { position: fixed; top: 20px; right: 20px; background: #E31837; color: white !important; padding: 20px; border-radius: 8px; font-size: 3rem; font-weight: 700; border: 2px solid #D4AF37; z-index: 9999; }
    
    /* MENSAJE FINAL */
    .mensaje-final { color: #FFD700 !important; font-size: 2rem !important; font-weight: 700 !important; text-shadow: 2px 2px 8px #000000 !important; margin-top: 40px; padding: 20px; border-top: 2px solid #D4AF37; }
    
    .stButton>button { background-color: #D4AF37 !important; color: #0A1929 !important; font-weight: 700 !important;
