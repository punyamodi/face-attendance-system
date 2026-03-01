from typing import Dict

from sqlalchemy.orm import Session

from app.repositories.person_repository import PersonRepository
from app.services.face_service import FaceService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TrainingService:
    def __init__(self, db: Session, face_service: FaceService):
        self.person_repo = PersonRepository(db)
        self.face_service = face_service

    def train_all(self) -> Dict:
        persons = self.person_repo.get_all(active_only=True)
        person_dicts = [{"id": p.id, "name": p.name} for p in persons]
        total_encodings = self.face_service.retrain_all(person_dicts)
        return {
            "persons_trained": len(persons),
            "total_encodings": total_encodings,
            "model_ready": total_encodings > 0,
        }

    def get_training_status(self) -> Dict:
        return {
            "encoding_count": self.face_service.encoding_count,
            "model_exists": self.face_service.encoding_count > 0,
        }
