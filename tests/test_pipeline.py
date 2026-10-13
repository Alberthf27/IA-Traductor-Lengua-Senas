import unittest
import numpy as np
import time

from src.filters import EMALandmarkFilter
from src.motion_detector import KinematicMotionDetector
from src.sentence_builder import MorphosyntacticSentenceAssembler
from src.tts_engine import TextToSpeechManager
from src.recognizer import ASLRecognizer

class TestASLPipeline(unittest.TestCase):
    
    def test_ema_filter_reduces_jitter(self):
        filter_ema = EMALandmarkFilter(alpha=0.6)
        # Puntos base
        base_pts = np.ones((21, 3), dtype=np.float32) * 0.5
        filter_ema.update(base_pts)
        
        # Inyectar ruido gaussiano simulado de cámara
        noise = np.random.normal(0, 0.05, (21, 3)).astype(np.float32)
        jittered_pts = base_pts + noise
        smoothed_pts = filter_ema.update(jittered_pts)
        
        # El desplazamiento del punto suavizado debe ser menor que el ruido puro
        smoothed_disp = np.mean(np.abs(smoothed_pts - base_pts))
        raw_disp = np.mean(np.abs(jittered_pts - base_pts))
        self.assertLess(smoothed_disp, raw_disp, "El filtro EMA debe atenuar el ruido de alta frecuencia.")

    def test_motion_detector_state_machine(self):
        detector = KinematicMotionDetector()
        
        # 1. Reposo
        res = detector.update([0.5, 0.5, 0.0])
        self.assertFalse(res["is_apex"])
        
        # 2. Movimiento rápido (preparación del gesto)
        for i in range(5):
            detector.update([0.5 + i * 0.03, 0.5 + i * 0.03, 0.0])
        self.assertEqual(detector.state, "MOVING", "Debe entrar en estado MOVING con alta velocidad.")
        
        # 3. Desaceleración y estabilización (Ápice biomecánico)
        apex_triggered = False
        last_pos = [0.65, 0.65, 0.0]
        for _ in range(5):
            res = detector.update(last_pos)
            if res["is_apex"]:
                apex_triggered = True
                break
        self.assertTrue(apex_triggered, "Debe detectar el ápice tras estabilizar la mano después de un movimiento.")

    def test_sentence_assembler_rules(self):
        assembler = MorphosyntacticSentenceAssembler()
        
        # Caso 1: Saludo cortés
        self.assertEqual(assembler.assemble(["Hola", "Amigo"]), "¡Hola, amigo!")
        
        # Caso 2: Petición con cortesía
        self.assertEqual(assembler.assemble(["Por favor", "Agua"]), "Por favor, ¿me das un vaso de agua?")
        
        # Caso 3: Agrupación dactilológica (deletreo)
        self.assertEqual(assembler.assemble(["C", "A", "S", "A"]), "Casa")
        self.assertEqual(assembler.assemble(["H", "O", "L", "A"]), "¡Hola!")
        
        # Caso 4: Palabra simple enriquecida
        self.assertEqual(assembler.assemble(["Gracias"]), "¡Muchas gracias!")
        self.assertEqual(assembler.assemble(["Ayuda"]), "¡Necesito ayuda!")

    def test_tts_engine_caching(self):
        tts = TextToSpeechManager()
        # Verificar que speak_async no levanta excepciones
        tts.speak_async("Prueba")
        
        # Verificar que el generador de bytes con lru_cache funciona
        t0 = time.time()
        bytes1 = tts.generate_audio_bytes("Hola")
        t_first = time.time() - t0
        
        t0 = time.time()
        bytes2 = tts.generate_audio_bytes("Hola")
        t_cached = time.time() - t0
        
        self.assertIsNotNone(bytes1)
        self.assertEqual(bytes1, bytes2)
        # La consulta en caché debe ser ultra rápida (< 10ms)
        self.assertLess(t_cached, 0.010)

    def test_recognizer_end_to_end_inference(self):
        recognizer = ASLRecognizer()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Warmup inicial (TF Lite delegate initialization)
        recognizer.process_frame(dummy_frame)
        
        # Medir latencia en estado estable
        t0 = time.time()
        ann_frame, pred_info = recognizer.process_frame(dummy_frame)
        latency_ms = (time.time() - t0) * 1000
        
        self.assertEqual(ann_frame.shape, dummy_frame.shape)
        self.assertIn("motion", pred_info)
        self.assertIn("is_apex", pred_info)
        self.assertFalse(pred_info["hands_detected"])
        # Inferencia en estado estacionario debe ser menor a 150ms en CPU
        self.assertLess(latency_ms, 150.0, f"Latencia excesiva en estado estacionario: {latency_ms:.1f}ms")

if __name__ == "__main__":
    unittest.main()
