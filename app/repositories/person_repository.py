from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.models import Person
from app.schemas.person import PersonCreate, PersonUpdate


class PersonRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PersonCreate) -> Person:
        person = Person(**data.model_dump())
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def get_by_id(self, person_id: int) -> Optional[Person]:
        return self.db.query(Person).filter(Person.id == person_id).first()

    def get_by_person_id(self, person_id: str) -> Optional[Person]:
        return self.db.query(Person).filter(Person.person_id == person_id).first()

    def get_all(self, active_only: bool = False) -> List[Person]:
        query = self.db.query(Person)
        if active_only:
            query = query.filter(Person.is_active == True)
        return query.order_by(Person.name).all()

    def search(self, query: str) -> List[Person]:
        return (
            self.db.query(Person)
            .filter(
                or_(
                    Person.name.ilike(f"%{query}%"),
                    Person.person_id.ilike(f"%{query}%"),
                    Person.department.ilike(f"%{query}%"),
                )
            )
            .all()
        )

    def update(self, person_id: int, data: PersonUpdate) -> Optional[Person]:
        person = self.get_by_id(person_id)
        if not person:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(person, key, value)
        self.db.commit()
        self.db.refresh(person)
        return person

    def update_face_count(self, person_id: int, count: int) -> None:
        person = self.get_by_id(person_id)
        if person:
            person.face_count = count
            self.db.commit()

    def delete(self, person_id: int) -> bool:
        person = self.get_by_id(person_id)
        if not person:
            return False
        self.db.delete(person)
        self.db.commit()
        return True

    def count_active(self) -> int:
        return self.db.query(Person).filter(Person.is_active == True).count()
