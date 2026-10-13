import os
import time
import cv2
import numpy as np
from src.landmark_extractor import LandmarkExtractor

def run_collector():
    print("=" * 65)
    print("  GRABADOR DE DATASET DE LENGUA DE SEÑAS PERUANA (LSP)")
    print("  Captura secuencias cinemáticas de 30 frames (126 features)")
    print("=" * 65)
    
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(save_dir, exist_ok=True)
    dataset_file = os.path.join(save_dir, "lsp_dataset.npz")
    
    existing_samples = []
    existing_labels = []
    if os.path.exists(dataset_file):
        data = np.load(dataset_file)
        existing_samples = list(data["samples"])
        existing_labels = list(data["labels"])
        print(f"[*] Dataset existente encontrado con {len(existing_samples)} muestras.")
    
    label_name = input("\nIngrese el nombre de la seña a grabar (ej. 'HOLA', 'AYUDA', 'GRACIAS'): ").strip().upper()
    if not label_name:
        print("[!] Nombre inválido.")
        return

    num_samples_to_record = int(input("¿Cuántas repeticiones desea grabar para esta seña? (Recomendado: 15-30): ") or "15")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Error abriendo cámara web.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    extractor = LandmarkExtractor()

    print(f"\n[*] Todo listo para grabar '{label_name}'.")
    print("    - Presiona 'ESPACIO' para iniciar la captura de una repetición.")
    print("    - Presiona 'Q' para salir y guardar.")

    current_recorded = 0
    seq_len = 30

    while current_recorded < num_samples_to_record:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        _, annotated, hands_detected, _ = extractor.extract_landmarks(frame)

        status_text = f"Seña: {label_name} | Muestras: {current_recorded}/{num_samples_to_record}"
        cv2.putText(annotated, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(annotated, "Presiona ESPACIO para grabar | Q para terminar", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Grabador de Dataset LSP", annotated)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == 32:  # Barra espaciadora
            # Cuenta regresiva rápida
            for count in [3, 2, 1]:
                t_end = time.time() + 0.6
                while time.time() < t_end:
                    ret_c, frame_c = cap.read()
                    if not ret_c:
                        break
                    frame_c = cv2.flip(frame_c, 1)
                    cv2.putText(frame_c, f"Preparate: {count}", (240, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)
                    cv2.imshow("Grabador de Dataset LSP", frame_c)
                    cv2.waitKey(1)

            # Grabación de 30 fotogramas
            sequence_data = []
            print(f"[*] Grabando repetición #{current_recorded + 1}...")
            
            while len(sequence_data) < seq_len:
                ret_rec, frame_rec = cap.read()
                if not ret_rec:
                    break
                frame_rec = cv2.flip(frame_rec, 1)
                feats, ann_rec, _, _ = extractor.extract_landmarks(frame_rec)
                sequence_data.append(feats)

                pct = int((len(sequence_data) / seq_len) * 100)
                cv2.putText(ann_rec, f"GRABANDO: {pct}%", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.imshow("Grabador de Dataset LSP", ann_rec)
                cv2.waitKey(20)

            if len(sequence_data) == seq_len:
                existing_samples.append(np.array(sequence_data, dtype=np.float32))
                existing_labels.append(label_name)
                current_recorded += 1
                print(f"    [OK] Repetición #{current_recorded} guardada.")

    cap.release()
    cv2.destroyAllWindows()
    extractor.close()

    if existing_samples:
        np.savez_compressed(dataset_file, samples=np.array(existing_samples), labels=np.array(existing_labels))
        print(f"\n[ÉXITO] Dataset guardado en: {dataset_file}")
        print(f"Total acumulado: {len(existing_samples)} muestras.")
    else:
        print("\n[*] No se capturaron nuevas muestras.")

if __name__ == "__main__":
    run_collector()
