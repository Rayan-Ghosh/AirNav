import speech_recognition as sr
from pynput.keyboard import Key, Controller
import pyautogui
import threading
import time
# ==========================================
# === Global Variables and Configuration ===
# ==========================================
# Initialize the keyboard controller
keyboard = Controller()
# Global flag to switch between typing mode and command mode
# False = Command Mode (scrolling, shortcuts)
# True = Typing Mode (dictation)
typing_mode = False
# Mapping spoken numbers to their corresponding string representations
number_map = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
}
# Mapping spoken symbols to their corresponding characters
symbol_map = {
    "exclamation": "!",
    "at the rate": "@",
    "hash": "#",
    "dollar": "$",
    "percent": "%",
    "caret": "^",
    "ampersand": "&",
    "asterisk": "*",
    "open bracket": "(",
    "close bracket": ")"
}
# ========================
# === Helper Functions ===
# ========================
def press_key(key):
    """
    Simulates a single key press and release using pynput.
    """
    keyboard.press(key)
    keyboard.release(key)
def press_combo(*keys):
    """
    Simulates a combination key press (e.g., Ctrl + C).
    Keys are pressed in order and released in reverse order for accuracy.
    """
    for k in keys:
        keyboard.press(k)
    for k in reversed(keys):
        keyboard.release(k)
# ====================================
# === Core Voice Listener Function ===
# ====================================
def voice_listener():
    """
    Listens for voice commands continuously in a separate thread.
    Supports typing mode, command mode, and universal shortcuts.
    """
    global typing_mode
    # Initialize recognizer and microphone
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        # Calibrate for ambient noise for better accuracy
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for voice commands...")
        while True:
            try:
                # Listen for up to 5 seconds per phrase
                audio = recognizer.listen(source, phrase_time_limit=5)
                # Convert audio to lowercase text using Google's Speech API
                text = recognizer.recognize_google(audio).lower().strip()
                print(f"You said: {text}")
                # --- Mode Switching ---
                if text == "typing on":
                    typing_mode = True
                    print("Typing mode ON (scroll disabled)")
                    continue
                elif text == "typing off":
                    typing_mode = False
                    print("Typing mode OFF (scroll enabled)")
                    continue
                # --- Typing Mode ---
                if typing_mode:
                    # Type symbols if recognized
                    if text in symbol_map:
                        keyboard.type(symbol_map[text])
                    else:
                        # Type the text followed by a space
                        keyboard.type(text + " ")
                    continue
                # --- Command Mode ---
                if not typing_mode:
                    # Navigation commands
                    if text == "scroll up":
                        pyautogui.scroll(300)
                    elif text == "scroll down":
                        pyautogui.scroll(-300)
                    elif text == "scroll left":
                        pyautogui.hscroll(-300)
                    elif text == "scroll right":
                        pyautogui.hscroll(300)
                    # Zoom commands (Ctrl + Scroll)
                    elif text == "zoom in":
                        pyautogui.keyDown("ctrl")
                        pyautogui.scroll(300)
                        pyautogui.keyUp("ctrl")
                    elif text == "zoom out":
                        pyautogui.keyDown("ctrl")
                        pyautogui.scroll(-300)
                        pyautogui.keyUp("ctrl")
                # --- Universal Commands ---
                # Works in both typing and command modes
                if text == "enter":
                    press_key(Key.enter)
                elif text == "control c":
                    press_combo(Key.ctrl, 'c')
                elif text == "control v":
                    press_combo(Key.ctrl, 'v')
                elif text == "control a":
                    press_combo(Key.ctrl, 'a')
                elif text == "control x":
                    press_combo(Key.ctrl, 'x')
                elif text == "control z":
                    press_combo(Key.ctrl, 'z')
                elif text == "control y":
                    press_combo(Key.ctrl, 'y')
                elif text == "tab":
                    press_key(Key.tab)
                elif text == "shift tab":
                    press_combo(Key.shift, Key.tab)
                elif text == "escape":
                    press_key(Key.esc)
                elif text == "windows":
                    press_key(Key.cmd)
                elif text == "alt tab":
                    press_combo(Key.alt, Key.tab)
                elif text == "backspace":
                    press_key(Key.backspace)
                elif text == "delete":
                    press_key(Key.delete)
                elif text == "caps lock":
                    press_key(Key.caps_lock)
                elif text == "insert":
                    press_key(Key.insert)
                elif text == "print screen":
                    press_key(Key.print_screen)
                elif text == "num lock":
                    press_key(Key.num_lock)
                elif text in number_map:
                    press_key(number_map[text])
            # --- Error Handling ---
            except sr.UnknownValueError:
                # Speech was unintelligible, ignore silently
                pass
            except sr.RequestError as e:
                # API request failed (e.g., no internet)
                print(f"Speech recognition error: {e}")
            except KeyboardInterrupt:
                # Gracefully exit on Ctrl+C
                print("\nExiting...")
                break
# ============================
# === Main Execution Block ===
# ============================
if __name__ == "__main__":
    # Start the voice listener in a separate daemon thread
    voice_thread = threading.Thread(target=voice_listener, daemon=True)
    voice_thread.start()
    # Keep the main program alive
    while True:
        try:
            time.sleep(0.1)  # Prevents high CPU usage
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
