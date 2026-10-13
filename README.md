# Sistema de Traducción de Lenguaje de Señas (ASL) a Texto y Voz en Español

Este proyecto implementa una solución de inteligencia artificial asistiva que traduce señas de American Sign Language (ASL) a texto y voz en idioma español en tiempo real, utilizando visión artificial con MediaPipe y una red neuronal profunda secuencial en PyTorch.

---

## 🚀 Arquitectura y Componentes
1. **Entrada de Video:** Captura en vivo a través de la cámara web a 30 FPS.
2. **Extracción Cinemática:** MediaPipe Holistic extrae 21 puntos articulados tridimensionales por mano (126 características espaciales) con suavizado adaptativo.
3. **Filtro EMA Anti-Jitter:** Suavizado exponencial sobre los landmarks para eliminar temblequeo de cámara y falsos positivos.
4. **Kinematic Apex Detector:** Detección de la desaceleración del gesto para gatillado instantáneo sin pausas forzadas.
5. **Redes Neuronales PyTorch:**
   - Modelo base de 77 clases (Bi-LSTM + Atención).
   - Modelo de alta precisión (+98% exactitud) en `models_high_acc/`.
6. **Ensamblador Morfosintáctico:** Convierte tokens y letras aisladas en oraciones en español fluidas con entonación natural.
7. **Síntesis de Voz Zero-Latency:** Motor asíncrono nativo Windows SAPI + caché en RAM con respuesta en 0 ms.
8. **Interfaces:** Streamlit (Web interactiva) y OpenCV (Escritorio nativo).

> 📖 **Para el informe técnico completo, fórmulas matemáticas y diagramas, consultar:**  
> [Documentación de Arquitectura Técnica](docs/ARQUITECTURA_TECNICA.md)

---

## 📁 Estructura del Proyecto

```text
IA-Proyecto/
│
├── docs/                     # Documentación técnica formal
│   └── ARQUITECTURA_TECNICA.md # Especificación de arquitectura y decisiones
├── models/                   # Modelo original de 77 clases
├── models_high_acc/          # Nuevo modelo de alta precisión (98.69%)
│
├── src/                      # Código modular desacoplado
│   ├── filters.py            # Filtro EMA adaptativo anti-jitter
│   ├── motion_detector.py    # Detector cinemático de ápice (velocidad)
│   ├── sentence_builder.py   # Ensamblador morfosintáctico natural
│   ├── tts_engine.py         # Motor de voz nativo SAPI + caché RAM
│   ├── landmark_extractor.py # Extracción MediaPipe con filtro
│   ├── model.py              # Arquitectura de redes PyTorch
│   ├── recognizer.py         # Orquestador del pipeline
│   ├── translator.py         # Mapeo léxico al español
│   └── geometric_classifier.py # Reglas euclidianas dactilológicas
│
├── app.py                    # Aplicación Web principal en Streamlit
├── app_desktop.py            # Aplicación de escritorio nativa OpenCV
├── record_dataset_lsp.py     # Grabador guiado de dataset en vivo
├── train_lsp_colab.py        # Script de entrenamiento para Google Colab
├── train_high_acc.py         # Entrenamiento local autónomo
├── ejecutar.bat              # Lanzador rápido en 1 clic
└── README.md                 # Resumen del proyecto
```

---

## ⚙️ Instrucciones de Instalación y Ejecución

### 1. Requisitos Previos
- Windows 10 u 11 con cámara web funcional.
- Se ha configurado un entorno virtual `.venv` con Python 3.11 en la raíz del proyecto.

### 2. Ejecución Rápida
Simplemente haz doble clic sobre el archivo:
```cmd
ejecutar.bat
```
El menú te permitirá elegir entre:
- **[1] Interfaz Web en Streamlit** (Recomendado).
- **[2] Aplicación Ligera de Escritorio** (OpenCV directo).

### 3. Ejecución Manual desde la Terminal (PowerShell)
Para iniciar la interfaz web de Streamlit:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```
O para iniciar la ventana directa de escritorio:
```powershell
.\.venv\Scripts\python.exe app_desktop.py
```

---

## 🎯 Vocabulario Reconocido (77 Clases)
- **26 Letras del Abecedario:** A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z.
- **51 Expresiones y Palabras:**
  - *Saludos y cortesía:* Hola (hello), Adiós (goodbye), Por favor (please), Gracias (thank_you), Disculpa (sorry).
  - *Acciones cotidianas:* Comer (eat), Beber (drink), Ven (come), Ir (go), Aprender (learn), Hablar (speak), Leer (read), Escribir (write), Trabajar (work).
  - *Respuestas y estados:* Sí (yes), No (no), Feliz (happy), Triste (sad), Enojado (angry), Cansado (tired), Bueno (good), Malo (bad).
  - *Objetos y personas:* Agua (water), Comida (food), Amigo (friend), Familia (family), Libro (book), Hogar (home), Escuela (school), Estudiante (student), Profesor (teacher).
  - *Tiempo:* Tiempo (time), Hoy (today), Mañana (tomorrow), Ayer (yesterday), Buenos días (morning), Tarde (afternoon), Buenas noches (night / evening).
