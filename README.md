# 🛡️ VisionGuard AI

**Professional AI-Based Human Recognition and Robot Tracking System**

VisionGuard AI is a desktop application that enrolls people from gallery
images, recognizes them in real time from a webcam feed, estimates their
distance from the camera, tracks them across frames, and generates
directional commands for a robot to follow a recognized person —
wrapped in a modern, dark-themed CustomTkinter interface.

---

## Overview

VisionGuard AI uses **InsightFace's Buffalo_L** model pack purely as a
pretrained feature extractor — it is never retrained or fine-tuned. The
model provides face detection, 5-point alignment, and 512-dimensional
ArcFace embeddings out of the box. "Training" in this application
exclusively means *enrolling* a person: generating embeddings from
their photos and persisting them to the local face database. Identity
matching at inference time is done with cosine similarity against every
stored embedding (embeddings are never averaged per person).

## Architecture

```
main.py                        Application entry point
app/
├── config.py                  Typed, singleton config.yaml loader/saver
├── logger.py                  Rotating file + console logging setup
├── core/                      Framework-agnostic business logic
│   ├── camera_utils.py        Threaded webcam capture (FPS-tracked)
│   ├── database_utils.py      Embedding + metadata persistence (joblib/JSON)
│   ├── distance_utils.py      Monocular distance estimation & zone classification
│   ├── embedding_utils.py     L2 normalization & cosine similarity matching
│   ├── face_utils.py          InsightFace Buffalo_L wrapper (detect/align/embed)
│   ├── file_utils.py          Filesystem helpers (gallery folders, safe names)
│   ├── image_utils.py         Image I/O, thumbnails, color-space conversion
│   ├── recognition_utils.py   Detection -> matching pipeline + label smoothing
│   ├── robot_utils.py         Command decision logic + serial/simulated dispatch
│   └── tracking_utils.py      Lightweight centroid multi-face tracker
└── ui/                        CustomTkinter presentation layer
    ├── context.py              Shared AppContext (config/db/engine singletons)
    ├── main_window.py           Top-level window, page router
    ├── sidebar.py                Left navigation sidebar
    ├── theme.py                  Shared design tokens (colors, fonts, spacing)
    ├── pages/                    Dashboard, Enroll, Registered, Live, Robot, Settings
    └── widgets/                  InfoCard, DistanceIndicator, dialogs
data/
├── database/                  embeddings.pkl + metadata.json (auto-created)
├── images/                    Per-person enrolled image galleries
├── models/                    InsightFace ONNX model weights (auto-downloaded)
└── logs/                      Rotating application logs
```

The `core` layer has zero dependency on `customtkinter` or any UI code,
so the recognition/robot/database logic can be reused, unit-tested, or
driven from a different front end without modification.

## Features

- **Enroll Person** — upload 2–20 images per identity via a native file
  picker; each image is validated (rejecting zero-face or multi-face
  images), aligned, embedded, and stored individually.
- **Registered Persons** — a searchable table with thumbnail, enrollment
  date, image/embedding counts, and View / Update / Delete actions.
- **Live Recognition** — real-time detection with green (known) / red
  (unknown) boxes, name, confidence %, FPS, live clock, and a
  color-coded circular distance indicator.
- **Robot Mode** — everything in Live Recognition plus autonomous
  target selection and LEFT / RIGHT / FORWARD / BACKWARD / STOP command
  generation, dispatched to an on-screen simulator or real hardware
  over serial.
- **Settings** — edit similarity threshold, distance thresholds, focal
  length, camera index, robot/serial configuration, and theme, all
  persisted back to `config.yaml`.
- **Dashboard** — live system status cards and a recent-activity feed.

## Technology Stack

| Concern              | Library                          |
|-----------------------|----------------------------------|
| Face detection/embedding | InsightFace (Buffalo_L) + ONNX Runtime |
| Image/video processing   | OpenCV, NumPy, Pillow             |
| Similarity search         | scikit-learn / NumPy (cosine similarity) |
| Persistence                | joblib, JSON, PyYAML             |
| Desktop UI                  | CustomTkinter                    |
| Hardware I/O                 | pyserial                        |
| Logging                        | Python `logging` (rotating file handler) |

## Installation

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

On first launch, InsightFace will automatically download the
`buffalo_l` model pack into `data/models/` (requires an internet
connection the first time only).

## Usage / Workflow

1. **Enroll Person** — enter a name, upload 2–20 clear face photos, and
   click *Enroll Person*. If the name already exists you'll be asked to
   Overwrite, Append Images, or Cancel.
2. **Registered Persons** — review, search, update (add more images),
   or delete any enrolled identity.
3. **Live Recognition** — start the camera to see real-time recognition
   with bounding boxes, names, confidence, FPS, and live distance.
4. **Robot Mode** — start tracking to see the same recognition pipeline
   drive simulated (or real, over serial) robot movement commands.
5. **Settings** — tune thresholds, camera index, and robot/serial
   configuration at any time; changes are saved to `config.yaml`.

## Folder Structure

See [Architecture](#architecture) above for the full module layout.
All configurable file paths (database, images, models, logs) live under
`data/` and are created automatically on first run.

## Error Handling

The application is designed to fail gracefully rather than crash:
camera-unavailable, missing/corrupted images, zero-face or multi-face
enrollment images, missing database files, and serial connection
failures are all caught and surfaced to the user through in-app
dialogs, with full details written to the rotating log file at
`data/logs/visionguard.log`.

## Screenshots

*(Add screenshots of the Dashboard, Enroll Person, Registered Persons,
Live Recognition, and Robot Mode pages here after your first run.)*

## Future Scope

- Multi-camera support with per-camera calibration profiles
- On-device liveness/anti-spoofing check before enrollment
- Cloud/remote database sync for multi-workstation deployments
- Configurable robot motion profiles (PID-based smoothing) beyond
  discrete LEFT/RIGHT/FORWARD/BACKWARD/STOP commands
- Automated focal-length calibration wizard in the Settings page
- Export/import of the face database for backup and migration

---

**Important note on scope:** face detection, alignment, and embedding
extraction are performed entirely by the pretrained InsightFace
Buffalo_L model pack. This project never retrains or fine-tunes that
model — enrollment only ever generates and stores embeddings.
