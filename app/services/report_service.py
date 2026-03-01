import csv
import io
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.subject_repository import SubjectRepository


class ReportService:
    def __init__(self, db: Session):
        self.attendance_repo = AttendanceRepository(db)
        self.person_repo = PersonRepository(db)
        self.subject_repo = SubjectRepository(db)

    def session_csv(self, session_id: int) -> str:
        session = self.attendance_repo.get_session(session_id)
        records = self.attendance_repo.get_records_by_session(session_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        subject_name = session.subject.name if session and session.subject else "N/A"
        writer.writerow(["Session Report"])
        writer.writerow(
            [
                "Session ID",
                "Subject",
                "Start Time",
                "End Time",
                "Status",
                "Total Present",
            ]
        )
        if session:
            writer.writerow(
                [
                    session.id,
                    subject_name,
                    session.start_time.strftime("%Y-%m-%d %H:%M"),
                    session.end_time.strftime("%Y-%m-%d %H:%M") if session.end_time else "",
                    session.status,
                    len(records),
                ]
            )
        writer.writerow([])
        writer.writerow(["#", "Name", "Person ID", "Department", "Time", "Confidence", "Method"])
        for i, rec in enumerate(records, 1):
            p = rec.person
            writer.writerow(
                [
                    i,
                    p.name if p else "Unknown",
                    p.person_id if p else "",
                    p.department if p else "",
                    rec.marked_at.strftime("%H:%M:%S"),
                    f"{rec.confidence:.1%}" if rec.confidence else "",
                    rec.method,
                ]
            )
        return buf.getvalue()

    def person_csv(self, person_id: int) -> str:
        person = self.person_repo.get_by_id(person_id)
        records = self.attendance_repo.get_records_by_person(person_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Attendance History"])
        writer.writerow(["Name", "Person ID", "Department", "Email", "Total Sessions"])
        if person:
            writer.writerow(
                [
                    person.name,
                    person.person_id,
                    person.department or "",
                    person.email or "",
                    len(records),
                ]
            )
        writer.writerow([])
        writer.writerow(["#", "Subject", "Date", "Time", "Confidence", "Method"])
        for i, rec in enumerate(records, 1):
            subject_name = (
                rec.session.subject.name
                if rec.session and rec.session.subject
                else "N/A"
            )
            writer.writerow(
                [
                    i,
                    subject_name,
                    rec.marked_at.strftime("%Y-%m-%d"),
                    rec.marked_at.strftime("%H:%M:%S"),
                    f"{rec.confidence:.1%}" if rec.confidence else "",
                    rec.method,
                ]
            )
        return buf.getvalue()
