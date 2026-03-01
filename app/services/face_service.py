import base64
import pickle
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import face_recognition
import numpy as np

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FaceService:
    def __init__(self):
        self._known_encodings: List[np.ndarray] = []
        self._known_person_ids: List[int] = []
        self._known_names: List[str] = []
        self._load_encodings()

    def _load_encodings(self) -> None:
        if not settings.encodings_file.exists():
            return
        try:
            with open(settings.encodings_file, "rb") as f:
                data = pickle.load(f)
            self._known_encodings = data.get("encodings", [])
            self._known_person_ids = data.get("ids", [])
            self._known_names = data.get("names", [])
            logger.info(f"Loaded {len(self._known_encodings)} face encodings")
        except Exception as exc:
            logger.error(f"Failed to load encodings: {exc}")

    def _save_encodings(self) -> None:
        settings.models_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "encodings": self._known_encodings,
            "ids": self._known_person_ids,
            "names": self._known_names,
        }
        with open(settings.encodings_file, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Saved {len(self._known_encodings)} encodings")

    def _extract_encodings(self, person_dir: Path) -> List[np.ndarray]:
        encodings: List[np.ndarray] = []
        patterns = ("*.jpg", "*.jpeg", "*.png")
        images = [p for pat in patterns for p in person_dir.glob(pat)]
        for img_path in images:
            try:
                image = face_recognition.load_image_file(str(img_path))
                found = face_recognition.face_encodings(image)
                if found:
                    encodings.append(found[0])
            except Exception as exc:
                logger.warning(f"Skipping {img_path.name}: {exc}")
        return encodings

    def _remove_person_from_memory(self, person_id: int) -> None:
        combined = list(
            zip(self._known_encodings, self._known_person_ids, self._known_names)
        )
        filtered = [(e, i, n) for e, i, n in combined if i != person_id]
        if filtered:
            encs, ids, names = zip(*filtered)
            self._known_encodings = list(encs)
            self._known_person_ids = list(ids)
            self._known_names = list(names)
        else:
            self._known_encodings = []
            self._known_person_ids = []
            self._known_names = []

    def save_person_images(
        self, person_id: int, person_name: str, images: List[np.ndarray]
    ) -> int:
        person_dir = settings.faces_dir / str(person_id)
        person_dir.mkdir(parents=True, exist_ok=True)
        existing = list(person_dir.glob("*.jpg"))
        start_idx = len(existing)
        saved = 0
        for i, img in enumerate(images):
            path = person_dir / f"face_{start_idx + i:04d}.jpg"
            cv2.imwrite(str(path), img)
            saved += 1
        self._remove_person_from_memory(person_id)
        new_encs = self._extract_encodings(person_dir)
        for enc in new_encs:
            self._known_encodings.append(enc)
            self._known_person_ids.append(person_id)
            self._known_names.append(person_name)
        self._save_encodings()
        return len(new_encs)

    def retrain_all(self, persons: List[Dict]) -> int:
        self._known_encodings = []
        self._known_person_ids = []
        self._known_names = []
        total = 0
        for person in persons:
            person_dir = settings.faces_dir / str(person["id"])
            if not person_dir.exists():
                continue
            encs = self._extract_encodings(person_dir)
            for enc in encs:
                self._known_encodings.append(enc)
                self._known_person_ids.append(person["id"])
                self._known_names.append(person["name"])
            total += len(encs)
        self._save_encodings()
        logger.info(f"Retrained: {total} encodings across {len(persons)} persons")
        return total

    def recognize_frame(self, frame: np.ndarray) -> List[Dict]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        scale = settings.frame_scale
        small = cv2.resize(rgb, (0, 0), fx=scale, fy=scale)
        locations = face_recognition.face_locations(small, model="hog")
        if not locations:
            return []
        encodings = face_recognition.face_encodings(small, locations)
        results: List[Dict] = []
        inv = 1.0 / scale
        for (top, right, bottom, left), enc in zip(locations, encodings):
            top = int(top * inv)
            right = int(right * inv)
            bottom = int(bottom * inv)
            left = int(left * inv)
            person_id: Optional[int] = None
            person_name = "Unknown"
            confidence = 0.0
            if self._known_encodings:
                distances = face_recognition.face_distance(self._known_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_dist = float(distances[best_idx])
                if best_dist <= settings.tolerance:
                    person_id = self._known_person_ids[best_idx]
                    person_name = self._known_names[best_idx]
                    confidence = round(1.0 - best_dist, 3)
            results.append(
                {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left,
                    "person_id": person_id,
                    "person_name": person_name,
                    "confidence": confidence,
                }
            )
        return results

    def annotate_frame(self, frame: np.ndarray, faces: List[Dict]) -> np.ndarray:
        out = frame.copy()
        for face in faces:
            t, r, b, l = face["top"], face["right"], face["bottom"], face["left"]
            known = face["person_id"] is not None
            color = (34, 197, 94) if known else (239, 68, 68)
            cv2.rectangle(out, (l, t), (r, b), color, 2)
            cv2.rectangle(out, (l, b - 28), (r, b), color, cv2.FILLED)
            label = (
                f"{face['person_name']} {face['confidence']:.0%}"
                if known
                else "Unknown"
            )
            cv2.putText(
                out, label, (l + 5, b - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
        return out

    def decode_base64_image(self, b64: str) -> Optional[np.ndarray]:
        try:
            if "," in b64:
                b64 = b64.split(",")[1]
            raw = base64.b64decode(b64)
            arr = np.frombuffer(raw, np.uint8)
            return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except Exception as exc:
            logger.error(f"Image decode failed: {exc}")
            return None

    def delete_person_data(self, person_id: int) -> None:
        person_dir = settings.faces_dir / str(person_id)
        if person_dir.exists():
            shutil.rmtree(person_dir)
        self._remove_person_from_memory(person_id)
        self._save_encodings()

    def get_photo_count(self, person_id: int) -> int:
        person_dir = settings.faces_dir / str(person_id)
        if not person_dir.exists():
            return 0
        return len(list(person_dir.glob("*.jpg")))

    @property
    def encoding_count(self) -> int:
        return len(self._known_encodings)


_face_service_instance: Optional[FaceService] = None


def get_face_service() -> FaceService:
    global _face_service_instance
    if _face_service_instance is None:
        _face_service_instance = FaceService()
    return _face_service_instance
