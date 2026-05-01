import cv2
import numpy as np
import os
from datetime import datetime
from hand_tracking import HandTracker
from gestures import is_pointing

# Configuration
WINDOW_NAME = "Virtual Drawing Board"
FPS_DISPLAY = True

# Color palette (BGR format) - Only 3 colors
COLORS = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
}

COLOR_LIST = ['red', 'green', 'blue']
COLOR_BARS = {color: (i * 80, i * 80 + 70) for i, color in enumerate(COLOR_LIST)}

# Toolbar configuration
TOOLBAR_HEIGHT = 70
CLEAR_ZONE = (240, 320)
UNDO_ZONE = (320, 400)

# Initialize
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

tracker = HandTracker()

# Canvas and drawing state
canvas = None
prev_x, prev_y = 0, 0
current_color = 'red'
brush_thickness = 5
drawing_history = []  # Store canvas snapshots for undo

# FPS tracking
frame_count = 0
fps = 0
prev_time = cv2.getTickCount()

def save_to_history():
    """Save current canvas state to history"""
    if canvas is not None:
        drawing_history.append(canvas.copy())
        # Keep history limited to 20 frames to manage memory
        if len(drawing_history) > 20:
            drawing_history.pop(0)

def undo_drawing():
    """Undo last drawing action"""
    global canvas
    if len(drawing_history) > 0:
        canvas = drawing_history.pop()
    else:
        # If no history, clear canvas
        canvas = np.zeros_like(canvas)

def reset_drawing_state():
    """Reset drawing state when mode changes"""
    global prev_x, prev_y
    prev_x, prev_y = 0, 0

def draw_toolbar(img, current_color):
    """Draw color and control toolbar"""
    h, w = img.shape[:2]
    
    # Draw background
    cv2.rectangle(img, (0, 0), (w, TOOLBAR_HEIGHT), (40, 40, 40), -1)
    
    # Draw color options
    for i, color_name in enumerate(COLOR_LIST):
        start_x = i * 80
        end_x = start_x + 70
        color_bgr = COLORS[color_name]
        
        # Highlight current color
        if color_name == current_color:
            cv2.rectangle(img, (start_x, 5), (end_x, TOOLBAR_HEIGHT - 5), (200, 200, 200), 3)
        else:
            cv2.rectangle(img, (start_x, 5), (end_x, TOOLBAR_HEIGHT - 5), (100, 100, 100), 2)
        
        # Color box
        cv2.rectangle(img, (start_x + 8, 12), (end_x - 8, TOOLBAR_HEIGHT - 12), color_bgr, -1)
        
        # Label
        label = color_name.upper()[0]
        cv2.putText(img, label, (start_x + 22, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # Clear button
    clear_start = CLEAR_ZONE[0]
    clear_end = CLEAR_ZONE[1]
    cv2.rectangle(img, (clear_start, 5), (clear_end, TOOLBAR_HEIGHT - 5), (100, 100, 100), 2)
    cv2.rectangle(img, (clear_start + 3, 8), (clear_end - 3, TOOLBAR_HEIGHT - 8), (100, 150, 200), -1)
    cv2.putText(img, "CLR", (clear_start + 5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Undo button
    undo_start = UNDO_ZONE[0]
    undo_end = UNDO_ZONE[1]
    cv2.rectangle(img, (undo_start, 5), (undo_end, TOOLBAR_HEIGHT - 5), (100, 100, 100), 2)
    cv2.rectangle(img, (undo_start + 3, 8), (undo_end - 3, TOOLBAR_HEIGHT - 8), (150, 150, 200), -1)
    cv2.putText(img, "UND", (undo_start + 5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Info display
    cv2.putText(img, f"Color: {current_color.upper()}", (w - 280, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    return img

def draw_fps(img, fps):
    """Draw FPS counter"""
    cv2.putText(img, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return img

def draw_instructions(img):
    """Draw keyboard instructions at bottom"""
    h, w = img.shape[:2]
    cv2.putText(img, "Keys: C=Clear, Backspace=Undo | Tap color to select | Draw with index finger", 
                (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    return img

def clear_canvas_func():
    """Clear the canvas"""
    global canvas
    save_to_history()
    canvas = np.zeros_like(canvas)
    reset_drawing_state()

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to read frame")
        break
    
    img = cv2.flip(img, 1)
    h, w = img.shape[:2]
    
    # Initialize canvas
    if canvas is None:
        canvas = np.zeros_like(img)
    
    # Get hand landmarks
    lm_list = tracker.get_landmarks(img)
    
    # FPS calculation
    frame_count += 1
    current_time = cv2.getTickCount()
    elapsed = (current_time - prev_time) / cv2.getTickFrequency()
    if elapsed >= 1:
        fps = frame_count / elapsed
        frame_count = 0
        prev_time = current_time
    
    if len(lm_list) > 0:
        # Get index finger position
        index_x, index_y = lm_list[8][1], lm_list[8][2]
        
        # Check if pointing gesture
        if is_pointing(lm_list):
            # Check if in toolbar area
            if index_y < TOOLBAR_HEIGHT:
                # Color selection
                for color_name, (start, end) in COLOR_BARS.items():
                    if start < index_x < end:
                        current_color = color_name
                        reset_drawing_state()
                        break
                
                # Clear button
                if CLEAR_ZONE[0] < index_x < CLEAR_ZONE[1]:
                    clear_canvas_func()
                
                # Undo button
                elif UNDO_ZONE[0] < index_x < UNDO_ZONE[1]:
                    undo_drawing()
                    reset_drawing_state()
            
            # Drawing below toolbar
            else:
                # Smooth drawing - draw line from previous point
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = index_x, index_y
                else:
                    # Draw smooth line as finger moves
                    cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), 
                            COLORS[current_color], brush_thickness)
                
                prev_x, prev_y = index_x, index_y
        else:
            # Not pointing - stop drawing and save to history
            if prev_x != 0 or prev_y != 0:
                save_to_history()
            reset_drawing_state()
        
        # Draw circle at index finger for visual feedback
        cv2.circle(img, (index_x, index_y), 8, (0, 255, 255), -1)
        cv2.circle(img, (index_x, index_y), 12, (0, 255, 255), 2)
    
    else:
        # No hand detected
        if prev_x != 0 or prev_y != 0:
            save_to_history()
        reset_drawing_state()
    
    # Draw toolbar
    img = draw_toolbar(img, current_color)
    
    # FPS display
    if FPS_DISPLAY:
        img = draw_fps(img, fps)
    
    # Draw instructions
    img = draw_instructions(img)
    
    # Merge canvas with webcam image
    # Create mask for canvas
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, canvas_mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
    canvas_mask_inv = cv2.bitwise_not(canvas_mask)
    canvas_mask_3ch = cv2.cvtColor(canvas_mask, cv2.COLOR_GRAY2BGR)
    canvas_mask_inv_3ch = cv2.cvtColor(canvas_mask_inv, cv2.COLOR_GRAY2BGR)
    
    # Blend
    webcam_part = cv2.bitwise_and(img, canvas_mask_inv_3ch)
    drawing_part = cv2.bitwise_and(canvas, canvas_mask_3ch)
    
    final_img = cv2.add(webcam_part, drawing_part)
    
    # Display
    cv2.imshow(WINDOW_NAME, final_img)
    
    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC - quit
        break
    elif key == ord('c') or key == ord('C'):  # C - clear
        clear_canvas_func()
    elif key == 8:  # Backspace - undo
        undo_drawing()

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Drawing board closed")