from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.subject_repository import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(active_only: bool = False, db: Session = Depends(get_db)):
    repo = SubjectRepository(db)
    return repo.get_all(active_only=active_only)


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    repo = SubjectRepository(db)
    if repo.get_by_code(data.code):
        raise HTTPException(status_code=409, detail="Subject code already exists")
    return repo.create(data)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: int, db: Session = Depends(get_db)):
    repo = SubjectRepository(db)
    subject = repo.get_by_id(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db)
):
    repo = SubjectRepository(db)
    subject = repo.update(subject_id, data)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.delete("/{subject_id}")
async def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    repo = SubjectRepository(db)
    if not repo.delete(subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Deleted successfully"}
