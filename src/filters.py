import numpy as np

class EMALandmarkFilter:
    """
    Filtro de Suavizado Exponencial (EMA - Exponential Moving Average)
    para landmarks tridimensionales de MediaPipe.
    Elimina el temblequeo de alta frecuencia (jitter) de la cámara
    manteniendo la respuesta instantánea en transiciones rápidas.
    """
    def __init__(self, alpha=0.65):
        self.alpha = alpha
        self.smoothed_pts = None

    def update(self, current_pts):
        """
        current_pts: np.ndarray de forma (21, 3)
        Retorna los puntos suavizados con la misma forma.
        """
        if current_pts is None:
            self.smoothed_pts = None
            return None

        if self.smoothed_pts is None or len(self.smoothed_pts) != len(current_pts):
            self.smoothed_pts = current_pts.copy()
            return self.smoothed_pts

        # Suavizado adaptativo: si el movimiento es brusco (rápido), aumenta alpha para cero retardo
        displacement = np.linalg.norm(current_pts - self.smoothed_pts, axis=1)
        mean_disp = np.mean(displacement)
        
        # Alpha dinámico: más suave en reposo, más reactivo en movimiento rápido
        adaptive_alpha = min(1.0, max(self.alpha, self.alpha + mean_disp * 2.0))
        
        self.smoothed_pts = adaptive_alpha * current_pts + (1.0 - adaptive_alpha) * self.smoothed_pts
        return self.smoothed_pts.copy()

    def reset(self):
        self.smoothed_pts = None
