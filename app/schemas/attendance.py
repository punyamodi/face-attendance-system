from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AttendanceSessionCreate(BaseModel):
    subject_id: int
    title: Optional[str] = None


class AttendanceSessionResponse(BaseModel):
    id: int
    subject_id: int
    title: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    status: str

    model_config = {"from_attributes": True}


class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    person_id: int
    marked_at: datetime
    confidence: Optional[float]
    method: str
    person_name: Optional[str] = None
    person_identifier: Optional[str] = None

    model_config = {"from_attributes": True}


class ManualAttendanceCreate(BaseModel):
    session_id: int
    person_id: int


class CaptureFramesRequest(BaseModel):
    frames: list[str]


class RecognitionResult(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
    person_id: Optional[int]
    person_name: str
    confidence: float
