from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.subject_repository import SubjectRepository
from app.schemas.attendance import (
    AttendanceRecordResponse,
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    ManualAttendanceCreate,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.get("/sessions", response_model=List[AttendanceSessionResponse])
async def list_sessions(limit: int = 50, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    return repo.get_all_sessions(limit=limit)


@router.post("/sessions", response_model=AttendanceSessionResponse, status_code=201)
async def create_session(data: AttendanceSessionCreate, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    if not SubjectRepository(db).get_by_id(data.subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")
    return repo.create_session(data)


@router.get("/sessions/active")
async def get_active_session(db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    session = repo.get_active_session()
    if not session:
        return {"active": False, "session": None}
    return {
        "active": True,
        "session": {
            "id": session.id,
            "subject": session.subject.name if session.subject else None,
            "title": session.title,
            "start_time": session.start_time.isoformat(),
            "status": session.status,
        },
    }


@router.put("/sessions/{session_id}/close", response_model=AttendanceSessionResponse)
async def close_session(session_id: int, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    session = repo.close_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/records", response_model=List[AttendanceRecordResponse])
async def session_records(session_id: int, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    records = repo.get_records_by_session(session_id)
    return [
        AttendanceRecordResponse(
            id=r.id,
            session_id=r.session_id,
            person_id=r.person_id,
            marked_at=r.marked_at,
            confidence=r.confidence,
            method=r.method,
            person_name=r.person.name if r.person else None,
            person_identifier=r.person.person_id if r.person else None,
        )
        for r in records
    ]


@router.post("/sessions/{session_id}/records/manual", status_code=201)
async def manual_attendance(
    session_id: int, data: ManualAttendanceCreate, db: Session = Depends(get_db)
):
    repo = AttendanceRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    record = repo.create_record(
        session_id=session_id,
        person_id=data.person_id,
        method="manual",
    )
    if not record:
        raise HTTPException(status_code=409, detail="Attendance already marked")
    return {"message": "Attendance marked", "record_id": record.id}


@router.delete("/records/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    if not repo.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted"}


@router.get("/sessions/{session_id}/export")
async def export_session_csv(session_id: int, db: Session = Depends(get_db)):
    svc = ReportService(db)
    content = svc.session_csv(session_id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}.csv"},
    )


@router.get("/persons/{person_id}/export")
async def export_person_csv(person_id: int, db: Session = Depends(get_db)):
    svc = ReportService(db)
    content = svc.person_csv(person_id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=person_{person_id}.csv"},
    )


@router.get("/stats/weekly")
async def weekly_stats(db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    return repo.get_weekly_counts()


@router.get("/persons/{person_id}/stats")
async def person_stats(person_id: int, db: Session = Depends(get_db)):
    repo = AttendanceRepository(db)
    return repo.get_person_stats(person_id)
