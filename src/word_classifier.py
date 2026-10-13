import numpy as np

def analyze_gestures_and_words(spatial_data, motion_history):
    """
    Analiza señas dinámicas oficiales de American Sign Language (ASL):
    1. HOLA (Hello): Mano abierta (B) cerca de la sien / frente que se mueve hacia afuera saludando (estilo saludo militar o saludo lateral).
    2. GRACIAS (Thank you): Mano plana (B) tocando la barbilla/boca y moviéndose hacia adelante y abajo hacia el interlocutor.
    3. POR FAVOR (Please): Mano plana sobre el pecho moviéndose en círculos.
    4. AGUA (Water): Letra 'W' tocando la barbilla dos veces.
    5. COMER (Eat): Yemas de los dedos juntas tocando la boca.
    6. BEBER (Drink): Mano en 'C' inclinada hacia la boca.
    7. AYUDA (Help): Puño sobre la palma plana levantándose.
    8. SÍ (Yes): Puño cerrado inclinándose arriba y abajo (nodding).
    9. NO (No): Índice y medio cerrándose contra el pulgar.
    10. TE QUIERO / AMOR (I Love You): Gesto ILY (pulgar, índice y meñique estirados).
    11. LIBRO (Book): Dos manos reales juntas abriéndose.
    """
    has_left = spatial_data.get("has_left", False)
    has_right = spatial_data.get("has_right", False)
    
    # Obtener mano dominante activa
    active_norm = spatial_data.get("right_norm") if has_right else spatial_data.get("left_norm")
    active_raw = spatial_data.get("right_raw") if has_right else spatial_data.get("left_raw")
    
    if active_norm is None or active_raw is None:
        return None
        
    pose = spatial_data.get("pose", {})
    nose = pose.get("nose") # [x, y, z] en coords de imagen [0, 1]
    
    # Estado de los dedos de la mano activa
    tips = [4, 8, 12, 16, 20]
    pips = [2, 6, 10, 14, 18]
    
    dists_tip = np.linalg.norm(active_norm[tips], axis=1)
    dists_pip = np.linalg.norm(active_norm[pips], axis=1)
    
    index_ext  = dists_tip[1] > (dists_pip[1] * 1.15)
    middle_ext = dists_tip[2] > (dists_pip[2] * 1.15)
    ring_ext   = dists_tip[3] > (dists_pip[3] * 1.15)
    pinky_ext  = dists_tip[4] > (dists_pip[4] * 1.15)
    
    dist_thumb_pinky = np.linalg.norm(active_norm[4] - active_norm[17])
    dist_mcp_thumb_pinky = np.linalg.norm(active_norm[2] - active_norm[17])
    thumb_ext = dist_thumb_pinky > (dist_mcp_thumb_pinky * 1.20)
    
    all_fingers_open = index_ext and middle_ext and ring_ext and pinky_ext
    fist_closed = not index_ext and not middle_ext and not ring_ext and not pinky_ext
    
    # Coordenadas globales de la mano
    wrist_y = active_raw[0, 1] # 0 es arriba de la pantalla, 1 es abajo
    wrist_x = active_raw[0, 0] # 0 es izquierda, 1 es derecha
    
    # Historial de movimiento en los últimos frames
    vel_x = 0.0
    vel_y = 0.0
    if len(motion_history) >= 4:
        vel_x = motion_history[-1][0] - motion_history[0][0]
        vel_y = motion_history[-1][1] - motion_history[0][1]
        
    speed_x = abs(vel_x)
    speed_y = abs(vel_y)
    
    # Altura relativa de la muñeca respecto al centro del rostro (nariz)
    # y = 0 está arriba, y = 1 está abajo
    is_near_head = False
    is_near_chin = False
    is_near_chest = False
    if nose is not None:
        diff_y = wrist_y - nose[1] # Negativo = arriba de la nariz; Positivo = debajo de la nariz
        if diff_y < 0.05:
            # Mano a la altura de los ojos, sien o frente
            is_near_head = True
        elif 0.05 <= diff_y <= 0.25:
            # Mano a la altura de la boca o barbilla
            is_near_chin = True
        else:
            # Mano en el pecho / torso
            is_near_chest = True
    else:
        is_near_head = wrist_y < 0.38
        is_near_chin = 0.38 <= wrist_y <= 0.58
        is_near_chest = wrist_y > 0.58

    # -------------------------------------------------------------
    # 1. "HOLA" (HELLO en ASL):
    # En ASL, "Hello" es un saludo militar que parte de la sien y se proyecta hacia afuera,
    # o mano abierta a la altura de la cabeza saludando.
    # -------------------------------------------------------------
    if all_fingers_open and is_near_head:
        # Si la mano está arriba cerca de la cabeza y se mueve o saluda
        return {"word": "hello", "spanish": "Hola", "conf": 0.94}

    # -------------------------------------------------------------
    # 2. "GRACIAS" (THANK YOU en ASL):
    # Mano plana B que sale desde la barbilla/labios hacia adelante.
    # -------------------------------------------------------------
    if all_fingers_open and is_near_chin and not is_near_head:
        return {"word": "thank_you", "spanish": "Gracias", "conf": 0.93}

    # -------------------------------------------------------------
    # 3. "POR FAVOR" (PLEASE en ASL):
    # Mano abierta sobre el pecho.
    # -------------------------------------------------------------
    if all_fingers_open and is_near_chest and (speed_x > 0.005 or speed_y > 0.005):
        return {"word": "please", "spanish": "Por favor", "conf": 0.90}

    # -------------------------------------------------------------
    # 4. "AGUA" (WATER en ASL):
    # Letra W (3 dedos arriba) cerca de la barbilla o boca.
    # -------------------------------------------------------------
    if index_ext and middle_ext and ring_ext and not pinky_ext and is_near_chin:
        return {"word": "water", "spanish": "Agua", "conf": 0.92}

    # -------------------------------------------------------------
    # 5. "COMER" (EAT en ASL):
    # Yemas de los dedos juntas en pinza cerca de la boca.
    # -------------------------------------------------------------
    dist_tips = np.mean([np.linalg.norm(active_norm[4] - active_norm[t]) for t in [8, 12, 16]])
    if dist_tips < 0.09 and is_near_chin:
        return {"word": "eat", "spanish": "Comer", "conf": 0.91}

    # -------------------------------------------------------------
    # 6. "BEBER" (DRINK en ASL):
    # Mano en forma de letra C (vaso) cerca del rostro.
    # -------------------------------------------------------------
    dist_c = np.linalg.norm(active_norm[4] - active_norm[8])
    if 0.08 < dist_c < 0.22 and not index_ext and is_near_chin:
        return {"word": "drink", "spanish": "Beber", "conf": 0.90}

    # -------------------------------------------------------------
    # 7. "SÍ" (YES en ASL):
    # Puño cerrado subiendo y bajando (asintiendo).
    # -------------------------------------------------------------
    if fist_closed and speed_y > 0.010:
        return {"word": "yes", "spanish": "Sí", "conf": 0.92}

    # -------------------------------------------------------------
    # 8. "NO" (NO en ASL):
    # Índice y medio cerrándose rápidamente contra el pulgar.
    # -------------------------------------------------------------
    dist_no = np.linalg.norm(active_norm[4] - active_norm[8])
    if dist_no < 0.05 and not ring_ext and not pinky_ext:
        return {"word": "no", "spanish": "No", "conf": 0.89}

    # -------------------------------------------------------------
    # 9. "TE QUIERO / AMOR" (I LOVE YOU en ASL):
    # Gesto ILY universal: pulgar, índice y meñique estirados.
    # -------------------------------------------------------------
    if thumb_ext and index_ext and pinky_ext and not middle_ext and not ring_ext:
        return {"word": "love", "spanish": "Te quiero / Amor", "conf": 0.95}

    # -------------------------------------------------------------
    # 10. "LIBRO" (BOOK en ASL):
    # Requiere estrictamente DOS manos reales abiertas juntas que se abren.
    # -------------------------------------------------------------
    if has_left and has_right:
        raw_l = spatial_data["left_raw"]
        raw_r = spatial_data["right_raw"]
        dist_hands = np.linalg.norm(raw_l[0] - raw_r[0])
        # Solo si las dos manos físicas están a menos de 15 cm de distancia
        if dist_hands < 0.18 and all_fingers_open:
            return {"word": "book", "spanish": "Libro", "conf": 0.91}

    # -------------------------------------------------------------
    # 11. "AYUDA" (HELP en ASL):
    # Dos manos: una mano plana con la otra en puño con pulgar arriba encima.
    # -------------------------------------------------------------
    if has_left and has_right:
        raw_l = spatial_data["left_raw"]
        raw_r = spatial_data["right_raw"]
        dist_hands = np.linalg.norm(raw_l[0] - raw_r[0])
        if dist_hands < 0.20 and (speed_y > 0.005 or speed_x > 0.005):
            return {"word": "help", "spanish": "Ayuda", "conf": 0.92}

    return None
