import collections
import numpy as np

class KinematicMotionDetector:
    """
    Detector de dinámica de movimiento y ápice (Apex Detector).
    Modela el ciclo biomecánico del gesto:
      1. IDLE (Mano en reposo / neutra)
      2. MOVING (Fase de preparación o desplazamiento activo)
      3. APEX (Punto cúspide de estabilidad: desaceleración momentánea tras movimiento)
    """
    def __init__(self, history_len=10, speed_thresh_moving=0.018, speed_thresh_stable=0.009, stable_patience=3):
        self.history = collections.deque(maxlen=history_len)
        self.speed_thresh_moving = speed_thresh_moving
        self.speed_thresh_stable = speed_thresh_stable
        self.stable_patience = stable_patience
        
        self.state = "IDLE"
        self.stable_counter = 0
        self.had_motion = False
        self.cooldown_frames = 0

    def update(self, wrist_pt, fingertip_pt=None):
        """
        Actualiza el estado cinemático con la posición normalizada actual de la muñeca (y punta de dedo).
        Retorna un diccionario con métricas y si este fotograma es un Ápice (trigger).
        """
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

        if wrist_pt is None:
            self.history.clear()
            self.state = "IDLE"
            self.had_motion = False
            self.stable_counter = 0
            return {"is_apex": False, "speed": 0.0, "state": "IDLE"}

        pos = np.array(wrist_pt[:2], dtype=np.float32)
        if fingertip_pt is not None:
            # Ponderar muñeca (60%) y punta de índice (40%) para captar tanto traslación como flexión
            pos = 0.6 * pos + 0.4 * np.array(fingertip_pt[:2], dtype=np.float32)

        self.history.append(pos)

        if len(self.history) < 3:
            return {"is_apex": False, "speed": 0.0, "state": "IDLE"}

        # Velocidad instantánea suavizada sobre los últimos 3 fotogramas
        diffs = np.linalg.norm(np.diff(np.array(self.history)[-3:], axis=0), axis=1)
        current_speed = float(np.mean(diffs))

        is_apex = False

        if current_speed > self.speed_thresh_moving:
            self.state = "MOVING"
            self.had_motion = True
            self.stable_counter = 0
        elif current_speed < self.speed_thresh_stable:
            self.stable_counter += 1
            if self.had_motion and self.stable_counter >= self.stable_patience and self.cooldown_frames == 0:
                self.state = "APEX"
                is_apex = True
                self.had_motion = False
                self.cooldown_frames = 12  # Evita doble disparo en el mismo ápice (~0.4s a 30fps)
            elif not self.had_motion and self.stable_counter >= self.stable_patience:
                self.state = "IDLE"
        else:
            # Zona intermedia (desacelerando)
            if self.had_motion:
                self.state = "DECELERATING"

        return {
            "is_apex": is_apex,
            "speed": current_speed,
            "state": self.state,
            "stable_frames": self.stable_counter
        }

    def reset(self):
        self.history.clear()
        self.state = "IDLE"
        self.had_motion = False
        self.stable_counter = 0
        self.cooldown_frames = 0
