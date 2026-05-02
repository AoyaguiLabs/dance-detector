import cv2
import numpy as np
from PIL import Image
import time
import random
import os
import math

try:
    from mediapipe.python.solutions import pose as mp_pose
except ImportError:
    print("❌ Erro: MediaPipe não encontrado.")
    exit()

# --- CONFIGURAÇÕES ---
GIF_DIR = os.path.join("assets", "gifs")
ANGLE_TRIGGER = 80
GRACE_PERIOD = 0.6
PRAYER_THRESHOLD = 0.25 

# GRID ESPAÇADO (X inicial em 650 para não cobrir a câmera)
SLOTS = [
    (650, 0),   (1000, 0),   (1350, 0),
    (650, 350), (1000, 350), (1350, 350),
    (650, 700), (1000, 700), (1350, 700)
]

pose_tracker = mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def load_gifs_with_cache(directory):
    """Pré-carrega GIFs em 3 tamanhos diferentes para evitar lag no spawn"""
    print("⏳ Carregando exército de Jamals e preparando cache...")
    gifs_cache = {} # Estrutura: { nome: { 'P': frames, 'M': frames, 'G': frames } }
    
    if not os.path.exists(directory): return {}
    files = [f for f in os.listdir(directory) if f.lower().endswith(".gif")]
    
    sizes = {"P": 160, "M": 240, "G": 320} # Definição dos tamanhos

    for name in files:
        path = os.path.join(directory, name)
        try:
            img = Image.open(path)
            raw_frames = []
            while True:
                raw_frames.append(img.convert("RGB"))
                img.seek(img.tell() + 1)
        except EOFError:
            if raw_frames:
                gifs_cache[name] = {}
                # Cria as 3 versões redimensionadas de uma vez só no início
                for label, s in sizes.items():
                    processed = [cv2.cvtColor(np.array(f.resize((s, s))), cv2.COLOR_RGB2BGR) for f in raw_frames]
                    gifs_cache[name][label] = processed
                print(f"✅ Cache pronto: {name}")
    return gifs_cache

# --- INICIALIZAÇÃO ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

all_gifs_cache = load_gifs_with_cache(GIF_DIR)
gif_names = list(all_gifs_cache.keys())

active_windows, used_slots = {}, set()
last_spawn, last_movement_time = 0, 0
main_win = "CAMERA_JAMAL"

cv2.namedWindow(main_win)
cv2.moveWindow(main_win, 0, 0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    res = pose_tracker.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    moving_now, is_arigato = False, False
    
    if res.pose_landmarks:
        lm = res.pose_landmarks.landmark
        dist_pulsos = math.sqrt((lm[15].x - lm[16].x)**2 + (lm[15].y - lm[16].y)**2)
        
        if dist_pulsos < PRAYER_THRESHOLD:
            is_arigato = True
            cv2.rectangle(frame, (150, 40), (490, 100), (0, 0, 0), -1)
            cv2.putText(frame, "ARIGATO 🏯", (180, 85), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 255, 255), 2)

        # Tracking (Braços + Mãos)
        for chain in [(11, 13, 15), (12, 14, 16), (15, 17, 19, 21), (16, 18, 20, 22)]:
            for i in range(len(chain) - 1):
                p1 = (int(lm[chain[i]].x * w), int(lm[chain[i]].y * h))
                p2 = (int(lm[chain[i+1]].x * w), int(lm[chain[i+1]].y * h))
                cv2.line(frame, p1, p2, (0, 255, 0), 2)

        # Detecção de braço dobrado
        for side in [(11, 13, 15), (12, 14, 16)]:
            p_ombro = [lm[side[0]].x, lm[side[0]].y]
            p_cotovelo = [lm[side[1]].x, lm[side[1]].y]
            p_pulso = [lm[side[2]].x, lm[side[2]].y]
            
            # Cálculo de ângulo (usando a função np.array interna para ser mais rápido)
            a, b, c = np.array(p_ombro), np.array(p_cotovelo), np.array(p_pulso)
            rad = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
            ang = np.abs(rad * 180.0 / np.pi)
            if (360 - ang if ang > 180 else ang) < ANGLE_TRIGGER:
                moving_now = True

    # --- LÓGICA DE JANELAS (SEM CÁLCULO PESADO) ---
    agora = time.time()
    if is_arigato:
        if active_windows:
            for win_name in list(active_windows.keys()): cv2.destroyWindow(win_name)
            active_windows, used_slots = {}, set()
    elif moving_now:
        last_movement_time = agora
        if (agora - last_spawn) > 0.4:
            available = [n for n in gif_names if n not in active_windows]
            free_slots = [i for i in range(len(SLOTS)) if i not in used_slots]
            
            if available and free_slots:
                new_gif_name = random.choice(available)
                slot_idx = free_slots[0]
                
                # 📏 SORTEIA APENAS O LABEL DO TAMANHO (P, M ou G)
                size_label = random.choice(["P", "M", "G"])
                
                cv2.namedWindow(new_gif_name)
                cv2.moveWindow(new_gif_name, SLOTS[slot_idx][0], SLOTS[slot_idx][1])
                
                # Puxa os frames já processados do cache
                active_windows[new_gif_name] = {
                    "frames": all_gifs_cache[new_gif_name][size_label], 
                    "idx": 0, 
                    "slot": slot_idx
                }
                used_slots.add(slot_idx)
                last_spawn = agora

    elif (agora - last_movement_time) > GRACE_PERIOD:
        if active_windows:
            for win_name in list(active_windows.keys()): cv2.destroyWindow(win_name)
            active_windows, used_slots = {}, set()

    # Renderização Fluida
    for win_name, data in active_windows.items():
        cv2.imshow(win_name, data["frames"][data["idx"]])
        data["idx"] = (data["idx"] + 1) % len(data["frames"])

    cv2.imshow(main_win, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()