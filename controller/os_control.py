# controller/os_control.py
import pyautogui

SCREEN_W, SCREEN_H = pyautogui.size()
SMOOTHING = 0.2

prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2

# -------------------------------------------------
# GLOBAL SETTINGS
# -------------------------------------------------
pyautogui.FAILSAFE = False   # prevent mouse corner crash
pyautogui.PAUSE = 0.01       # small delay for stability

# -------------------------------------------------
# INTERNAL STATE
# -------------------------------------------------
_muted = False

# -------------------------------------------------
# AUDIO CONTROLS
# -------------------------------------------------
def mute():
    """Mute system volume (one-way, non-toggle)."""
    global _muted
    if not _muted:
        pyautogui.press("volumemute")
        _muted = True

def volume_up():
    """Increase volume and auto-unmute."""
    global _muted
    pyautogui.press("volumeup")
    _muted = False

def volume_down():
    """Decrease volume and auto-unmute."""
    global _muted
    pyautogui.press("volumedown")
    _muted = False


# -------------------------------------------------
# WINDOW CONTROLS
# -------------------------------------------------
def minimize_window():
    """
    Minimize active window.
    Win + Down twice ensures minimize (Windows-safe).
    """
    pyautogui.hotkey("win", "down")
    pyautogui.hotkey("win", "down")


# -------------------------------------------------
# MOUSE CONTROLS
# -------------------------------------------------
def move_mouse(x, y):
    pyautogui.moveTo(x, y, duration=0.1)


def left_click():
    """Left mouse click."""
    pyautogui.click()

def scroll_up():
    """Scroll up."""
    pyautogui.scroll(250)

def scroll_down():
    """Scroll down."""
    pyautogui.scroll(-250)


# -------------------------------------------------
# BRIGHTNESS CONTROLS
# -------------------------------------------------
def brightness_up():
    """
    Increase brightness.
    NOTE:
    Implement OS-specific logic here.
    """
    try:
        pyautogui.press("brightnessup")
    except Exception:
        pass

def brightness_down():
    """
    Decrease brightness.
    NOTE:
    Implement OS-specific logic here.
    """
    try:
        pyautogui.press("brightnessdown")
    except Exception:
        pass
