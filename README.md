Real-Time Hand Drawn Canvas
A real-time virtual drawing application built using Python, OpenCV, NumPy, and MediaPipe Hands that enables drawing, erasing, and color selection through hand gestures captured via webcam.

Overview
This project uses computer vision techniques to track 21 hand landmarks and interpret finger movements as drawing inputs. The index finger acts as a pointer for drawing, while specific gestures enable mode switching such as erasing or selecting colors.

Features
Real-time hand tracking using MediaPipe

Gesture-based drawing and erasing

Interactive color selection toolbar

Persistent canvas layered over webcam feed

Smooth drawing using continuous coordinate tracking

Modular and scalable project structure

Gesture Controls
Index finger up: Drawing mode

Index & Middle fingers up: Selection/Eraser mode (Hover over toolbar to change colors)

Technologies Used
Python

OpenCV

NumPy

MediaPipe Hands

Usage
Ensure you have the required libraries installed:

Bash
pip install opencv-python numpy mediapipe
Run the application:

Bash
python main.py

3.  The webcam interface will open. Use your finger gestures to draw, erase, and select colors directly on the screen without using a mouse or keyboard.

---

## **Objective**
To demonstrate real-time gesture recognition and human-computer interaction using computer vision.
