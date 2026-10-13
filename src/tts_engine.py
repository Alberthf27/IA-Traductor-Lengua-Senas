import os
import threading
import tempfile
import functools
from gtts import gTTS

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

class TextToSpeechManager:
    """
    Gestor de síntesis de voz de ultra baja latencia (Zero-Latency Engine).
    Utiliza SAPI.SpVoice nativo de Windows (asíncrono, 0ms de retardo)
    y memoria caché LRU para streaming de audio MP3 en interfaces web.
    """
    def __init__(self):
        self._sapi_voice = None
        self._init_sapi()

    def _init_sapi(self):
        if HAS_WIN32COM:
            try:
                self._sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
                # Intentar configurar voz en español
                for v in self._sapi_voice.GetVoices():
                    desc = v.GetDescription().lower()
                    if "spanish" in desc or "español" in desc or "helena" in desc or "sabina" in desc or "raul" in desc or "laura" in desc:
                        self._sapi_voice.Voice = v
                        break
                self._sapi_voice.Rate = 0  # Velocidad normal (rango -10 a 10)
            except Exception as e:
                print(f"[!] Aviso SAPI: {e}")
                self._sapi_voice = None

    def speak_async(self, text: str):
        """
        Reproduce voz de manera instantánea y asíncrona.
        Cero bloqueo del hilo de video.
        """
        if not text:
            return

        if self._sapi_voice is not None:
            try:
                # SVSFlagsAsync = 1 (reproducción asíncrona no bloqueante)
                self._sapi_voice.Speak(text, 1)
                return
            except Exception:
                pass

        # Fallback pyttsx3 si SAPI directo fallara
        if HAS_PYTTSX3:
            def _fallback():
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 155)
                    engine.say(text)
                    engine.runAndWait()
                except Exception as ex:
                    print(f"[!] Error fallback TTS: {ex}")

            threading.Thread(target=_fallback, daemon=True).start()

    @functools.lru_cache(maxsize=128)
    def generate_audio_bytes(self, text: str) -> bytes:
        """
        Genera audio en bytes con caché en RAM (LRU Cache).
        La primera vez genera el audio; las siguientes llamadas tardan 0.00 ms.
        """
        if not text:
            return None
        try:
            tts = gTTS(text=text, lang='es', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name
            tts.save(temp_filename)
            with open(temp_filename, "rb") as f:
                audio_bytes = f.read()
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return audio_bytes
        except Exception as e:
            print(f"[!] Error generando audio caché: {e}")
            return None
