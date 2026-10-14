# Estado y Contexto Actual del Proyecto

**Sistema Inteligente de Traducción de Lengua de Señas a Texto y Voz**  
**Rama:** `develop` | **Fecha:** Octubre 2026 | **Licencia:** MIT

---

## 1. Resumen Ejecutivo del Estado del Sistema

El proyecto evolucionó de un prototipo básico con problemas de latencia, temblequeo de landmarks y desfasaje sintáctico a una solución con arquitectura modular desacoplada (**Clean Architecture**), preparada para ejecución en tiempo real tanto en entornos locales (**Desktop OpenCV**) como en la nube (**Streamlit Community Cloud**).

Actualmente el sistema cuenta con:
- **Tubería de visión computacional optimizada:** MediaPipe Holistic (42 landmarks de manos + hombros/rostro).
- **Filtrado estocástico adaptativo:** Supresión de jitter mediante Exponential Moving Average (EMA).
- **Detección cinemática por ápice (Apex Detector):** Gatillado de inferencia por derivadas de posición (velocidad y aceleración), eliminando esperas arbitrarias.
- **Ensamblador morfosintáctico:** Conversión de señas aisladas a lenguaje natural fluido en español con puntuación y cortesías.
- **Motor TTS Zero-Latency:** Despacho asíncrono SAPI en Windows y streaming MP3 con caché LRU para web.
- **Suite de pruebas automatizadas:** 5/5 pruebas unitarias pasando al 100%.

---

## 2. Mapa de Ramas del Repositorio

| Rama | Propósito | Estado |
|---|---|---|
| `main` | Producción / Despliegue en Streamlit Cloud | Estable, con dependencias fijadas y modelos cargados |
| `master` | Compatibilidad histórica | Sincronizada con `main` |
| `develop` | Desarrollo activo, nuevas señas y optimizaciones | Rama actual de trabajo |

---

## 3. Módulos y Arquitectura Implementada

### `src/filters.py` (Filtro EMA Adaptativo)
- Implementa $\hat{x}_t = \alpha \cdot x_t + (1 - \alpha) \cdot \hat{x}_{t-1}$.
- Suprime el ruido del sensor de la cámara web sin inducir retardo perceptual (fijado en $\alpha = 0.65$).

### `src/motion_detector.py` (Detector Cinemático Biomecánico)
- Calcula velocidad instantánea euclidiana de muñeca e índice en ventanas temporales deslizantes.
- Detecta el estado de reposo (*STILL*), movimiento (*MOVING*) y el ápice de la seña (*APEX*).
- Gatilla la inferencia en el punto de inflexión del gesto, mejorando la respuesta y evitando predicciones falsas durante la transición.

### `src/sentence_builder.py` (Ensamblador Morfosintáctico)
- Recibe tokens aislados (ej. `["hola", "como", "estas", "gracias"]`).
- Agrupa letras dactilológicas consecutivas en palabras cohesivas (ej. `["h", "o", "l", "a"]` $\rightarrow$ `"hola"`).
- Aplica reglas de cortesía, capitalización, signos de interrogación invertidos (`¿?`) y puntuación final (`¡Hola! ¿Cómo estás? Muchas gracias.`).

### `src/tts_engine.py` (Motor de Síntesis de Voz)
- En Windows local: utiliza `win32com.client.Dispatch("SAPI.SpVoice")` con bandera asíncrona (`SVSFlagsAsync = 1`), logrando tiempo de respuesta de **0 ms**.
- En la nube / Linux: fallback a `gTTS` con decorador `@functools.lru_cache(maxsize=128)` para streaming instantáneo de audio MP3 sin re-generar frases repetidas.

### `src/landmark_extractor.py` (Extracción Robusta)
- Compatible con entornos modernos de Linux y Windows mediante importación resiliente `from mediapipe.python.solutions import holistic`.
- Integra el suavizado EMA en la fase de extracción previa al buffer secuencial.

---

## 4. Estado de los Modelos de Inteligencia Artificial

### 1. Modelo en Producción (`models/`)
- **Archivos:** `models/best_model.pth` (~39.2 MB) y `models/label_encoder_classes.npy`.
- **Arquitectura:** Red neuronal recurrente espaciotemporal (Bi-LSTM / Bi-GRU con capas densas y Dropout).
- **Vocabulario:** 26 clases de señas estáticas y dinámicas (alfabeto y palabras comunes: Hola, Gracias, Por Favor, Agua, Beber, etc.).

### 2. Modelo de Alta Precisión (`models_high_acc/`)
- **Entrenamiento:** Entrenado mediante `train_high_acc.py` sobre 5,080 muestras reales de landmarks de MediaPipe.
- **Rendimiento:** **98.69% de precisión** en validación.
- **Optimizaciones:** CrossEntropy con Label Smoothing (0.05), Scheduler `CosineAnnealingLR` y normalización euclidiana de coordenadas.

---

## 5. Configuración y Despliegue en Streamlit Community Cloud

### Requisitos Críticos de Despliegue
1. **Versión de Python en el Dashboard:**
   - Debe seleccionarse **Python 3.11** en el menú de Streamlit Cloud (`⋮ -> Settings -> Python version -> 3.11`).
   - *Razón técnica:* Python 3.12+ en Linux tiene incompatibilidad de C-API con MediaPipe y NumPy 2.x.
2. **Dependencias de Sistema (`packages.txt`):**
   ```text
   libgl1
   libglib2.0-0
   ```
3. **Dependencias de Python (`requirements.txt`):**
   ```text
   streamlit>=1.35.0
   opencv-python-headless>=4.8.0
   mediapipe==0.10.14
   torch>=2.0.0
   torchvision>=0.15.0
   numpy>=1.24.0,<2.0.0
   gTTS>=2.4.0
   huggingface-hub>=0.20.0
   streamlit-webrtc>=0.47.0
   ```

---

## 6. Guía de Ejecución Local y Verificación

### Entorno Virtual
```powershell
# Activar entorno virtual existente
.\.venv\Scripts\Activate.ps1
```

### Ejecutar Aplicación Web (Streamlit)
```powershell
streamlit run app.py
```
Incluye diccionario visual de señas interactivo por pestañas (Saludos, Necesidades, Respuestas, Abecedario), telemetría de FPS y latencia en vivo.

### Ejecutar Aplicación de Escritorio de Alto Rendimiento (OpenCV + HUD)
```powershell
python app_desktop.py
```
Controles rápidos:
- `C`: Limpiar frase acumulada.
- `V`: Forzar reproducción por voz (TTS).
- `Q`: Salir.

### Ejecutar Pruebas Automatizadas
```powershell
python -m unittest discover tests/
```
Valida:
- Filtro EMA adaptativo.
- Extractor de landmarks y dimensionalidad.
- Clasificador geométrico euclidiano.
- Ensamblador de oraciones y puntuación.
- Sintetizador de voz y fallback.

---

## 7. Próximos Pasos en la Rama `develop`
1. **Ampliación del Dataset LSP:** Grabar nuevas señas dinámicas peruanas utilizando el script `record_dataset_lsp.py`.
2. **Exportación a ONNX / TensorRT:** Evaluar cuantización INT8 para reducir el tamaño del modelo (`.pth`) de 39 MB a menos de 10 MB, acelerando el arranque en la nube.
3. **WebRTC TURN Server:** Configurar servidores STUN/TURN gratuitos adicionales en `app.py` para mejorar la estabilidad de la cámara web en conexiones móviles.
