from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import cv2
import numpy as np

from app.database.connection import get_db
from app.repositories.person_repository import PersonRepository
from app.schemas.attendance import CaptureFramesRequest
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate
from app.services.face_service import FaceService, get_face_service

router = APIRouter(prefix="/api/persons", tags=["persons"])


@router.get("", response_model=List[PersonResponse])
async def list_persons(
    active_only: bool = False,
    q: str = "",
    db: Session = Depends(get_db),
):
    repo = PersonRepository(db)
    if q:
        return repo.search(q)
    return repo.get_all(active_only=active_only)


@router.post("", response_model=PersonResponse, status_code=201)
async def create_person(data: PersonCreate, db: Session = Depends(get_db)):
    repo = PersonRepository(db)
    if repo.get_by_person_id(data.person_id):
        raise HTTPException(status_code=409, detail="Person ID already registered")
    return repo.create(data)


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    repo = PersonRepository(db)
    person = repo.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int, data: PersonUpdate, db: Session = Depends(get_db)
):
    repo = PersonRepository(db)
    person = repo.update(person_id, data)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.delete("/{person_id}")
async def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    face_svc: FaceService = Depends(get_face_service),
):
    repo = PersonRepository(db)
    face_svc.delete_person_data(person_id)
    if not repo.delete(person_id):
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Deleted successfully"}


@router.post("/{person_id}/photos")
async def upload_photos(
    person_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    face_svc: FaceService = Depends(get_face_service),
):
    repo = PersonRepository(db)
    person = repo.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    images: List[np.ndarray] = []
    for f in files:
        raw = await f.read()
        arr = np.frombuffer(raw, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is not None:
            images.append(img)
    if not images:
        raise HTTPException(status_code=400, detail="No valid images provided")
    count = face_svc.save_person_images(person_id, person.name, images)
    repo.update_face_count(person_id, count)
    return {"face_count": count, "message": f"{count} face samples registered"}


@router.post("/{person_id}/capture")
async def capture_webcam_frames(
    person_id: int,
    body: CaptureFramesRequest,
    db: Session = Depends(get_db),
    face_svc: FaceService = Depends(get_face_service),
):
    repo = PersonRepository(db)
    person = repo.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    images: List[np.ndarray] = []
    for b64 in body.frames:
        img = face_svc.decode_base64_image(b64)
        if img is not None:
            images.append(img)
    if not images:
        raise HTTPException(status_code=400, detail="No valid frames provided")
    count = face_svc.save_person_images(person_id, person.name, images)
    repo.update_face_count(person_id, count)
    return {"face_count": count, "message": f"{count} face samples saved"}
