import cv2
import time
from src.recognizer import ASLRecognizer
from src.tts_engine import TextToSpeechManager
from src.sentence_builder import MorphosyntacticSentenceAssembler

def run_desktop():
    print("=" * 65)
    print("  TRADUCTOR INTELIGENTE DE LENGUAJE DE SEÑAS (ASL / LSP)")
    print("  Visión Cinemática con Detección de Ápice y Ensamblado Natural")
    print("=" * 65)
    print("[*] Iniciando cámara web y pipeline cinemático...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Error: No se pudo abrir la cámara web.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    recognizer = ASLRecognizer(confidence_threshold=0.35)
    tts = TextToSpeechManager()
    assembler = MorphosyntacticSentenceAssembler()

    sentence_tokens = []
    last_spoken_label = ""
    last_added_time = 0
    t_prev = time.time()

    print("[*] Sistema listo.")
    print("    - Tecla 'C': Limpiar la oración acumulada")
    print("    - Tecla 'V': Leer la oración completa en voz alta")
    print("    - Tecla 'Q': Salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        t_start = time.time()
        
        annotated_frame, pred_info = recognizer.process_frame(frame)
        curr_time = time.time()
        
        # Cálculo de FPS
        fps = 1.0 / max(curr_time - t_prev, 0.001)
        t_prev = curr_time

        label_es = pred_info.get("spanish_label")
        label_en = pred_info.get("english_label")
        conf = pred_info.get("confidence", 0.0)
        is_apex = pred_info.get("is_apex", False)

        # Disparo fluido: Agregar a la frase en el ápice o al cambiar de seña
        if label_es:
            should_add = (is_apex and label_es != last_spoken_label) or \
                         (label_es != last_spoken_label and (curr_time - last_added_time > 1.2)) or \
                         (curr_time - last_added_time > 3.0)

            if should_add:
                sentence_tokens.append(label_es)
                tts.speak_async(label_es)
                last_spoken_label = label_es
                last_added_time = curr_time

        # --- HUD GRÁFICO SUPERPUESTO ---
        # 1. Barra superior: Oración ensamblada de lenguaje natural
        frase_ensamblada = assembler.assemble(sentence_tokens)
        cv2.rectangle(annotated_frame, (0, 0), (640, 50), (20, 20, 20), -1)
        display_phrase = f"Frase: {frase_ensamblada}" if frase_ensamblada else "Frase: (Realiza señas...)"
        cv2.putText(annotated_frame, display_phrase[:50], (15, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        # 2. Barra inferior: Diagnóstico de seña actual, FPS y estado
        cv2.rectangle(annotated_frame, (0, 435), (640, 480), (15, 15, 15), -1)
        if label_es:
            current_status = f"Detectado: {label_es} ({conf*100:.0f}%)"
            color_stat = (0, 255, 0)
        else:
            motion_state = pred_info.get("motion", {}).get("state", "IDLE")
            current_status = f"Estado: {motion_state}" if pred_info.get("hands_detected") else "Esperando manos..."
            color_stat = (180, 180, 180)

        cv2.putText(annotated_frame, current_status, (15, 465),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_stat, 2)
        cv2.putText(annotated_frame, f"FPS: {fps:.0f}", (530, 465),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)

        cv2.imshow("Traductor Inteligente de Senas [Q: Salir | C: Limpiar | V: Leer]", annotated_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            sentence_tokens.clear()
            last_spoken_label = ""
        elif key == ord('v'):
            if sentence_tokens:
                tts.speak_async(frase_ensamblada)

    cap.release()
    cv2.destroyAllWindows()
    recognizer.extractor.close()
    print("[*] Aplicación de escritorio finalizada.")

if __name__ == "__main__":
    run_desktop()
