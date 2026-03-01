from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SubjectCreate) -> Subject:
        subject = Subject(**data.model_dump())
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_code(self, code: str) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.code == code).first()

    def get_all(self, active_only: bool = False) -> List[Subject]:
        query = self.db.query(Subject)
        if active_only:
            query = query.filter(Subject.is_active == True)
        return query.order_by(Subject.name).all()

    def update(self, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
        subject = self.get_by_id(subject_id)
        if not subject:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(subject, key, value)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete(self, subject_id: int) -> bool:
        subject = self.get_by_id(subject_id)
        if not subject:
            return False
        self.db.delete(subject)
        self.db.commit()
        return True

    def count_active(self) -> int:
        return self.db.query(Subject).filter(Subject.is_active == True).count()
