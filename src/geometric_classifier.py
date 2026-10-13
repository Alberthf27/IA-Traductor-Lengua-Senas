import numpy as np

def analyze_hand_geometry(pts_norm):
    """
    Analiza la geometría tridimensional de los 21 landmarks de una mano
    para clasificar de forma robusta las letras del abecedario dactilológico:
    L, V, U, W, Y, I, D, F, B, C, A, E, K, R, X, etc.
    """
    if pts_norm is None or len(pts_norm) != 21:
        return None
        
    wrist = pts_norm[0] # (0, 0, 0)
    
    # Índices de puntas (tips) y nudillos (MCP / PIP):
    tips = [4, 8, 12, 16, 20]
    pips = [2, 6, 10, 14, 18]
    mcps = [1, 5, 9, 13, 17]
    
    # Distancias Euclidianas desde la muñeca
    dists_tip = np.linalg.norm(pts_norm[tips], axis=1)
    dists_pip = np.linalg.norm(pts_norm[pips], axis=1)
    dists_mcp = np.linalg.norm(pts_norm[mcps], axis=1)
    
    # Dedos extendidos
    index_ext  = dists_tip[1] > (dists_pip[1] * 1.15)
    middle_ext = dists_tip[2] > (dists_pip[2] * 1.15)
    ring_ext   = dists_tip[3] > (dists_pip[3] * 1.15)
    pinky_ext  = dists_tip[4] > (dists_pip[4] * 1.15)
    
    # Pulgar extendido hacia afuera vs pegado a la palma
    dist_thumb_pinky = np.linalg.norm(pts_norm[4] - pts_norm[17])
    dist_mcp_thumb_pinky = np.linalg.norm(pts_norm[2] - pts_norm[17])
    thumb_ext = dist_thumb_pinky > (dist_mcp_thumb_pinky * 1.20)
    
    # Separación entre índice y medio (para 'V' vs 'U')
    dist_index_middle_tips = np.linalg.norm(pts_norm[8] - pts_norm[12])
    fingers_spread = dist_index_middle_tips > 0.075
    
    # Pulgar toca índice (gesto de 'OK' -> F)
    dist_thumb_index_tips = np.linalg.norm(pts_norm[4] - pts_norm[8])
    thumb_index_touching = dist_thumb_index_tips < 0.055
    
    # Todos los dedos tocan el pulgar formando un círculo ('O')
    dist_thumb_middle_tips = np.linalg.norm(pts_norm[4] - pts_norm[12])
    
    # 1. LETRA 'L': Pulgar e índice extendidos formando una L en 90°
    if thumb_ext and index_ext and not middle_ext and not ring_ext and not pinky_ext:
        return {"letter": "L", "conf": 0.92}
        
    # 2. LETRA 'Y': Pulgar y meñique extendidos ("shaka / llamada")
    if thumb_ext and pinky_ext and not index_ext and not middle_ext and not ring_ext:
        return {"letter": "Y", "conf": 0.93}

    # 3. LETRA 'W': Índice, medio y anular extendidos
    if index_ext and middle_ext and ring_ext and not pinky_ext:
        return {"letter": "W", "conf": 0.90}

    # 4. LETRA 'V': Índice y medio abiertos formando una V (paz / victoria)
    if index_ext and middle_ext and not ring_ext and not pinky_ext and fingers_spread:
        return {"letter": "V", "conf": 0.90}

    # 5. LETRA 'U': Índice y medio levantados juntos y pegados
    if index_ext and middle_ext and not ring_ext and not pinky_ext and not fingers_spread:
        return {"letter": "U", "conf": 0.88}

    # 6. LETRA 'I': Solo dedo meñique extendido
    if pinky_ext and not index_ext and not middle_ext and not ring_ext and not thumb_ext:
        return {"letter": "I", "conf": 0.90}

    # 7. LETRA 'D': Solo dedo índice hacia arriba (señalando)
    if index_ext and not middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
        return {"letter": "D", "conf": 0.88}

    # 8. LETRA 'F': Círculo con pulgar e índice ("OK"), otros tres dedos abiertos
    if thumb_index_touching and middle_ext and ring_ext and pinky_ext:
        return {"letter": "F", "conf": 0.88}

    # 9. LETRA 'B': Cuatro dedos abiertos juntos hacia arriba, pulgar doblado
    if index_ext and middle_ext and ring_ext and pinky_ext and not thumb_ext:
        return {"letter": "B", "conf": 0.92}

    # 10. LETRA 'K': Índice arriba, medio horizontal hacia el frente y pulgar abierto
    if index_ext and middle_ext and thumb_ext and not ring_ext and not pinky_ext:
        return {"letter": "K", "conf": 0.86}

    # 11. LETRA 'C': Mano abierta y curvada de perfil (como sostener un vaso)
    if not index_ext and not middle_ext and not ring_ext and not pinky_ext:
        if dist_thumb_index_tips > 0.08 and dist_thumb_index_tips < 0.22:
            return {"letter": "C", "conf": 0.85}
        elif dist_thumb_index_tips <= 0.06:
            # Todos los dedos se tocan con el pulgar formando un círculo
            return {"letter": "O", "conf": 0.82}
        else:
            # Puño cerrado clásico
            return {"letter": "A", "conf": 0.88}

    return None
