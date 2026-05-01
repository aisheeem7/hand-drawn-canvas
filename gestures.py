import math

def fingers_up(lm_list):
    """
    Detect which fingers are up.
    Returns list of binary values: [index_up, middle_up, ring_up, pinky_up]
    Based on y-coordinates of finger tips vs knuckles
    """
    if len(lm_list) == 0:
        return []

    fingers = []

    # Index finger (tip: 8, pip: 6)
    if lm_list[8][2] < lm_list[6][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Middle finger (tip: 12, pip: 10)
    if lm_list[12][2] < lm_list[10][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Ring finger (tip: 16, pip: 14)
    if lm_list[16][2] < lm_list[14][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Pinky (tip: 20, pip: 18)
    if lm_list[20][2] < lm_list[18][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    return fingers


def thumb_up(lm_list):
    """
    Detect if thumb is up.
    Thumb is up if thumb tip (4) is above thumb pip (3)
    """
    if len(lm_list) < 5:
        return 0
    
    if lm_list[4][1] < lm_list[3][1]:  # Compare x-coordinates
        return 1
    return 0


def is_peace_sign(lm_list):
    """
    Detect peace sign (index and middle finger up, others down).
    Used to trigger eraser mode.
    """
    if len(lm_list) == 0:
        return False
    
    fingers = fingers_up(lm_list)
    
    # Index and middle up, ring and pinky down
    if len(fingers) >= 4:
        return fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0
    
    return False


def is_pointing(lm_list):
    """
    Detect pointing gesture (only index finger up).
    Used for drawing/selection.
    """
    if len(lm_list) == 0:
        return False
    
    fingers = fingers_up(lm_list)
    
    if len(fingers) >= 4:
        return fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0
    
    return False


def is_ok_sign(lm_list):
    """
    Detect OK sign (thumb and index touching, others up).
    """
    if len(lm_list) < 9:
        return False
    
    # Distance between thumb tip (4) and index tip (8)
    thumb_x, thumb_y = lm_list[4][1], lm_list[4][2]
    index_x, index_y = lm_list[8][1], lm_list[8][2]
    
    distance = math.sqrt((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2)
    
    # If distance is small, fingers are touching
    return distance < 30


def is_open_palm(lm_list):
    """
    Detect open palm (all fingers up).
    """
    if len(lm_list) == 0:
        return False
    
    fingers = fingers_up(lm_list)
    
    if len(fingers) >= 4:
        return all(f == 1 for f in fingers)
    
    return False


def is_fist(lm_list):
    """
    Detect closed fist (all fingers down).
    """
    if len(lm_list) == 0:
        return False
    
    fingers = fingers_up(lm_list)
    
    if len(fingers) >= 4:
        return all(f == 0 for f in fingers)
    
    return False


def get_finger_distance(lm_list, finger1_tip, finger2_tip):
    """
    Calculate distance between two finger tips.
    Useful for pinch detection.
    """
    if len(lm_list) < max(finger1_tip, finger2_tip) + 1:
        return float('inf')
    
    x1, y1 = lm_list[finger1_tip][1], lm_list[finger1_tip][2]
    x2, y2 = lm_list[finger2_tip][1], lm_list[finger2_tip][2]
    
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance