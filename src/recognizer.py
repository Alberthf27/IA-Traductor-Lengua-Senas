import os
import collections
import cv2
import numpy as np
import torch
import torch.nn.functional as F

from src.model import ImprovedASLModel
from src.translator import translate_sign
from src.landmark_extractor import LandmarkExtractor
from src.geometric_classifier import analyze_hand_geometry
from src.word_classifier import analyze_gestures_and_words
from src.motion_detector import KinematicMotionDetector

class ASLRecognizer:
    """
    Controlador de reconocimiento de ASL en tiempo real.
    """
    def __init__(self, models_dir=None, seq_len=30, confidence_threshold=0.35):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
            
        self.seq_len = seq_len
        self.confidence_threshold = confidence_threshold
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        labels_file = os.path.join(models_dir, "label_encoder_classes.npy")
        weights_file = os.path.join(models_dir, "best_model.pth")
        
        self.classes = np.load(labels_file, allow_pickle=True).tolist()
        self.num_classes = len(self.classes)
        
        self.model = ImprovedASLModel(num_classes=self.num_classes)
        checkpoint = torch.load(weights_file, map_location=self.device)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        self.sequence_buffer = collections.deque(maxlen=self.seq_len)
        self.wrist_history = collections.deque(maxlen=15)
        self.extractor = LandmarkExtractor()
        self.motion_detector = KinematicMotionDetector()

    def process_frame(self, frame_bgr):
        landmarks, annotated_frame, hands_detected, spatial_data = self.extractor.extract_landmarks(frame_bgr)
        self.sequence_buffer.append(landmarks)
        
        # Registrar y analizar cinemática de la mano activa
        active_raw = spatial_data.get("right_raw") if spatial_data.get("has_right") else spatial_data.get("left_raw")
        wrist_pos = active_raw[0] if active_raw is not None else None
        index_pos = active_raw[8] if active_raw is not None and len(active_raw) > 8 else None
        
        motion_info = self.motion_detector.update(wrist_pos, index_pos)
        
        prediction_info = {
            "english_label": None,
            "spanish_label": None,
            "confidence": 0.0,
            "top3": [],
            "hands_detected": hands_detected,
            "buffer_fill": len(self.sequence_buffer) / self.seq_len,
            "motion": motion_info,
            "is_apex": motion_info["is_apex"]
        }
        
        if not hands_detected:
            self.wrist_history.clear()
            self.motion_detector.reset()
            return annotated_frame, prediction_info

        if active_raw is not None:
            self.wrist_history.append(active_raw[0]) # (x, y, z) de la muñeca
            
        motion_hist_list = list(self.wrist_history)

        # Dibujar HUD cinemático sutil en pantalla
        state_str = motion_info["state"]
        hud_color = (0, 255, 0) if motion_info["is_apex"] else ((0, 165, 255) if state_str == "MOVING" else (200, 200, 200))
        hud_text = f"Apex: ACTIVADO" if motion_info["is_apex"] else f"Estado: {state_str}"
        cv2.putText(annotated_frame, hud_text, (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, hud_color, 2)

        # 1. EVALUAR PALABRAS / EXPRESIONES DE ASL CONTEXTUALES (Hola, Gracias, Por favor, Agua, etc.)
        word_result = analyze_gestures_and_words(spatial_data, motion_hist_list)
        if word_result:
            w_eng = word_result["word"]
            w_esp = word_result["spanish"]
            conf = word_result["conf"]
            prediction_info["top3"] = [{"english": w_eng, "spanish": w_esp, "prob": conf}]
            prediction_info["english_label"] = w_eng
            prediction_info["spanish_label"] = w_esp
            prediction_info["confidence"] = conf
            return annotated_frame, prediction_info

        # 2. EVALUAR LETRAS DACTILOLÓGICAS ESTÁTICAS (L, Y, V, W, I, D, F, B, C, A, etc.)
        active_norm = spatial_data.get("right_norm") if spatial_data.get("has_right") else spatial_data.get("left_norm")
        geom_result = analyze_hand_geometry(active_norm)
        if geom_result:
            letter = geom_result["letter"]
            conf = geom_result["conf"]
            prediction_info["top3"] = [{"english": letter, "spanish": letter, "prob": conf}]
            prediction_info["english_label"] = letter
            prediction_info["spanish_label"] = letter
            prediction_info["confidence"] = conf
            return annotated_frame, prediction_info

        # 3. EVALUACIÓN DE LA RED NEURONAL PROFUNDA (Bi-LSTM + Atención)
        if len(self.sequence_buffer) == self.seq_len:
            seq_array = np.array(self.sequence_buffer, dtype=np.float32)
            tensor_input = torch.tensor(seq_array, dtype=torch.float32).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor_input)
                probs = F.softmax(logits, dim=-1)[0]
                top_values, top_indices = torch.topk(probs, 3)
                top3_list = []
                for val, idx in zip(top_values, top_indices):
                    c_eng = self.classes[idx.item()]
                    c_esp = translate_sign(c_eng)
                    top3_list.append({"english": c_eng, "spanish": c_esp, "prob": val.item()})
                
                prediction_info["top3"] = top3_list
                best = top3_list[0]
                if best["prob"] >= self.confidence_threshold:
                    prediction_info["english_label"] = best["english"]
                    prediction_info["spanish_label"] = best["spanish"]
                    prediction_info["confidence"] = best["prob"]

        return annotated_frame, prediction_info
