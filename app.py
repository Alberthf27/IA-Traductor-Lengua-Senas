import streamlit as st
import cv2
import numpy as np
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recognizer import ASLRecognizer
from src.tts_engine import TextToSpeechManager
from src.translator import ASL_TO_SPANISH
from src.sentence_builder import MorphosyntacticSentenceAssembler

st.set_page_config(
    page_title="Traductor de Lengua de Señas a Voz",
    page_icon="🤟",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .sentence-box {
        background-color: #EFF6FF;
        border-radius: 12px;
        padding: 16px 20px;
        border: 2px solid #3B82F6;
        margin-bottom: 15px;
    }
    .sentence-text {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .pred-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 6px solid #10B981;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .word-active {
        font-size: 2.2rem;
        font-weight: 800;
        color: #047857;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤟 Traductor de Lenguaje de Señas a Voz y Frases</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Reconocimiento de Letras, Palabras y Construcción de Oraciones en Tiempo Real</div>', unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    confidence_thresh = st.slider("Umbral de confianza mínima:", min_value=0.20, max_value=0.85, value=0.35, step=0.05)
    auto_voice = st.checkbox("Reproducir voz al detectar palabra/letra", value=True)
    voice_cooldown = st.slider("Pausa entre repeticiones de voz (segundos):", 1.0, 4.0, 2.0, 0.5)

    st.divider()
    st.header("📖 Guía Rápida de Señas")
    tab_palabras, tab_letras = st.tabs(["🗣️ Palabras Clave", "🔤 Abecedario"])
    
    with tab_palabras:
        st.markdown("""
        - **Hola:** Mano abierta saludando al costado de la sien.
        - **Gracias:** Mano plana saliendo de la barbilla hacia adelante.
        - **Por favor:** Mano plana frotando en círculo sobre el pecho.
        - **Agua:** Letra W (3 dedos) tocando los labios.
        - **Comer:** Yemas de los dedos juntas hacia la boca.
        - **Beber:** Mano en 'C' (vaso) inclinada hacia la boca.
        - **Ayuda:** Puño sobre la palma de la mano base subiendo.
        - **Sí:** Puño cerrado asintiendo arriba y abajo.
        - **No:** Índice y medio cerrándose contra el pulgar.
        - **Te quiero:** Pulgar, índice y meñique estirados (gesto ILY).
        """)
        
    with tab_letras:
        st.markdown("""
        - **L:** Pulgar e índice en 90°.
        - **V:** Signo de la paz (índice y medio en V).
        - **W:** 3 dedos arriba (índice, medio, anular).
        - **Y:** Gesto surfer (pulgar y meñique afuera).
        - **I:** Solo dedo meñique hacia arriba.
        - **D:** Solo índice hacia arriba señalando.
        - **B:** 4 dedos juntos hacia arriba.
        - **F:** Pulgar e índice tocándose (signo 'OK').
        - **C:** Mano curva como sosteniendo una taza.
        - **A:** Puño cerrado con pulgar al costado.
        """)
        
    st.divider()
    st.header("⚡ Telemetría de Rendimiento")
    col_t1, col_t2 = st.columns(2)
    metric_fps = col_t1.empty()
    metric_lat = col_t2.empty()

@st.cache_resource
def load_recognizer():
    try:
        return ASLRecognizer(confidence_threshold=0.35)
    except Exception as e:
        st.error(f"❌ Error al inicializar el reconocedor: {e}")
        st.info("💡 En Streamlit Cloud, asegúrate de que la versión de Python sea 3.11 en App Settings (⋮ -> Settings -> Python version -> 3.11).")
        raise e

@st.cache_resource
def load_tts():
    return TextToSpeechManager()

recognizer = load_recognizer()
tts = load_tts()
sentence_assembler = MorphosyntacticSentenceAssembler()
recognizer.confidence_threshold = confidence_thresh

# Historial y Frase en Sesión
if "sentence" not in st.session_state:
    st.session_state.sentence = []

col_cam, col_info = st.columns([3, 2])

with col_info:
    st.markdown("### 💬 Oración Natural Ensamblada")
    sentence_placeholder = st.empty()
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("🔊 Leer Frase"):
            if st.session_state.sentence:
                frase_completa = sentence_assembler.assemble(st.session_state.sentence)
                tts.speak_async(frase_completa)
    with col_btn2:
        if st.button("⬅️ Borrar última"):
            if st.session_state.sentence:
                st.session_state.sentence.pop()
                st.rerun()
    with col_btn3:
        if st.button("🗑️ Limpiar frase"):
            st.session_state.sentence = []
            st.rerun()

    st.markdown("### 🎯 Seña Actual en Pantalla")
    current_word_placeholder = st.empty()
    metric_placeholder = st.empty()

with col_cam:
    st.markdown("### 📷 Cámara en Vivo")
    run_camera = st.toggle("Activar Cámara Web", value=False)
    frame_placeholder = st.empty()

if run_camera:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        st.error("No se pudo acceder a la cámara web. Verifica que no esté en uso por otra app.")
    else:
        last_spoken = ""
        last_time = 0
        last_added_time = 0
        
        while run_camera:
            t_frame_start = time.time()
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            ann_frame, pred_info = recognizer.process_frame(frame)
            
            frame_rgb = cv2.cvtColor(ann_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            curr_t = time.time()
            frame_time_ms = max((curr_t - t_frame_start) * 1000, 1.0)
            fps_val = 1000.0 / frame_time_ms
            metric_fps.metric("FPS", f"{fps_val:.0f}")
            metric_lat.metric("Latencia", f"{frame_time_ms:.0f} ms")
            if pred_info["spanish_label"]:
                es_word = pred_info["spanish_label"]
                conf = pred_info["confidence"]
                
                current_word_placeholder.markdown(f"""
                <div class="pred-card">
                    <div class="word-active">{es_word}</div>
                    <div>Confianza estimada: <b>{conf*100:.1f}%</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                metric_placeholder.progress(min(int(conf * 100), 100), text=f"Certeza: {conf*100:.1f}%")
                
                # Disparo fluido: Agregar a la frase si se detecta el ápice cinemático o cambió la seña
                is_apex = pred_info.get("is_apex", False)
                should_add = (is_apex and es_word != last_spoken) or (es_word != last_spoken and (curr_t - last_added_time > 1.2)) or (curr_t - last_added_time > 3.0)
                
                if should_add:
                    st.session_state.sentence.append(es_word)
                    last_added_time = curr_t
                    
                    if auto_voice and ((es_word != last_spoken) or (curr_t - last_time > voice_cooldown)):
                        tts.speak_async(es_word)
                        last_spoken = es_word
                        last_time = curr_t
            else:
                if pred_info["hands_detected"]:
                    current_word_placeholder.info(f"🖐️ Mano detectada. Realiza la seña...")
                else:
                    current_word_placeholder.warning("⚠️ Coloca tus manos frente a la cámara.")
                metric_placeholder.progress(int(pred_info["buffer_fill"] * 100), text="Seguimiento de manos...")

            # Mostrar la frase acumulada naturalmente
            frase_mostrar = sentence_assembler.assemble(st.session_state.sentence)
            sentence_placeholder.markdown(f"""
            <div class="sentence-box">
                <div class="sentence-text">{frase_mostrar if frase_mostrar else "<i>(Haz señas para formar tu frase...)</i>"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        cap.release()
else:
    frame_placeholder.info("Activa el interruptor 'Activar Cámara Web' para iniciar la detección.")
    frase_mostrar = sentence_assembler.assemble(st.session_state.sentence)
    sentence_placeholder.markdown(f"""
    <div class="sentence-box">
        <div class="sentence-text">{frase_mostrar if frase_mostrar else "<i>(Cámara apagada)</i>"}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# DICCIONARIO INTERACTIVO DE SEÑAS Y FRASES (PARA PRINCIPIANTES)
# ==============================================================================
st.divider()
st.markdown("## 📚 Diccionario y Explorador Interactivo de Señas")
st.markdown("Aprende la colocación anatómica de tus manos y cómo combinarlas para armar frases completas.")

dic_tab1, dic_tab2, dic_tab3, dic_tab4 = st.tabs([
    "🗣️ Saludos y Cortesía",
    "💧 Necesidades y Acciones",
    "💬 Respuestas y Emociones",
    "🔤 Abecedario Dactilológico (A-Z)"
])

with dic_tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.expander("👋 **Hola** *(Hello)*", expanded=True):
            st.markdown("""
            * **Posición:** Mano abierta plana con los 5 dedos extendidos.
            * **Altura:** Al costado de tu sien/ojo (arriba de la nariz).
            * **Movimiento:** Saludo militar hacia afuera o suave vaivén.
            * **Ejemplo de frase:** *Hola* + *Amigo* ➔ *"¡Hola, amigo!"*
            """)
    with c2:
        with st.expander("🙏 **Gracias** *(Thank You)*", expanded=True):
            st.markdown("""
            * **Posición:** Mano plana con dedos juntos.
            * **Altura:** Tocando la barbilla / labios inferiores.
            * **Movimiento:** Sale de la barbilla hacia adelante hacia la cámara.
            * **Ejemplo de frase:** *Sí* + *Gracias* ➔ *"Sí, muchas gracias."*
            """)
    with c3:
        with st.expander("🤲 **Por favor** *(Please)*", expanded=True):
            st.markdown("""
            * **Posición:** Mano plana sobre el pecho.
            * **Altura:** En el centro del torso.
            * **Movimiento:** Frotar en círculos suaves sobre el pecho.
            * **Ejemplo de frase:** *Agua* + *Por favor* ➔ *"Un vaso de agua, por favor."*
            """)

    c4, c5, c6 = st.columns(3)
    with c4:
        with st.expander("👋 **Adiós** *(Goodbye)*"):
            st.markdown("""
            * **Posición:** Mano abierta levantada saludando de lado a lado.
            * **Altura:** A la altura de la cara o hombro.
            * **Ejemplo de frase:** *"¡Hasta luego!"*
            """)
    with c5:
        with st.expander("🤝 **Amigo** *(Friend)*"):
            st.markdown("""
            * **Posición:** Dedos índices de ambas manos enganchados en gancho.
            * **Altura:** Al centro del pecho.
            * **Ejemplo de frase:** *Hola* + *Amigo* ➔ *"¡Hola, amigo!"*
            """)
    with c6:
        with st.expander("🙇 **Disculpa** *(Sorry)*"):
            st.markdown("""
            * **Posición:** Puño cerrado en 'A' frotando en círculos sobre el pecho.
            * **Altura:** En el pecho.
            * **Ejemplo de frase:** *"Disculpa la molestia."*
            """)

with dic_tab2:
    n1, n2, n3 = st.columns(3)
    with n1:
        with st.expander("💧 **Agua** *(Water)*", expanded=True):
            st.markdown("""
            * **Posición:** Letra 'W' (índice, medio y anular estirados).
            * **Altura:** Tocando el labio inferior o barbilla con el índice.
            * **Movimiento:** Dos toques suaves en los labios.
            * **Ejemplo:** *Por favor* + *Agua* ➔ *"Por favor, ¿me das un vaso de agua?"*
            """)
    with n2:
        with st.expander("🍎 **Comer** *(Eat)*", expanded=True):
            st.markdown("""
            * **Posición:** Yemas de los 5 dedos juntas (como sosteniendo comida).
            * **Altura:** Tocando la boca repetidamente.
            * **Movimiento:** Acercar las yemas a la boca 2 veces.
            * **Ejemplo:** *Comer* + *Por favor* ➔ *"Tengo hambre, por favor."*
            """)
    with n3:
        with st.expander("🥤 **Beber** *(Drink)*", expanded=True):
            st.markdown("""
            * **Posición:** Mano en forma de 'C' (como sosteniendo un vaso).
            * **Altura:** Inclinada hacia la boca como tomando agua.
            * **Ejemplo:** *"Tengo sed, por favor."*
            """)

    n4, n5, n6 = st.columns(3)
    with n4:
        with st.expander("🆘 **Ayuda** *(Help)*", expanded=True):
            st.markdown("""
            * **Posición:** Dos manos. Una mano base plana con palma hacia arriba.
            * **Acción:** Un puño cerrado sobre la palma base que se levanta junto.
            * **Ejemplo:** *Por favor* + *Ayuda* ➔ *"¡Por favor, necesito ayuda!"*
            """)
    with n5:
        with st.expander("🚶 **Ir** *(Go)*"):
            st.markdown("""
            * **Posición:** Dedos índices apuntando y girando hacia el frente.
            * **Ejemplo:** *Ir* + *Casa* ➔ *"Quiero ir a casa."*
            """)
    with n6:
        with st.expander("💼 **Trabajar** *(Work)*"):
            st.markdown("""
            * **Posición:** Dos puños cerrados, uno golpeando suavemente sobre la muñeca del otro.
            * **Ejemplo:** *"Voy a trabajar."*
            """)

with dic_tab3:
    r1, r2, r3 = st.columns(3)
    with r1:
        with st.expander("✅ **Sí** *(Yes)*", expanded=True):
            st.markdown("""
            * **Posición:** Puño cerrado en forma de 'S'.
            * **Movimiento:** Asentir con la muñeca hacia arriba y abajo (como una cabeza diciendo sí).
            * **Ejemplo:** *Sí* + *Gracias* ➔ *"Sí, muchas gracias."*
            """)
    with r2:
        with st.expander("❌ **No** *(No)*", expanded=True):
            st.markdown("""
            * **Posición:** Dedos índice y medio extendidos juntos.
            * **Movimiento:** Ciérralos tocando la yema del pulgar (como un pico de pato cerrándose).
            * **Ejemplo:** *No* + *Gracias* ➔ *"No, muchas gracias."*
            """)
    with r3:
        with st.expander("🤟 **Te Quiero** *(I Love You)*", expanded=True):
            st.markdown("""
            * **Posición:** Pulgar, índice y meñique estirados (gesto ILY).
            * **Dedos cerrados:** Dedo medio y anular doblados contra la palma.
            * **Ejemplo:** *"Te quiero mucho."*
            """)

with dic_tab4:
    st.markdown("### 🔤 Guía Anatómica del Abecedario Dactilológico")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown("""
        * **A:** Puño cerrado, pulgar apoyado al costado del índice.
        * **B:** 4 dedos juntos hacia arriba, pulgar doblado en la palma.
        * **C:** Mano curva como sosteniendo una taza.
        * **D:** Solo dedo índice apuntando al techo, otros en círculo con pulgar.
        * **E:** 4 dedos doblados sobre el pulgar recogido.
        * **F:** Signo 'OK' (pulgar e índice formando círculo, otros 3 abiertos).
        """)
    with a2:
        st.markdown("""
        * **G:** Índice y pulgar paralelos apuntando hacia el costado.
        * **H:** Índice y medio juntos apuntando hacia el costado.
        * **I:** Solo dedo meñique levantado hacia arriba.
        * **J:** Dedo meñique trazando una curva de anzuelo en el aire.
        * **K:** Índice arriba, medio hacia el frente, pulgar entre ambos.
        * **L:** Pulgar e índice formando una 'L' de 90° (pistola arriba).
        """)
    with a3:
        st.markdown("""
        * **M:** Pulgar debajo de los primeros 3 dedos doblados.
        * **N:** Pulgar debajo de los primeros 2 dedos doblados.
        * **O:** Todos los dedos tocando la punta del pulgar formando una O.
        * **P:** Como la letra 'K' pero apuntando hacia el suelo.
        * **Q:** Como la letra 'G' pero apuntando hacia el suelo.
        * **R:** Dedo medio cruzado sobre el dedo índice.
        """)
    with a4:
        st.markdown("""
        * **S:** Puño cerrado con pulgar cruzado por encima de los dedos.
        * **T:** Pulgar metido entre el dedo índice y el medio.
        * **U:** Índice y medio levantados juntos y pegados.
        * **V:** Símbolo de la paz (índice y medio separados en V).
        * **W:** 3 dedos arriba (índice, medio y anular en W).
        * **Y:** Gesto surfer (pulgar y meñique afuera, otros 3 cerrados).
        """)

