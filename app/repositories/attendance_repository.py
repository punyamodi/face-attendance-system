from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.database.models import AttendanceRecord, AttendanceSession, Person
from app.schemas.attendance import AttendanceSessionCreate


class AttendanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, data: AttendanceSessionCreate) -> AttendanceSession:
        session = AttendanceSession(**data.model_dump())
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> Optional[AttendanceSession]:
        return (
            self.db.query(AttendanceSession)
            .options(joinedload(AttendanceSession.subject))
            .filter(AttendanceSession.id == session_id)
            .first()
        )

    def get_active_session(self) -> Optional[AttendanceSession]:
        return (
            self.db.query(AttendanceSession)
            .options(joinedload(AttendanceSession.subject))
            .filter(AttendanceSession.status == "active")
            .order_by(AttendanceSession.start_time.desc())
            .first()
        )

    def close_session(self, session_id: int) -> Optional[AttendanceSession]:
        session = self.get_session(session_id)
        if session:
            session.status = "completed"
            session.end_time = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session

    def get_all_sessions(self, limit: int = 50) -> List[AttendanceSession]:
        return (
            self.db.query(AttendanceSession)
            .options(joinedload(AttendanceSession.subject))
            .order_by(AttendanceSession.start_time.desc())
            .limit(limit)
            .all()
        )

    def create_record(
        self,
        session_id: int,
        person_id: int,
        confidence: Optional[float] = None,
        method: str = "auto",
    ) -> Optional[AttendanceRecord]:
        existing = (
            self.db.query(AttendanceRecord)
            .filter(
                and_(
                    AttendanceRecord.session_id == session_id,
                    AttendanceRecord.person_id == person_id,
                )
            )
            .first()
        )
        if existing:
            return None
        record = AttendanceRecord(
            session_id=session_id,
            person_id=person_id,
            confidence=confidence,
            method=method,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_records_by_session(self, session_id: int) -> List[AttendanceRecord]:
        return (
            self.db.query(AttendanceRecord)
            .options(joinedload(AttendanceRecord.person))
            .filter(AttendanceRecord.session_id == session_id)
            .order_by(AttendanceRecord.marked_at)
            .all()
        )

    def get_records_by_person(
        self, person_id: int, limit: int = 100
    ) -> List[AttendanceRecord]:
        return (
            self.db.query(AttendanceRecord)
            .options(
                joinedload(AttendanceRecord.session).joinedload(
                    AttendanceSession.subject
                )
            )
            .filter(AttendanceRecord.person_id == person_id)
            .order_by(AttendanceRecord.marked_at.desc())
            .limit(limit)
            .all()
        )

    def delete_record(self, record_id: int) -> bool:
        record = (
            self.db.query(AttendanceRecord)
            .filter(AttendanceRecord.id == record_id)
            .first()
        )
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def get_daily_stats(self, target_date: Optional[date] = None) -> Dict:
        if target_date is None:
            target_date = date.today()
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        count = (
            self.db.query(func.count(AttendanceRecord.id))
            .filter(AttendanceRecord.marked_at.between(start, end))
            .scalar()
        )
        return {"date": str(target_date), "count": count or 0}

    def get_weekly_counts(self) -> List[Dict]:
        today = date.today()
        return [
            self.get_daily_stats(today - timedelta(days=i)) for i in range(6, -1, -1)
        ]

    def get_session_count(self, session_id: int) -> int:
        return (
            self.db.query(func.count(AttendanceRecord.id))
            .filter(AttendanceRecord.session_id == session_id)
            .scalar()
            or 0
        )

    def get_attendance_rate(self, session_id: int, total_persons: int) -> float:
        if total_persons == 0:
            return 0.0
        present = self.get_session_count(session_id)
        return round((present / total_persons) * 100, 2)

    def get_person_stats(self, person_id: int) -> Dict:
        total = (
            self.db.query(func.count(AttendanceRecord.id))
            .filter(AttendanceRecord.person_id == person_id)
            .scalar()
            or 0
        )
        recent = (
            self.db.query(AttendanceRecord)
            .filter(AttendanceRecord.person_id == person_id)
            .order_by(AttendanceRecord.marked_at.desc())
            .first()
        )
        return {
            "total_present": total,
            "last_seen": recent.marked_at.isoformat() if recent else None,
        }
