from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.face_service import FaceService, get_face_service
from app.services.training_service import TrainingService

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("/train")
async def train_model(
    face_svc: FaceService = Depends(get_face_service),
    db: Session = Depends(get_db),
):
    svc = TrainingService(db, face_svc)
    result = svc.train_all()
    return result


@router.get("/status")
async def training_status(
    face_svc: FaceService = Depends(get_face_service),
    db: Session = Depends(get_db),
):
    svc = TrainingService(db, face_svc)
    return svc.get_training_status()
