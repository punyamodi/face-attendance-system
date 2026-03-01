from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SubjectCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    instructor: Optional[str] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    is_active: Optional[bool] = None


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    instructor: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
