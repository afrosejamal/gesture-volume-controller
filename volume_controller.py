import math
import time
from ctypes import cast, POINTER
import cv2
import mediapipe as mp
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Audio setup ---
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# --- Mediapipe setup ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# --- Camera setup ---
CAM_WIDTH, CAM_HEIGHT = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)

# --- Gesture volume control parameters ---
MIN_DIST = 30      # Fingers nearly touching = 0%
MAX_DIST = 250     # Fingers spread = 100%
SMOOTHING = 0.7    # Smoothing factor

class ExponentialSmoother:
    def __init__(self, alpha=0.7, initial=None):
        self.alpha = alpha
        self.state = initial
    def update(self, value):
        if self.state is None:
            self.state = value
        else:
            self.state = self.alpha * self.state + (1 - self.alpha) * value
        return self.state

smoother = ExponentialSmoother(SMOOTHING)

def interp(x, in_min, in_max, out_min, out_max):
    x = max(min(x, in_max), in_min)
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

prev_time = 0

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            h, w, _ = frame.shape
            lm_index = hand_landmarks.landmark[8]  # Index fingertip
            lm_thumb = hand_landmarks.landmark[4]  # Thumb tip
            x1, y1 = int(lm_index.x * w), int(lm_index.y * h)
            x2, y2 = int(lm_thumb.x * w), int(lm_thumb.y * h)
            dist = math.hypot(x2 - x1, y2 - y1)

            # Draw landmarks and line
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

            # Map distance to volume scalar (0.0 - 1.0)
            vol_scalar = interp(dist, MIN_DIST, MAX_DIST, 0.0, 1.0)
            vol_scalar = smoother.update(vol_scalar)
            volume.SetMasterVolumeLevelScalar(vol_scalar, None)

            # Convert to percentage
            vol_percent = int(vol_scalar * 100)

            # Draw volume bar
            bar_x, bar_y, bar_w, bar_h = 50, 100, 30, 250
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (50,50,50), 2)
            fill_h = int(bar_h * vol_percent / 100)
            cv2.rectangle(frame, (bar_x, bar_y + bar_h - fill_h), (bar_x+bar_w, bar_y+bar_h), (0,255,0), cv2.FILLED)

            # Display percentage on screen
            cv2.putText(frame, f'Volume: {vol_percent}%', (bar_x - 10, bar_y + bar_h + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
        prev_time = curr_time
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow('Gesture Volume Controller', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

cap.release()
cv2.destroyAllWindows()

