from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class PersonCreate(BaseModel):
    name: str
    person_id: str
    department: Optional[str] = None
    email: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class PersonResponse(BaseModel):
    id: int
    name: str
    person_id: str
    department: Optional[str]
    email: Optional[str]
    face_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
