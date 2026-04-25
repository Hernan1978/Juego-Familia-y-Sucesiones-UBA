def aplicar_estilo():
    fondo_url = "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070"
    st.markdown(f"""
        <style>
        /* OCULTAR BARRA SUPERIOR (Fork, Deploy, etc) */
        header {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* AJUSTES VISUALES */
        .stApp {{ background-image: url("{fondo_url}"); background-size: cover; background-attachment: fixed; }}
        
        .main .block-container {{ 
            background-color: rgba(0, 0, 0, 0.85); 
            padding: 3rem 3rem; 
            border-radius: 20px; 
            border: 2px solid #D4AF37; 
            margin-top: 50px; /* Bajamos un poco el contenido */
        }}

        .reloj-container {{
            position: fixed; bottom: 30px; right: 30px; background-color: #C0392B; color: white;
            padding: 15px 25px; border-radius: 50px; border: 3px solid #D4AF37; z-index: 9999;
            font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7); animation: pulse 1s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        
        /* TEXTOS */
        h1, h2, h3, p, label, .stMarkdown, .stRadio label {{ 
            color: #FFFFFF !important; 
            text-shadow: 2px 2px 4px #000000; 
            font-size: 1.3rem !important; 
        }}
        
        .cartel-exito {{ 
            background-color: rgba(46, 204, 113, 0.4); 
            border: 3px solid #2ECC71; 
            padding: 40px; 
            border-radius: 15px; 
            text-align: center; 
            margin-top: 20px;
        }}
        
        .stButton>button {{ 
            background-color: #C0392B !important; 
            color: white !important; 
            font-size: 1.5rem !important; 
            height: 3.5rem; 
            width: 100%; 
            border: 1px solid #D4AF37;
        }}
        
        [data-testid="stSidebar"] {{ background-color: rgba(26, 58, 90, 1) !important; }}
        </style>
        """, unsafe_allow_html=True)
