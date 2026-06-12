# Gesture Volume Control

A simple Python program that allows you to control your computer's system volume using hand gestures. By opening your webcam, the app tracks your hand and measures the distance between your thumb and index finger to adjust the audio level in real-time.

---

## 🚀 Features

* **Real-Time Hand Tracking:** Uses your webcam to instantly detect and track your hand.
* **Gesture Control:** Widening the gap between your thumb and index finger increases the volume; bringing them together decreases it.
* **Visual Feedback:** Displays an on-screen volume bar, percentage indicator, and FPS counter directly on the camera feed.

---

## 🛠️ Built With

* **Python** - Core programming language.
* **OpenCV** - Opens the webcam and handles the on-screen display.
* **MediaPipe** - Google's framework used for high-accuracy hand landmark tracking.
* **PyCaw** - Python Audio Control Library used to interact with your system's sound card.

---

## 📦 Prerequisites

Make sure you have Python installed, then install the required dependencies using your terminal:

```bash
pip install opencv-python mediapipe numpy pycaw comtypes
