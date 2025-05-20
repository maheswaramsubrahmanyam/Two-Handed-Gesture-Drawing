# ✋🖌️ Two-Handed Gesture Drawing App

This is an advanced real-time gesture-based drawing application using **MediaPipe**, **OpenCV**, and **Python**, designed for use with **two hands**.

- 🖐️ **Left hand**: Tool & color selection, undo, save
- 👉 **Right hand**: Drawing, resizing brush, moving shapes

No keyboard or mouse needed — just use your hands!

---


![thumbnail](https://github.com/user-attachments/assets/cc7dd2b6-13f7-43d4-bc5d-6c619df0d30b)
<br>

![Demo](https://youtu.be/SbddlQf9ihQ?si=KQQW02A_KmlX80pV)


---

## 🧠 Features

| Feature                  | Description                                                             |
|--------------------------|-------------------------------------------------------------------------|
| 🖐️ Left-hand UI Control | Select Pen, Circle, Rectangle, Clear, Save & Colors via left index finger |
| ✍️ Right-hand Drawing   | Freely draw lines and shapes with your right index finger                |
| 🎯 Shape Dragging        | Grab and move existing circles and rectangles with your right hand       |
| 🔄 Undo                  | Raise left index + middle finger to undo last shape/stroke               |
| 🎨 Brush Size Control    | Adjust brush size by pinching thumb and index on right hand              |
| 💾 Save                  | Save your artwork with a left-hand tap on the Save button                |

---

## 📂 Folder Structure

HandGestureDrawingApp/<br>
├── Draw.py # Main application script<br>
├── README.md # This file<br>

yaml

> ⚠️ No external icons or images required. All buttons are drawn using OpenCV.

---

## 🚀 Installation

```bash
git clone https://github.com/your-username/HandGestureDrawingApp.git
cd HandGestureDrawingApp
pip install -r requirements.txt
python Draw.py
```
✅ Requirements
```
opencv-python
mediapipe
numpy
```
Install dependencies with:
```
pip install opencv-python mediapipe numpy
```

 Usage
Start the app: ```python Draw.py```
---

Use left hand index finger to click:

🖊️ Pen

⭕ Circle

▭ Rectangle

🧽 Clear

💾 Save

🎨 Colors
---
Use right hand to:

Draw (index finger down)

Adjust brush size (pinch thumb/index)

Drag shapes (hover & move)

Undo: Raise left index and middle finger
---
🧑‍💻 Author
Maheswaram Subrahmanyam<br>
GitHub: https://github.com/maheswaramsubrahmanyam

---
📄 License
This project is licensed under the MIT License.
