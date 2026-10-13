import numpy as np
import mediapipe as mp
import cv2
from src.filters import EMALandmarkFilter

class LandmarkExtractor:
    """
    Extrae landmarks de manos y pose (cabeza, hombros) utilizando MediaPipe Holistic.
    Aplica suavizado adaptativo EMA para eliminar el temblequeo de alta frecuencia.
    """
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.filter_left = EMALandmarkFilter(alpha=0.65)
        self.filter_right = EMALandmarkFilter(alpha=0.65)

    def extract_landmarks(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(frame_rgb)
        
        annotated_frame = frame_bgr.copy()
        
        left_hand_norm = np.zeros((21, 3), dtype=np.float32)
        right_hand_norm = np.zeros((21, 3), dtype=np.float32)
        
        left_hand_raw = None
        right_hand_raw = None
        hands_detected = False

        # Dibujar y procesar mano izquierda
        if results.left_hand_landmarks:
            hands_detected = True
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                results.left_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            raw_pts = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark], dtype=np.float32)
            pts = self.filter_left.update(raw_pts)
            left_hand_raw = pts.copy()
            left_hand_norm = pts - pts[0]
        else:
            self.filter_left.reset()

        # Dibujar y procesar mano derecha
        if results.right_hand_landmarks:
            hands_detected = True
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                results.right_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            raw_pts = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark], dtype=np.float32)
            pts = self.filter_right.update(raw_pts)
            right_hand_raw = pts.copy()
            right_hand_norm = pts - pts[0]
        else:
            self.filter_right.reset()

        # Puntos de referencia faciales/corporales si están disponibles
        pose_info = {}
        if results.pose_landmarks:
            pose_pts = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark], dtype=np.float32)
            pose_info["nose"] = pose_pts[0]       # Nariz / Centro de cara
            pose_info["l_shoulder"] = pose_pts[11] # Hombro izquierdo
            pose_info["r_shoulder"] = pose_pts[12] # Hombro derecho

        # 126 valores para la red profunda
        frame_features = np.concatenate([left_hand_norm.flatten(), right_hand_norm.flatten()])
        
        spatial_data = {
            "left_norm": left_hand_norm if results.left_hand_landmarks else None,
            "right_norm": right_hand_norm if results.right_hand_landmarks else None,
            "left_raw": left_hand_raw,
            "right_raw": right_hand_raw,
            "pose": pose_info,
            "has_left": results.left_hand_landmarks is not None,
            "has_right": results.right_hand_landmarks is not None
        }

        return frame_features, annotated_frame, hands_detected, spatial_data

    def close(self):
        self.holistic.close()
