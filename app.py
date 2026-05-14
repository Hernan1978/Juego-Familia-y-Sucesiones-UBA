if clave == "derecho2024":
        # Contenedor con fondo oscuro para que resalte el texto
        st.markdown("""
            <style>
            .caja-admin { 
                background: rgba(0, 0, 0, 0.7); 
                padding: 20px; 
                border-radius: 15px; 
                border: 1px solid #D4AF37;
                margin-bottom: 20px;
            }
            .lista-nombres { color: #D4AF37 !important; font-size: 1.2rem; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="caja-admin">', unsafe_allow_html=True)
            if os.path.exists("asistencia.csv"):
                df_asist = pd.read_csv("asistencia.csv")
                nombres = df_asist['Nombre'].unique()
                st.write(f"### 📋 Alumnos presentes: {len(nombres)}")
                
                # Aquí mostramos los nombres en pantalla
                st.markdown('<div class="lista-nombres">' + ", ".join(nombres) + '</div>', unsafe_allow_html=True)
                
                st.write("") # Espacio
                st.download_button("📥 Descargar Lista de Presentes (Excel/CSV)", df_asist.to_csv(index=False), "presentes.csv", "text/csv")
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sel = st.selectbox("Fase:", ["Espera", "Pregunta 1", "Pregunta 2", "Pregunta 3", "Resultados Parciales", "Podio Final"])
            if st.button("CAMBIAR FASE"):
                m = {"Espera":0, "Pregunta 1":1, "Pregunta 2":2, "Pregunta 3":3, "Resultados Parciales":10, "Podio Final":99}
                escribir_f(m[sel], 0); st.rerun()
        with col2:
            t_set = st.number_input("Segundos:", 5, 60, 25)
            if st.button("🚀 INICIAR RELOJ"):
                escribir_f(fase, time.time() + t_set); st.rerun()
        with col3:
            if st.button("⚠️ REINICIAR"):
                for f in ["d.csv", "f.txt", "asistencia.csv"]:
                    if os.path.exists(f): os.remove(f)
                st.rerun()
