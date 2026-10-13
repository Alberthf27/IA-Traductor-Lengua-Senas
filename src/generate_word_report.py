import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_second_report():
    doc = docx.Document()
    
    # Configurar márgenes estándar (2.54 cm / 1 pulgada)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Estilos de formato
    def set_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        return p

    def set_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
        return p

    def set_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x37, 0x41, 0x51)
        return p

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.name = 'Arial'
            r_b.font.size = Pt(11)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(11)
        r.italic = italic
        return p

    # --- PORTADA ---
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_uni.add_run("UNIVERSIDAD PRIVADA ANTENOR ORREGO\nFACULTAD DE INGENIERÍA\n")
    r.bold = True
    r.font.name = 'Arial'
    r.font.size = Pt(14)

    r_carr = p_uni.add_run("PROGRAMA DE ESTUDIOS DE INGENIERÍA DE SISTEMAS E INTELIGENCIA ARTIFICIAL\n\n")
    r_carr.bold = True
    r_carr.font.name = 'Arial'
    r_carr.font.size = Pt(12)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_tit.add_run("INFORME DE PROYECTO (SEGUNDO ENTREGABLE)\n")
    r_t.bold = True
    r_t.font.name = 'Arial'
    r_t.font.size = Pt(16)
    r_t.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    r_sub = p_tit.add_run("SISTEMA DE TRADUCCIÓN DE LENGUAJE DE SEÑAS (ASL) A TEXTO Y VOZ EN ESPAÑOL MEDIANTE VISIÓN COMPUTACIONAL Y APRENDIZAJE PROFUNDO\n\n\n")
    r_sub.bold = True
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(13)

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.line_spacing = 1.2
    p_meta.add_run("INTEGRANTES:\n").bold = True
    p_meta.add_run("• Aliaga Vásquez, Cristian\n• Flores Leonardo, Alberth Jair\n• Gutiérrez Gamboa, Fabrizzio\n• Lauriano Solano, Fabricio\n• Pita Verástegui, Anthony Eduardo\n• Santisteban Novoa, Julio Alejandro\n\n")
    p_meta.add_run("DOCENTE:\n").bold = True
    p_meta.add_run("Teobaldo Hernán Sagástegui Chigne\n\n")
    p_meta.add_run("CURSO:\n").bold = True
    p_meta.add_run("Inteligencia Artificial: Principios y Técnicas\n\n")
    
    p_lugar = doc.add_paragraph()
    p_lugar.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lugar.add_run("Trujillo, Perú\n2026")

    doc.add_page_break()

    # --- I. INTRODUCCIÓN ---
    set_heading_1("I. Introducción")

    set_heading_2("1.1 Título del Proyecto")
    add_p("Sistema Inteligente de Traducción en Tiempo Real de Lenguaje de Señas Americano (ASL) a Texto y Voz en Idioma Español Basado en Redes Neuronales Profundas Secuenciales y MediaPipe.")

    set_heading_2("1.2 Antecedentes")
    add_p("En el ámbito asistivo e investigativo, el reconocimiento automático de la lengua de señas ha sido abordado mediante diversas metodologías:")
    add_p("Implementaron un entorno multimedia asistivo para el aprendizaje de señas con retroalimentación acústica y táctil, demostrando una mejora de 32 % en la retención inicial, aunque carecía de traducción continua en tiempo real.", bold_prefix="• Hernández, Pulido y Arias (2015): ")
    add_p("Desarrolló un sistema basado en tecnología wearable mediante guantes instrumentados con flexómetros y unidades de medición inercial (IMU). Si bien alcanzó exactitudes elevadas, evidenció severas limitaciones operativas en costo, calibración constante y fatiga para el usuario.", bold_prefix="• Marin (2025): ")
    add_p("Validaron el empleo de visión artificial con cámaras estándar como una solución accesible de bajo coste, eliminando la necesidad de dispositivos portátiles invasivos.", bold_prefix="• Quinta Lipe y Guerrero (2025): ")
    add_p("Analizaron modelos de aprendizaje profundo para traducción bidireccional, concluyendo que las redes secuenciales con memoria resultan imperativas para evitar confusiones en gestos con trayectorias semejantes.", bold_prefix="• Alvarado Cadena (2025); Carvajal y Gómez (2026): ")
    add_p("Publicó el repositorio de acceso libre ASL Improved Recognition en Hugging Face, logrando una precisión de validación de 64.61 % sobre 77 clases mediante la combinación de MediaPipe, convoluciones 1D y redes Bi-LSTM con atención.", bold_prefix="• Namratha (2025): ")

    set_heading_2("1.3 Problema a Resolver")
    add_p("En el Perú y a nivel global, las personas con discapacidad auditiva y dificultades del habla afrontan marcadas barreras de integración en servicios de salud, educación, trámites civiles y empleo, puesto que la gran mayoría de la población oyente desconoce la lengua de señas. Además, las soluciones comerciales existentes se limitan mayoritariamente al idioma inglés, son cerradas o exigen periféricos costosos. Se requiere un traductor visual y acústico que interprete la seña y pronuncie la locución correspondiente en español de manera automática y con mínima latencia.", bold_prefix="Descripción de la problemática: ")

    add_p("¿En qué medida el desarrollo de un sistema basado en visión computacional y modelos de aprendizaje profundo secuenciales permite traducir eficazmente secuencias de señas de ASL a texto y voz sintetizada en español en tiempo real con una latencia inferior a 2 segundos?", bold_prefix="Problema General: ")

    add_p("1. ¿Cómo estructurar y normalizar las secuencias temporales de puntos clave (landmarks) de ambas manos a partir del flujo de video mediante MediaPipe para alimentar la red neuronal?\n2. ¿Cómo clasificar con robustez las 77 categorías de señas mediante una red profunda híbrida (CNN 1D + Bi-LSTM + Atención)?\n3. ¿Cómo articular un módulo de mapeo semántico inglés-español y un motor de síntesis de voz (TTS) para ofrecer una experiencia accesible al usuario?", bold_prefix="Problemas Específicos: ")

    set_heading_2("1.4 Objetivos")
    add_p("Desarrollar e implementar un sistema de inteligencia artificial en tiempo real que traduzca el lenguaje de señas a texto y audio en español mediante visión artificial con MediaPipe, redes neuronales profundas y síntesis de voz, desplegado en una interfaz accesible.", bold_prefix="Objetivo General: ")

    add_p("1. Extraer y preprocesar las secuencias de coordenadas esqueléticas de ambas manos (126 características por frame) a partir de video en vivo empleando MediaPipe.\n2. Integrar e inferir sobre la arquitectura de aprendizaje profundo ImprovedASLModel (CNN 1D + Bi-LSTM + Atención) entrenada sobre 77 clases de ASL.\n3. Construir el módulo de traducción léxica al español y conectar un motor de síntesis Text-to-Speech (TTS) de baja latencia.\n4. Diseñar e implementar una interfaz funcional en Streamlit y aplicación de escritorio que capture video, exponga las predicciones y reproduzca la voz traducida.", bold_prefix="Objetivos Específicos: ")

    # --- II. REQUERIMIENTOS ---
    set_heading_1("II. Requerimientos")

    set_heading_2("2.1 Definición del Dominio")
    add_p("El dominio de aplicación corresponde a la interacción humano-computador asistiva y el reconocimiento de patrones espacio-temporales en video. A diferencia del análisis de imágenes estáticas de dígitos o alimentos, una seña manual dinámica no puede ser descrita por un único fotograma: requiere modelar la postura de los dedos, la rotación de la muñeca y la cinemática de la trayectoria a lo largo de una ventana temporal.\n\nPara viabilizar el procesamiento en tiempo real sobre hardware convencional, el dominio no trabaja con matrices directas de píxeles RGB (las cuales exigirían un coste de cálculo y memoria prohibitivo), sino que se proyecta al espacio geométrico articular: cada mano se reduce a 21 puntos anatómicos tridimensionales (x, y, z). Por lo tanto, el dominio opera sobre series temporales multivariadas de 126 dimensiones por instante de tiempo.")

    set_heading_2("2.2 Determinación de Requisitos (Requerimientos)")
    
    add_p("Requisitos Funcionales del Sistema (RF):", bold_prefix="• ")
    table_rf = doc.add_table(rows=1, cols=3)
    table_rf.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table_rf.rows[0].cells
    hdr[0].text = "Código"
    hdr[1].text = "Requisito Funcional"
    hdr[2].text = "Descripción"
    
    rf_data = [
        ("RF-01", "Captura de video en vivo", "Capturar el flujo de fotogramas desde la cámara web a un régimen de 25-30 FPS."),
        ("RF-02", "Detección y extracción de landmarks", "Identificar manos y extraer las coordenadas tridimensionales de 21 articulaciones por mano mediante MediaPipe."),
        ("RF-03", "Normalización y relleno temporal", "Centrar las coordenadas respecto a la articulación de la muñeca y asegurar un tamaño uniforme de secuencia (30 fotogramas)."),
        ("RF-04", "Clasificación neuronal profunda", "Ejecutar la inferencia del modelo PyTorch para predecir la seña con mayor probabilidad entre las 77 clases."),
        ("RF-05", "Traducción de idioma (Inglés a Español)", "Convertir la etiqueta de clase de ASL a su equivalente semántico en español."),
        ("RF-06", "Síntesis de voz (Text-to-Speech)", "Generar la locución de audio en español correspondiente al término predicho utilizando síntesis TTS."),
        ("RF-07", "Interfaz gráfica interactiva", "Desplegar el video con el esqueleto superpuesto, métricas de confianza, historial y controles interactivos en Streamlit.")
    ]
    for c, r_name, desc in rf_data:
        row = table_rf.add_row().cells
        row[0].text = c
        row[1].text = r_name
        row[2].text = desc

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_p("Requisitos No Funcionales del Sistema (RNF):", bold_prefix="• ")
    table_rnf = doc.add_table(rows=1, cols=3)
    table_rnf.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr2 = table_rnf.rows[0].cells
    hdr2[0].text = "Código"
    hdr2[1].text = "Requisito No Funcional"
    hdr2[2].text = "Descripción"
    
    rnf_data = [
        ("RNF-01", "Latencia en tiempo real", "El tiempo total desde la culminación del gesto hasta la locución de audio debe ser menor a 1.5 segundos."),
        ("RNF-02", "Compatibilidad de hardware", "El sistema debe operar de forma óptima en computadoras portátiles o de escritorio estándar sin requerir aceleradores GPU industriales."),
        ("RNF-03", "Usabilidad y accesibilidad", "La aplicación debe ser intuitiva, con activación sencilla de la cámara web y visualización clara para el usuario."),
        ("RNF-04", "Privacidad y procesamiento local", "El procesamiento de imágenes y la inferencia se ejecutan localmente en el equipo sin enviar transmisiones de video a servidores externos.")
    ]
    for c, r_name, desc in rnf_data:
        row = table_rnf.add_row().cells
        row[0].text = c
        row[1].text = r_name
        row[2].text = desc

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --- III. PLANTEAMIENTO DEL DATA-SET ---
    set_heading_1("III. Planteamiento del Data-Set, Pre-Procesamiento y Normalización")

    set_heading_2("3.1 Medidas, Datos, Bases de Datos, Elaboración del Data-Set y Características (Features)")
    add_p("El proyecto se enmarca en la modalidad de Aprendizaje Supervisado de Deep Learning (Aprendizaje Profundo). Se basa en el conjunto de datos estandarizado de American Sign Language (ASL) documentado en el repositorio namratha2412/asl-improved-recognition de Hugging Face.")
    add_p("El dataset comprende 77 clases etiquetadas compuestas por:\n• 26 letras del alfabeto dactilológico (A a la Z).\n• 51 palabras y expresiones esenciales de la vida diaria (saludos, acciones, preguntas, términos de educación y familia).\n\nCada muestra se estructura como una serie de tiempo donde cada fotograma contiene las coordenadas normalizadas de ambas manos (mano izquierda y mano derecha). Con 21 puntos por mano y 3 coordenadas espaciales (x, y, z), el vector característico por fotograma se calcula como:")
    add_p("Features por fotograma = 2 manos × 21 landmarks × 3 coordenadas = 126 variables continuas.", italic=True)

    set_heading_2("3.2 Normalización y/o Filtrado de Datos")
    add_p("Para asegurar la consistencia numérica requerida por las capas convolucionales y recurrentes de la red, se implementó el siguiente preprocesamiento:")
    add_p("Las coordenadas absolutas en píxeles varían según la distancia del usuario y el encuadre de la cámara. Por ello, se realiza una traslación local restando las coordenadas del punto de referencia de la muñeca (landmark 0). Esto confiere invarianza traslacional a la postura de la mano.", bold_prefix="1. Invarianza espacial (Normalización de coordenadas): ")
    add_p("Dado que los usuarios ejecutan señas a diferentes velocidades, se estandariza la dimensión temporal a una longitud fija de 30 fotogramas. Si la secuencia capturada es más corta, se aplica relleno con ceros (zero-padding); si es más prolongada, se realiza un truncamiento o muestreo regular.", bold_prefix="2. Padding y Truncamiento temporal: ")
    add_p("En gestos que involucran únicamente una mano, las 63 coordenadas de la mano inactiva se completan con ceros, manteniendo la forma matricial de entrada uniforme (batch_size, 30, 126).", bold_prefix="3. Tratamiento de extremidad ausente: ")
    add_p("Durante la fase de entrenamiento original se aplicó data augmentation mediante inyección de ruido gaussiano aleatorio (σ = 0.02) y técnicas de regularización con Dropout (0.3) para prevenir el sobreajuste.", bold_prefix="4. Aumento de datos y reducción de ruido: ")

    set_heading_2("3.3 Planteamiento del Data-Set (Entrenamiento, Validación y Pruebas)")
    add_p("La organización del conjunto de datos para el entrenamiento y evaluación de la arquitectura se diseñó siguiendo el protocolo riguroso de aprendizaje automático supervisado:")
    add_p("Corresponde al 80 % del volumen total de datos. Este conjunto fue utilizado para optimizar los 3 258 574 parámetros entrenables del modelo mediante el optimizador AdamW con planificador de tasa de aprendizaje OneCycleLR y función de pérdida Cross-Entropy con ponderación de clases para compensar desbalances.", bold_prefix="• Data-Set de Entrenamiento (Training): ")
    add_p("Representa el 20 % restante del conjunto, particionado mediante división estratificada (Stratified Split) para conservar idéntica proporción de las 77 categorías. Este conjunto supervisó el rendimiento tras cada época de entrenamiento, permitiendo aplicar parada temprana (Early Stopping con paciencia de 15 épocas) y logrando el mejor punto de convergencia en la época 27 con 64.61 % de exactitud.", bold_prefix="• Set de Validación y Validación Cruzada (Validation / Cross-Validation): ")
    add_p("Para la validación de la solución integrada se diseñó un protocolo de evaluación funcional en tiempo real donde usuarios reales ejecutan secuencias de señas frente a la cámara web. Se evalúa la exactitud de predicción Top-1, el tiempo de inferencia del pipeline y la inteligibilidad de la síntesis de audio.", bold_prefix="• Data-Set de Pruebas (Test): ")

    # --- IV. APRENDIZAJE ---
    set_heading_1("IV. Aprendizaje")

    set_heading_2("4.1 Planteamiento del Modelo de Aprendizaje")
    add_p("El modelo desarrollado implementa un esquema de Deep Learning Híbrido concebido específicamente para series temporales de coordenadas cinemáticas. La arquitectura ImprovedASLModel se estructura en cuatro bloques sinérgicos:")
    
    add_p("Transforma el vector de 126 dimensiones mediante dos etapas de convolución con normalización por lotes (BatchNorm) y activación ReLU:\n  - Conv1d(126 → 128, kernel=3, padding=1) + BatchNorm1d + ReLU + Dropout(0.3)\n  - Conv1d(128 → 256, kernel=3, padding=1) + BatchNorm1d + ReLU + Dropout(0.3)\nEste bloque extrae las relaciones geométricas locales y la configuración espacial instantánea entre articulaciones contiguas.", bold_prefix="1. Bloque Convolucional 1D (CNN 1D): ")

    add_p("Configurada con 2 capas bidireccionales y 256 unidades ocultas por sentido (vector resultante de dimensión 512). Modela la evolución cronológica del movimiento, capturando las transiciones y dependencias tanto del pasado hacia el futuro como en sentido inverso a lo largo de los 30 fotogramas.", bold_prefix="2. Bloque Recurrente Bidireccional (Bi-LSTM): ")

    add_p("Calcula dinámicamente coeficientes de atención sobre cada fotograma de la secuencia. Esto permite a la red ponderar con mayor peso los instantes en los que el gesto alcanza su punto morfológico cúspide, descartando fotogramas transitorios o neutros.", bold_prefix="3. Mecanismo de Atención (Attention Mechanism): ")

    add_p("Proyecta el vector de contexto enriquecido de 512 variables hacia el espacio de clasificación final:\n  - Linear(512 → 512) + BatchNorm1d + ReLU + Dropout(0.3)\n  - Linear(512 → 256) + BatchNorm1d + ReLU + Dropout(0.3)\n  - Linear(256 → 77 clases)\nTotal de parámetros entrenables: 3,258,574 parámetros.", bold_prefix="4. Perceptrón Multicapa de Clasificación (MLP): ")

    set_heading_2("4.2 Desarrollo e Implementación del Modelo")
    add_p("El sistema fue programado íntegramente en Python 3.11 sobre una arquitectura de software modular y desacoplada:")
    add_p("Descarga automáticamente desde el repositorio de Hugging Face los pesos preentrenados (best_model.pth), el codificador de clases (label_encoder_classes.npy) y el archivo de configuración.", bold_prefix="• Módulo de Gestión de Modelos (src/download_model.py): ")
    add_p("Implementa la clase PyTorch ImprovedASLModel reproduciendo fielmente la arquitectura neuronal para la carga de tensores y ejecución de inferencia en CPU o CUDA.", bold_prefix="• Módulo de Red Neuronal (src/model.py): ")
    add_p("Gestiona el flujo de MediaPipe Hands, aplicando la extracción de los 21 puntos clave por mano, normalización centrada en muñeca y generación del esqueleto gráfico en pantalla.", bold_prefix="• Módulo de Visión Artificial (src/landmark_extractor.py): ")
    add_p("Traduce instantáneamente las 77 clases predichas en inglés a términos semánticos en español (incluyendo vocabulario y abecedario).", bold_prefix="• Módulo de Traducción (src/translator.py): ")
    add_p("Sintetiza la palabra traducida a audio natural en español empleando pyttsx3 para locución local sin latencia de red y gTTS para generación de flujo de audio reproducible.", bold_prefix="• Módulo de Voz Text-to-Speech (src/tts_engine.py): ")
    add_p("Orquesta la cola circular temporal de fotogramas (buffer de tamaño 30), invoca la inferencia del modelo y filtra las predicciones por umbral de certeza para evitar falsos positivos.", bold_prefix="• Módulo Orquestador (src/recognizer.py): ")
    add_p("Proporciona una interfaz web reactiva completa desarrollada en Streamlit (app.py) que permite al usuario encender la cámara, visualizar los landmarks en vivo, consultar el término en español con su porcentaje de certeza, revisar el historial de conversación y escuchar la pronunciación en audio. Adicionalmente, se incluye una versión de escritorio ultraligera (app_desktop.py) y un lanzador por lotes (ejecutar.bat).", bold_prefix="• Interfaz de Usuario y Despliegue (Streamlit y OpenCV): ")

    # Guardar documento
    output_filename = "INFORME_PROYECTO_IA_SEGUNDO_ENTREGABLE.docx"
    doc.save(output_filename)
    print(f"Documento guardado exitosamente como: {output_filename}")

if __name__ == "__main__":
    create_second_report()
