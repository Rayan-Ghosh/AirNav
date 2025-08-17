import cv2
import mediapipe as mp
import numpy as np
from pynput.mouse import Controller, Button
import time
# ================================
# CONFIGURATION & INITIALIZATION
# ================================
# Mouse controller from pynput
mouse = Controller()
# Click timing variables for detecting double-clicks & preventing rapid clicks
last_double_click_time = 0
last_click_time = 0
click_delay = 0.3  # Minimum delay between clicks (seconds)
# Dragging state
dragging = False
pinch_start_time = 0
drag_release_time = 0
DRAG_HOLD_TIME = 0.8  # Time (seconds) to hold pinch before drag starts

# Mediapipe Hands setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,               # Track up to 2 hands
    min_detection_confidence=0.8,  # Detection confidence threshold
    min_tracking_confidence=0.8    # Tracking confidence threshold
)
# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)
# Screen resolution (adjust if needed)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
# Gesture sensitivity thresholds
LEFT_CLICK_THRESHOLD = 0.04   # Distance between thumb & index tip for left click
RIGHT_CLICK_THRESHOLD = 0.04  # Distance between thumb & middle tip for right click
# Cursor smoothing variables
prev_x, prev_y = 0, 0
SMOOTHING = 4  # Higher = smoother, slower movement
# Click readiness flags (prevent multiple clicks while fingers are held together)
left_click_ready = True
right_click_ready = True
# ================================
# MAIN LOOP
# ================================
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    img_h, img_w, _ = frame.shape
    # Convert BGR to RGB for Mediapipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    # Process detected hands
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = hand_info.classification[0].label  # "Left" or "Right"
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # =======================
            # LEFT HAND → Mouse Movement
            # =======================
            if label == "Left":
                index_tip = hand_landmarks.landmark[8]
                # Scale hand coordinates to screen resolution
                DPI_FACTOR = 1.5  # Increase sensitivity
                x = np.interp(index_tip.x, [0, 1], [0, SCREEN_WIDTH]) * DPI_FACTOR
                y = np.interp(index_tip.y, [0, 1], [0, SCREEN_HEIGHT]) * DPI_FACTOR
                # Smooth cursor movement
                curr_x = prev_x + (x - prev_x) / SMOOTHING
                curr_y = prev_y + (y - prev_y) / SMOOTHING
                prev_x, prev_y = curr_x, curr_y
                # Move mouse pointer
                mouse.position = (curr_x, curr_y)
            # =======================
            # RIGHT HAND → Click & Drag
            # =======================
            elif label == "Right":
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                # Calculate distances between fingertips (normalized coords)
                dist_index_thumb = np.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                dist_middle_thumb = np.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y)
                current_time = time.time()
                # ---- LEFT CLICK ----
                if dist_index_thumb < LEFT_CLICK_THRESHOLD and left_click_ready:
                    if current_time - last_double_click_time < click_delay:
                        mouse.click(Button.left, 2)  # Double click
                        last_double_click_time = 0
                    else:
                        mouse.click(Button.left, 1)  # Single click
                        last_double_click_time = current_time
                    left_click_ready = False
                elif dist_index_thumb >= LEFT_CLICK_THRESHOLD:
                    left_click_ready = True
                # ---- RIGHT CLICK ----
                if dist_middle_thumb < RIGHT_CLICK_THRESHOLD and right_click_ready:
                    if time.time() - drag_release_time > 0.3:  # Prevent accidental right click after drag
                        mouse.click(Button.right, 1)
                        right_click_ready = False
                elif dist_middle_thumb >= RIGHT_CLICK_THRESHOLD:
                    right_click_ready = True
                # ---- CLICK & DRAG ----
                if dist_index_thumb < LEFT_CLICK_THRESHOLD:
                    if pinch_start_time == 0:
                        pinch_start_time = current_time
                    held_time = current_time - pinch_start_time
                    if held_time >= DRAG_HOLD_TIME and not dragging:
                        mouse.press(Button.left)
                        dragging = True
                else:
                    pinch_start_time = 0
                    if dragging:
                        mouse.release(Button.left)
                        dragging = False
                        drag_release_time = time.time()
    # Show video feed with hand landmarks
    cv2.imshow("Hand Gesture Mouse", frame)
    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break
# ================================
# CLEANUP
# ================================
cap.release()
cv2.destroyAllWindows()
