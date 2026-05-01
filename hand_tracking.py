import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    MODEL_FILE = "hand_landmarker.task"
    
    def __init__(self):
        """
        Initialize hand tracker using MediaPipe Tasks API (v0.9+).
        Works with MediaPipe 0.10.35 which doesn't have solutions module.
        Automatically downloads the model if not present.
        """
        # Ensure model file exists
        if not os.path.exists(self.MODEL_FILE):
            print(f"Downloading hand_landmarker.task model...")
            try:
                urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_FILE)
                print(f"✓ Model downloaded successfully")
            except Exception as e:
                print(f"✗ Failed to download model: {e}")
                raise
        
        # Create hand landmarker with downloaded model
        base_options = python.BaseOptions(model_asset_path=self.MODEL_FILE)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.detector = vision.HandLandmarker.create_from_options(options)

    def get_landmarks(self, img):
        """
        Get hand landmarks from image.
        Returns list of tuples: [(index, x, y), ...]
        where x, y are pixel coordinates
        """
        h, w, c = img.shape
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=img_rgb
        )
        
        # Detect hand landmarks
        result = self.detector.detect(mp_image)
        
        lm_list = []
        
        if result.hand_landmarks:
            # Get first hand
            hand = result.hand_landmarks[0]
            
            for i, lm in enumerate(hand):
                # Convert normalized coordinates to pixel coordinates
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                lm_list.append((i, cx, cy))
        
        return lm_list
    
    def draw_landmarks(self, img, lm_list):
        """Draw hand landmarks on image for debugging"""
        if lm_list:
            # Draw points
            for i, (idx, x, y) in enumerate(lm_list):
                cv2.circle(img, (x, y), 4, (0, 255, 0), -1)
        return img
    
    def close(self):
        """Cleanup resources"""
        if hasattr(self, 'detector'):
            self.detector.close()
    
    def __del__(self):
        """Cleanup resources on deletion"""
        self.close()