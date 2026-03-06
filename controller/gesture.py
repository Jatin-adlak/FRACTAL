# controller/gestures.py
import cv2
import mediapipe as mp
import os
import time
import math
import pyautogui

from .os_control import (
    move_mouse,
    left_click,
    scroll_up,
    scroll_down,
    volume_up,
    volume_down,
    mute,
    minimize_window,
    brightness_up,
    brightness_down
)

# Silence TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# -------------------------------------------------
# GLOBAL STATE
# -------------------------------------------------
_running = False
_last_action_time = 0
COOLDOWN = 1.0  # seconds

# Screen size (absolute mapping)
SCREEN_W, SCREEN_H = pyautogui.size()

# Mouse smoothing
SMOOTHING = 0.2
prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def finger_up(hand, tip, pip):
    return hand.landmark[tip].y < hand.landmark[pip].y


def distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.hypot(x2 - x1, y2 - y1)


def five_finger_pinch(hand, w, h, threshold=40):
    thumb = hand.landmark[4]
    for tip in [8, 12, 16, 20]:
        if distance(thumb, hand.landmark[tip], w, h) > threshold:
            return False
    return True


# -------------------------------------------------
# MAIN GESTURE LOOP
# -------------------------------------------------
def run_gestures():
    global _running, _last_action_time, prev_x, prev_y
    _running = True

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    while _running:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture_label = "NONE"
        now = time.time()

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]

            # Finger states
            index_up  = finger_up(hand, 8, 6)
            middle_up = finger_up(hand, 12, 10)
            ring_up   = finger_up(hand, 16, 14)
            pinky_up  = finger_up(hand, 20, 18)

            thumb_up = hand.landmark[4].x > hand.landmark[2].x
            all_up = index_up and middle_up and ring_up and pinky_up

            # ==================================================
            # COOLDOWN-BASED ACTIONS
            # ==================================================
            if now - _last_action_time > COOLDOWN:

                # ✋ OPEN PALM → MUTE
                if all_up:
                    mute()
                    gesture_label = "MUTE"
                    _last_action_time = now

                # 🤏 FIVE-FINGER PINCH → MINIMIZE WINDOW
                elif five_finger_pinch(hand, w, h):
                    minimize_window()
                    gesture_label = "MINIMIZE"
                    _last_action_time = now

                # 🤏 THUMB + INDEX → CLICK
                elif distance(hand.landmark[4], hand.landmark[8], w, h) < 35:
                    left_click()
                    gesture_label = "CLICK"
                    _last_action_time = now

                # ✌️ BRIGHTNESS (INDEX + MIDDLE, THUMB DOWN)
                elif index_up and middle_up and not thumb_up:
                    if hand.landmark[8].y < hand.landmark[12].y:
                        brightness_up()
                        gesture_label = "BRIGHTNESS UP"
                    else:
                        brightness_down()
                        gesture_label = "BRIGHTNESS DOWN"
                    _last_action_time = now

                # ✌️ SCROLL (INDEX + MIDDLE ONLY)
                elif index_up and middle_up and not ring_up and not pinky_up:
                    if hand.landmark[8].y < hand.landmark[12].y:
                        scroll_up()
                        gesture_label = "SCROLL UP"
                    else:
                        scroll_down()
                        gesture_label = "SCROLL DOWN"
                    _last_action_time = now

                # 👍 / 👎 VOLUME (THUMB ONLY)
                elif not index_up:
                    if thumb_up:
                        volume_up()
                        gesture_label = "VOLUME UP"
                    else:
                        volume_down()
                        gesture_label = "VOLUME DOWN"
                    _last_action_time = now

            # ==================================================
            # ☝️ PRECISE MOUSE MOVE (ONLY INDEX UP)
            # ==================================================
            if (
                index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            ):
                target_x = int(hand.landmark[8].x * SCREEN_W)
                target_y = int(hand.landmark[8].y * SCREEN_H)

                # Clamp to screen bounds
                target_x = max(0, min(SCREEN_W, target_x))
                target_y = max(0, min(SCREEN_H, target_y))

                # Smooth movement
                smooth_x = prev_x + (target_x - prev_x) * SMOOTHING
                smooth_y = prev_y + (target_y - prev_y) * SMOOTHING

                move_mouse(smooth_x, smooth_y)
                prev_x, prev_y = smooth_x, smooth_y
                gesture_label = "MOUSE MOVE"

            draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # -------------------------------------------------
        # UI LABEL
        # -------------------------------------------------
        cv2.rectangle(frame, (0, 0), (480, 45), (0, 0, 0), -1)
        cv2.putText(
            frame,
            f"Gesture: {gesture_label}",
            (10, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        cv2.imshow("FRACTAL – Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def stop_gestures():
    global _running
    _running = False
