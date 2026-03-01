# Face Attendance System

**Automated attendance tracking powered by CNN-based face recognition.**

A full-stack web application that uses deep learning to identify faces in real time and mark attendance — no manual roll calls, no RFID cards.

---

## Features

- **Live Recognition** — MJPEG camera stream with real-time face detection and identification
- **Attendance Sessions** — Start and stop sessions per subject; each session keeps an isolated record
- **Person Registration** — Register people via webcam capture or photo upload; supports multiple face angles
- **Model Training** — One-click retraining across all registered persons; encodings stored as a binary model
- **Manual Override** — Mark or remove attendance entries by hand during any active session
- **Subjects Management** — CRUD for subjects with instructor and description fields
- **Reports & Exports** — Download per-session or per-person attendance as CSV
- **Dashboard** — Weekly bar chart, today's count, model status, and recent session history
- **REST API** — Full JSON API backing every UI action; documented at `/docs`

---

## Architecture

```
face-attendance-system/
├── app/
│   ├── main.py                  FastAPI application entry
│   ├── config.py                Settings via pydantic-settings
│   ├── database/
│   │   ├── connection.py        SQLAlchemy engine and session
│   │   └── models.py            ORM models: Person, Subject, Session, Record
│   ├── repositories/
│   │   ├── person_repository.py
│   │   ├── subject_repository.py
│   │   └── attendance_repository.py
│   ├── services/
│   │   ├── face_service.py      Face encoding, recognition, annotation
│   │   ├── training_service.py  Model retraining orchestration
│   │   └── report_service.py    CSV generation
│   ├── routes/
│   │   ├── pages.py             Jinja2 HTML page routes
│   │   ├── persons.py           /api/persons
│   │   ├── subjects.py          /api/subjects
│   │   ├── attendance.py        /api/attendance
│   │   ├── stream.py            /api/stream  (MJPEG + recognition)
│   │   └── training.py          /api/training
│   ├── schemas/                 Pydantic request/response models
│   └── utils/                   Logger
├── templates/                   Jinja2 HTML (Tailwind CSS)
├── static/                      CSS, JS
├── data/
│   ├── faces/                   Per-person face image directories
│   └── models/                  Trained encoding pickle
├── requirements.txt
└── run.py
```

### Data flow

```
Register Person → Upload/Capture Photos → Extract Face Encodings
                                                    ↓
                                           Save to encodings.pkl
                                                    ↓
Live Session → Camera Frame → Detect Faces → Compare Encodings
                                                    ↓
                                         Match? → Mark Attendance
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Face Recognition | face_recognition (dlib CNN) |
| Computer Vision | OpenCV |
| Database | SQLite via SQLAlchemy |
| Frontend | Jinja2 + Tailwind CSS + Chart.js |
| Streaming | MJPEG over HTTP |

---

## Setup

### Prerequisites

- Python 3.10+
- CMake (required by dlib)
- A working webcam

**Install CMake:**

```bash
# macOS
brew install cmake

# Ubuntu / Debian
sudo apt-get install cmake

# Windows — download from https://cmake.org/download/
```

### Installation

```bash
git clone https://github.com/punyamodi/face-attendance-system.git
cd face-attendance-system

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run

```bash
python run.py
```

Visit **http://localhost:8000**

---

## Quickstart

1. **Add a Subject** — Go to Subjects → Add Subject (e.g. "Mathematics", code "MATH101")
2. **Register People** — Go to People → Register Person → fill details → capture 5+ face samples → Save
3. **Train the Model** — Click "Retrain Model" on the Dashboard (or it trains automatically on registration)
4. **Start a Session** — Go to Live Attendance → select subject → Start Session
5. **Take Attendance** — Camera starts; recognized faces are marked automatically
6. **Export** — Go to Reports → select session → Export CSV

---

## API Reference

Interactive docs available at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/persons` | List all persons |
| POST | `/api/persons` | Create person |
| POST | `/api/persons/{id}/photos` | Upload face photos |
| POST | `/api/persons/{id}/capture` | Save webcam frames |
| GET | `/api/subjects` | List subjects |
| POST | `/api/subjects` | Create subject |
| POST | `/api/attendance/sessions` | Start session |
| PUT | `/api/attendance/sessions/{id}/close` | End session |
| GET | `/api/attendance/sessions/{id}/records` | Get attendance list |
| GET | `/api/attendance/sessions/{id}/export` | Download CSV |
| GET | `/api/stream/video` | MJPEG stream with recognition |
| POST | `/api/training/train` | Retrain face model |
| GET | `/api/training/status` | Model status |

---

## Configuration

Create a `.env` file in the project root:

```env
TOLERANCE=0.5          # Lower = stricter matching (0.4–0.6 recommended)
CAMERA_INDEX=0         # 0 = default webcam
FRAME_SCALE=0.5        # Processing resolution scale (smaller = faster)
DEBUG=false
```

---

## Recognition Accuracy Tips

- Capture samples in varied lighting and at slight angles
- Aim for 8–15 samples per person
- Keep `TOLERANCE` between `0.45` and `0.55`
- Retrain the model after adding new people

---

## License

MIT