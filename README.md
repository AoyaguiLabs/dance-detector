# 🕺 Jamal’s Passinho AI

**Jamal’s Passinho AI** is an interactive Computer Vision experience that turns your body movements into a chaotic invasion of GIFs across your desktop.

Powered by **MediaPipe** for pose tracking and **OpenCV** for dynamic window management, the project creates a fun and *“controlled chaos”* of virtual dancers every time you catch the rhythm.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Dynamic%20UI-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Tracking-orange.svg)

---

## 🚀 Features

*   🎯 **Real-Time Pose Tracking:** Accurate detection of body joints (shoulders, elbows, wrists) using MediaPipe.
*   🔥 **Angle-Based Trigger System:** GIFs are spawned only when your elbows reach a specific activation angle.
*   🧩 **Slot System (Grid Layout):** Smart window management to prevent overlapping and keep your main camera visible.
*   🙏 **Arigato Mode:** A “prayer” gesture (hands together) instantly clears all GIF windows.
*   ⚡ **Optimized Performance:** GIFs are preloaded in multiple sizes (S, M, L) to ensure a smooth 30+ FPS experience.

---

## 🛠️ Tech Stack

*   **Python 3.11+**
*   **OpenCV** (Computer Vision & Window GUI)
*   **MediaPipe** (ML Pose Estimation)
*   **Pillow (PIL)** (Image processing)
*   **NumPy** (Mathematical operations)

---

## 📐 The Math Behind It

The project uses analytical geometry and vector math for gesture detection, translating human movement into digital triggers.

### Hand Distance (Arigato Mode)
To detect the "prayer" gesture, we calculate the Euclidean distance between the Left Wrist $(x_1, y_1)$ and Right Wrist $(x_2, y_2)$ landmarks. If the distance drops below a specific threshold, the screen clears.

$d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$

### Angle Activation (Passinho Trigger)
To detect when you hit the dance move, we calculate the angle at the elbow joint using the coordinates of three points: Shoulder ($A$), Elbow ($B$, the vertex), and Wrist ($C$). We use the law of cosines or vector dot products to find the angle $\theta$:

$\theta = \arccos\left(\frac{\vec{BA} \cdot \vec{BC}}{|\vec{BA}| |\vec{BC}|}\right)$

---

## 📂 Project Structure
```text
passinho_jamal/
├── assets/
│   └── gifs/               # GIF files (Jamal, dog, etc.)
├── venv/                   # Python virtual environment
├── app.py                  # Main application script
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

## 🔧 Installation & Usage

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/passinho-jamal-ai.git](https://github.com/your-username/passinho-jamal-ai.git)
cd passinho-jamal-ai

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python app.py
