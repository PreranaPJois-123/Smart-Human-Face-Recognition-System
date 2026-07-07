# 🛡️ Smart Human Face Recognition System

**Professional AI-Based Human Recognition and Robot Tracking System**

Smart Human Face Recognition System is a professional desktop application that enrolls people from gallery
images, recognizes them in real time from a webcam feed, estimates their
distance from the camera, tracks them across frames, and generates
directional commands for a robot to follow a recognized person —
all through a modern, dark-themed CustomTkinter interface.

---

# Overview

Smart Human Face Recognition System uses **InsightFace's Buffalo_L** model pack purely as a
pretrained feature extractor—it is never retrained or fine-tuned. The
model provides face detection, facial alignment, and 512-dimensional
ArcFace embeddings out of the box.

In this application, "training" simply means generating and storing
embeddings for enrolled users. During recognition, every live face is
matched against all stored embeddings using cosine similarity. The
embeddings are stored individually and are **never averaged**.

---

# Architecture

```text
main.py                        Application entry point
app/
├── config.py                  Typed, singleton config.yaml loader/saver
├── logger.py                  Rotating file + console logging setup
├── core/
│   ├── camera_utils.py        Threaded webcam capture (FPS-tracked)
│   ├── database_utils.py      Embedding + metadata persistence
│   ├── distance_utils.py      Distance estimation & zone classification
│   ├── embedding_utils.py     Embedding normalization & cosine similarity
│   ├── face_utils.py          InsightFace Buffalo_L wrapper
│   ├── file_utils.py          Filesystem utilities
│   ├── image_utils.py         Image processing utilities
│   ├── recognition_utils.py   Recognition pipeline
│   ├── robot_utils.py         Robot movement command generation
│   └── tracking_utils.py      Multi-face tracking
└── ui/
    ├── context.py
    ├── main_window.py
    ├── sidebar.py
    ├── theme.py
    ├── pages/
    └── widgets/

data/
├── database/
├── images/
├── models/
└── logs/
```

The business logic is completely separated from the user interface,
making the system modular, reusable, and easy to maintain.

---

# Features

### 👤 Person Enrollment

- Upload 2–20 gallery images
- Automatic face validation
- Face alignment
- ArcFace embedding extraction
- Individual embedding storage
- Duplicate identity handling

### 📋 Registered Persons

- Search registered users
- View enrolled images
- Update enrollment
- Delete users

### 🎥 Live Recognition

- Real-time webcam recognition
- Face detection
- Face tracking
- Name prediction
- Confidence score
- FPS display
- Current time
- Distance estimation

### 📏 Distance Estimation

- Live face distance calculation
- Color-coded distance indicator

| Distance | Status |
|----------|--------|
| 0–50 cm | 🔴 Too Close |
| 50–100 cm | 🟢 Ideal |
| 100–150 cm | 🟡 Too Far |
| >150 cm | ⚫ Out of Range |

### 🤖 Robot Mode

- Human tracking
- Horizontal position estimation
- Robot command generation

Commands:

- LEFT
- RIGHT
- FORWARD
- BACKWARD
- STOP

Supports both:

- Simulation mode
- Serial communication with real hardware

### ⚙ Settings

Configure:

- Recognition threshold
- Similarity threshold
- Camera index
- Distance calibration
- Robot settings
- Serial port
- Theme

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python 3.11+ |
| Face Recognition | InsightFace Buffalo_L |
| Inference Engine | ONNX Runtime |
| Computer Vision | OpenCV |
| Numerical Computing | NumPy |
| Machine Learning Utilities | scikit-learn |
| Desktop GUI | CustomTkinter |
| Image Processing | Pillow |
| Configuration | PyYAML |
| Database | Joblib + JSON |
| Robot Communication | pySerial |

---

# Installation

```bash
# Create Virtual Environment

python -m venv venv

# Windows

venv\Scripts\activate

# macOS/Linux

source venv/bin/activate

# Install Dependencies

pip install -r requirements.txt

# Run Application

python main.py
```

On the first launch, the InsightFace **Buffalo_L** model will automatically be downloaded into the `data/models` directory.

---

# Application Workflow

1. Enroll a person using 2–20 images.
2. Store multiple embeddings for each person.
3. Open Live Recognition.
4. Detect faces from webcam.
5. Generate embeddings.
6. Compare embeddings using cosine similarity.
7. Display recognition results.
8. Estimate face distance.
9. Generate robot movement commands.

---

# Folder Structure

```text
app/
data/
requirements.txt
config.yaml
README.md
main.py
```

---

# Error Handling

The application gracefully handles:

- Camera unavailable
- Missing images
- Invalid images
- No face detected
- Multiple faces detected
- Missing database
- Corrupted files
- Serial communication failures

All runtime events are recorded in rotating log files.

---

# Screenshots

> Add screenshots of:

- Dashboard
- Enroll Person
- Registered Persons
- Live Recognition
- Robot Mode
- Settings

---

# Future Enhancements

- Multi-camera support
- Face anti-spoofing
- Cloud synchronization
- Robot PID motion control
- Automatic camera calibration
- Database import/export
- GPU acceleration
- Multi-person tracking optimization

---

# Important Note

This project uses the pretrained **InsightFace Buffalo_L** model exclusively for:

- Face Detection
- Face Alignment
- ArcFace Embedding Extraction

The neural network is **never retrained or fine-tuned**.

Enrollment only generates and stores embeddings, while recognition is performed using cosine similarity against the stored embedding database.

---

## Developed By

**Prerana P Jois**

Computer Science Engineering Student

AI • Computer Vision • Python • Software Engineering
