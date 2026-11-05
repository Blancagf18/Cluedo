import streamlit as st
import random
# Importamos exactamente lo que existe en tu motor v11 (motor.py)
from motor import construir_mazo, SOSPECHOSOS, MOTIVOS_POR_SOSPECHOSO, DATA_ARMAS

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Misterio: Detective",
    page_icon="🕵️",
    layout="centered"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .carta-oculta {
        padding: 15px;
        background-color: #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: center;
        border: 2px dashed #999;
        color: #555;
    }
    .carta-visible {
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
        color: #31333F;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    .titulo-juego {
        text-align: center;
        color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DEL ESTADO ---
if 'juego_iniciado' not in st.session_state:
    st.session_state.juego_iniciado = False
    st.session_state.verdad = {}
    st.session_state.mazo = []
    st.session_state.dificultad = ""
    st.session_state.cartas_reveladas = set()

# --- PREPARAR LISTAS PARA DESPLEGABLES ---
LISTA_ARMAS = sorted(list(DATA_ARMAS.keys()))
LISTA_MOTIVOS = sorted(list(set(m for lista in MOTIVOS_POR_SOSPECHOSO.values() for m in lista)))

# =============================================================================
# PANTALLA 1: MENÚ PRINCIPAL
# =============================================================================
if not st.session_state.juego_iniciado:
    st.markdown("<h1 class='titulo-juego'>🕵️ CLUPEDO 🕵️</h1>", unsafe_allow_html=True)
    st.markdown("### Generador de Partidas")
    st.write("Bienvenido, subnormal. Selecciona la dificultad para recibir tu caso.")

    col1, col2 = st.columns(2)
    with col1:
        dif = st.selectbox("Nivel de Dificultad", ["Fácil", "Intermedio", "Difícil", "Crimen Maestro"], index=1)
    
    st.write("") 
    
    if st.button("📁 GENERAR NUEVO CASO", type="primary"):
        mapa_dif = {"Fácil": "1", "Intermedio": "2", "Difícil": "3", "Crimen Maestro": "4"}
        
        with st.spinner('Recopilando pruebas y declaraciones...'):
            verdad, mazo, nombre_dif = construir_mazo(mapa_dif[dif])
            
            if verdad:
                st.session_state.verdad = verdad
                st.session_state.mazo = mazo
                st.session_state.dificultad = nombre_dif
                st.session_state.juego_iniciado = True
                st.session_state.cartas_reveladas = set() 
                st.rerun()
            else:
                st.error("Error al generar la partida. Revisa motor.py y cartas_final.json")

# =============================================================================
# PANTALLA 2: EL JUEGO
# =============================================================================
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header(f"Nivel: {st.session_state.dificultad}")
        st.write("Analiza las cartas y encuentra la verdad.")
        
        st.markdown("---")
        
        if st.button("👁️ Revelar TODAS las cartas"):
            for c in st.session_state.mazo:
                st.session_state.cartas_reveladas.add(c['id'])
            st.rerun()

        st.markdown("---")

        if st.button("❌ Rendirse / Reiniciar"):
            st.session_state.juego_iniciado = False
            st.rerun()

        st.title(f"Caso: {st.session_state.dificultad}")
        
        with st.expander("📜 REGLAS OFICIALES DE CLUPEDO"):
            st.markdown("""
            ### 🎯 EL OBJETIVO
            Debes deducir quién es el Asesino, qué Arma usó y cuál fue su Móvil. 
            En dificultades altas (Difícil y Crimen Maestro), el asesino cuenta con un **Cómplice**. Deberás descubrir también quién es y cuál es su móvil para ganar la partida.

            ### 🃏 PREPARACIÓN
            Una vez generada la partida en la web, buscad en la caja **solo las cartas que indica la lista** y barajadlas bien. 
            Repartid **6 cartas** a cada jugador. El resto de cartas forman el mazo central de robo (boca abajo).

            ### 🗣️ EL TURNO: LA REGLA DE LOS 3 ELEMENTOS
            Para equilibrar el juego, en tu turno puedes interrogar al resto de jugadores preguntando por **3 elementos**. 
            *Estrategia recomendada:* Nombra 1 Personaje, 1 Habitación y 1 Categoría Forense/Móvil (Ej: *"Pregunto por Blanca, la Terraza y armas Asfixiantes"*). 

            ### 🤝 EL INTERCAMBIO DE CARTAS
            1. Haces tu petición en voz alta.
            2. El resto de jugadores mira su mano. Si tienen cartas vinculadas a lo que has pedido, te hacen una oferta diciendo la **suma de los puntos** de esas cartas (el valor 1, 2 o 3 viene impreso en la carta). No están obligados a ofrecerte todo lo que tienen.
            3. Tú decides si aceptas la oferta de un jugador. Si lo haces, debes pagarle dándole cartas de tu propia mano que sumen **ese mismo valor o más**. El intercambio se hace en secreto.

            ### ♻️ FIN DE RONDA Y DESCARTE
            Una ronda termina cuando **todos** los jugadores de la mesa han tenido su turno para preguntar e intercambiar. En ese momento:
            1. Todos los jugadores revisan su mano y **se descartan en secreto** de las cartas que ya no quieran, hasta quedarse obligatoriamente con solo **3 cartas**. (Las cartas descartadas van a una pila de descarte común).
            2. Cada jugador roba nuevas cartas del mazo central hasta volver a tener **6 cartas** en la mano.
            3. Comienza una nueva ronda. *(Si el mazo central se agota, barajad la pila de descarte para formar uno nuevo).*

            ### 📋 LA LEY DE LA HOJA DE DEDUCCIÓN
            La hoja de deducción física es la ley absoluta para saber si debes enseñar una carta.
            Si alguien pregunta por "El Pedo", y tú tienes una carta que descarta la categoría general de "Asfixiantes", **debes contarla en tu oferta**, ya que ambos conceptos están unidos visualmente en la hoja. Lo mismo aplica a personajes y sus móviles.

            ### 🤥 MENTIRAS, CÁMARAS Y COARTADAS
            **El juego nunca miente, pero los criminales sí.**
            *   **Inocentes:** Sus cartas de coartada siempre dicen la verdad sobre dónde terminaron la noche.
            *   **El Equipo Criminal:** El Asesino y el Cómplice nunca confesarán estar en la escena del crimen. Si actuaron juntos, su coartada de unión afirmará que pasaron toda la noche juntos en la sala de donde robaron el arma. 
            *   **La trampa:** ¡Usa las cartas de Cámaras de Seguridad y Bloqueos de Paso! Si las cámaras graban a un criminal moviéndose por los pasillos, su coartada quedará desmontada.

            ### 🩸 LAS EVIDENCIAS Y EL "CABEZA DE TURCO"
            En las partidas más difíciles, aparecerán hasta 3 cartas de "Evidencia de Móvil". 
            ¡Cuidado! No todas son reales. Una pertenece al Asesino, otra al Cómplice, y otra es una pista falsa plantada por el motor del juego para incriminar a un inocente (el Cabeza de Turco). Deberás cruzar estas evidencias con los informes policiales de descarte para saber cuáles son verdaderas y cuál es una trampa.
            """)
    
    # --- CHULETA DE EXTRACCIÓN FÍSICA ---
    st.success("📦 **CARTAS FÍSICAS QUE DEBES SACAR DE LA CAJA (Orden numérico exacto):**")
    lista_ids = [str(c['id']) for c in st.session_state.mazo]
    st.write(", ".join(lista_ids))

    # --- FUNCIÓN DE RENDERIZADO CORREGIDA (SECCION) ---
    def render_cartas(lista_cartas, seccion_key):
        """
        Recibe una lista de cartas y una 'seccion_key' única (ej: 'tab_forense')
        para evitar duplicidad de keys en los botones.
        """
        if not lista_cartas:
            st.info("No hay pistas de este tipo.")
            return

        for c in lista_cartas:
            c_id = c['id']
            tipo_fmt = c['tipo'].upper().replace('_', ' ')
            
            container = st.container()
            
            # Si el ID está revelado, muestra texto
            if c_id in st.session_state.cartas_reveladas:
                container.markdown(f"""
                <div class="carta-visible">
                    <small style="color:#888;">ID {c_id:03} | {tipo_fmt}</small><br>
                    <strong>{c['texto']}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Si no, muestra reverso + botón con KEY ÚNICA
                col_txt, col_btn = container.columns([3, 1])
                with col_txt:
                    st.markdown(f"""
                    <div class="carta-oculta">
                        🔒 <strong>PISTA {c_id:03}</strong><br>
                        <small>{tipo_fmt}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    # AQUÍ ESTÁ EL CAMBIO: Añadimos seccion_key al key del botón
                    unique_key = f"btn_{c_id}_{seccion_key}"
                    if st.button("👁️ Ver", key=unique_key):
                        st.session_state.cartas_reveladas.add(c_id)
                        st.rerun()

    # --- PESTAÑAS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Mazo", "🧬 Forense", "📹 Cámaras", "📍 Lugares", "🗣️ Social"])

    c_forense = [c for c in st.session_state.mazo if c["tipo"] in ["descarte_arma", "informe_categoria", "sintoma_negativo", "sintoma_positivo", "evidencia_motivo"]]
    c_camaras = [c for c in st.session_state.mazo if "camara" in c["tipo"]]
    c_lugares = [c for c in st.session_state.mazo if c["tipo"] in ["lugar_limpio", "bloqueo_paso"]]
    c_social  = [c for c in st.session_state.mazo if c not in c_forense and c not in c_camaras and c not in c_lugares]

    # Pasamos un identificador único (string) a cada llamada
    with tab1:
        st.write(f"Total de Pistas: {len(st.session_state.mazo)}")
        render_cartas(st.session_state.mazo, "tab_mazo")
    with tab2:
        render_cartas(c_forense, "tab_forense")
    with tab3:
        render_cartas(c_camaras, "tab_camaras")
    with tab4:
        render_cartas(c_lugares, "tab_lugares")
    with tab5:
        render_cartas(c_social, "tab_social")

    st.markdown("---")
    
    # --- RESOLUCIÓN ---
    st.header("⚖️ RESOLUCIÓN FINAL")
    
    with st.container():
        st.info("Completa tu acusación. El sistema NO te dirá qué has fallado.")
        
        verdad = st.session_state.verdad
        tiene_complice = verdad.get('complice') is not None

        col_sus, col_arma, col_movil = st.columns(3)
        with col_sus:
            acusacion_asesino = st.selectbox("¿Quién es el Asesino?", ["Seleccionar..."] + SOSPECHOSOS)
        with col_arma:
            acusacion_arma = st.selectbox("¿Qué Arma usó?", ["Seleccionar..."] + LISTA_ARMAS)
        with col_movil:
            acusacion_movil = st.selectbox("¿Cuál fue el Móvil?", ["Seleccionar..."] + LISTA_MOTIVOS)

        # CAMPOS EXTRA SI HAY CÓMPLICE
        if tiene_complice:
            st.write("---")
            st.markdown("#### 👥 Identifica al Cómplice")
            col_comp, col_mov_comp = st.columns(2)
            with col_comp:
                acusacion_complice = st.selectbox("¿Quién es el Cómplice?", ["Seleccionar..."] + SOSPECHOSOS)
            with col_mov_comp:
                acusacion_movil_comp = st.selectbox("¿Cuál fue el Móvil del Cómplice?", ["Seleccionar..."] + LISTA_MOTIVOS)

        if st.button("🔨 DICTAR SENTENCIA", type="primary"):
            if "Seleccionar..." in [acusacion_asesino, acusacion_arma, acusacion_movil]:
                st.warning("Debes completar todos los campos del asesino.")
            elif tiene_complice and "Seleccionar..." in [acusacion_complice, acusacion_movil_comp]:
                st.warning("Debes completar todos los campos del cómplice.")
            else:
                acierto_base = (acusacion_asesino == verdad['culpable'] and 
                                acusacion_arma == verdad['arma'] and 
                                acusacion_movil == verdad['motivo'])
                
                acierto_complice = True
                if tiene_complice:
                    acierto_complice = (acusacion_complice == verdad['complice'] and 
                                        acusacion_movil_comp == verdad['motivo_complice'])
                
                if acierto_base and acierto_complice:
                    st.balloons()
                    st.success("## 🎉 ¡CORRECTO! CASO CERRADO")
                    st.write("Enhorabuena Richard Widmark.")
                else:
                    st.error("## 💀 INCORRECTO")
                    st.write("Tu teoría es una puta bazofia. Chúpame los huevos.")
    
    st.markdown("---")

    # --- SPOILER ---
    with st.expander("🔐 VER LA SOLUCIÓN (Rendirse)"):
        st.warning("¿Seguro? Eres maricón.")
        if st.checkbox("Sí, soy maricón."):
            v = st.session_state.verdad
            st.markdown(f"""
            - **Culpable:** {v['culpable']} (Móvil: {v['motivo']})
            - **Arma:** {v['arma']} ({v['origen_arma']})
            - **Cómplice:** {v['complice'] if v['complice'] else 'Ninguno'} (Móvil: {v.get('motivo_complice', 'Ninguno')})
            """)