import cv2
import mediapipe as mp
import time
import math

from .os_control import (
    left_click,
    scroll_up,
    scroll_down,
    volume_up,
    volume_down,
    mute
)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils

_running = False
_last_action = 0
COOLDOWN = 0.8


def start_camera():
    global _running
    _running = True


def stop_camera():
    global _running
    _running = False


def finger_up(hand, tip, pip):
    return hand.landmark[tip].y < hand.landmark[pip].y


def distance(p1, p2, w, h):
    return math.hypot(
        int(p1.x * w) - int(p2.x * w),
        int(p1.y * h) - int(p2.y * h)
    )


def gen_frames():
    global _last_action

    cap = cv2.VideoCapture(0)
    

    while _running:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        label = "NONE"
        now = time.time()

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]

            index_up = finger_up(hand, 8, 6)
            middle_up = finger_up(hand, 12, 10)
            ring_up = finger_up(hand, 16, 14)
            pinky_up = finger_up(hand, 20, 18)

            thumb_up = hand.landmark[4].x > hand.landmark[2].x
            thumb_down = hand.landmark[4].x < hand.landmark[2].x

            if now - _last_action > COOLDOWN:

                # ✋ MUTE
                if index_up and middle_up and ring_up and pinky_up:
                    mute()
                    label = "MUTE"

                # 🤏 CLICK
                elif distance(hand.landmark[4], hand.landmark[8], w, h) < 35:
                    left_click()
                    label = "CLICK"

                # ✌️ SCROLL
                elif index_up and middle_up:
                    if hand.landmark[8].y < hand.landmark[12].y:
                        scroll_up()
                        label = "SCROLL UP"
                    else:
                        scroll_down()
                        label = "SCROLL DOWN"

                # 👍 / 👎 VOLUME
                elif not index_up:
                    if thumb_up:
                        volume_up()
                        label = "VOLUME UP"
                    elif thumb_down:
                        volume_down()
                        label = "VOLUME DOWN"

                _last_action = now

            draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Overlay label
        cv2.rectangle(frame, (0, 0), (300, 40), (0, 0, 0), -1)
        cv2.putText(frame, label, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
