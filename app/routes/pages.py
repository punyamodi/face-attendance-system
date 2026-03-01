from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.subject_repository import SubjectRepository
from app.services.face_service import FaceService, get_face_service

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    face_svc: FaceService = Depends(get_face_service),
):
    person_repo = PersonRepository(db)
    attendance_repo = AttendanceRepository(db)
    subject_repo = SubjectRepository(db)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_persons": person_repo.count_active(),
            "total_subjects": subject_repo.count_active(),
            "today_count": attendance_repo.get_daily_stats()["count"],
            "weekly_data": attendance_repo.get_weekly_counts(),
            "recent_sessions": attendance_repo.get_all_sessions(limit=5),
            "active_session": attendance_repo.get_active_session(),
            "encoding_count": face_svc.encoding_count,
        },
    )


@router.get("/persons", response_class=HTMLResponse)
async def persons_page(request: Request, db: Session = Depends(get_db)):
    repo = PersonRepository(db)
    return templates.TemplateResponse(
        "persons.html", {"request": request, "persons": repo.get_all()}
    )


@router.get("/persons/register", response_class=HTMLResponse)
async def register_person_page(request: Request):
    return templates.TemplateResponse("register_person.html", {"request": request})


@router.get("/live", response_class=HTMLResponse)
async def live_page(request: Request, db: Session = Depends(get_db)):
    subject_repo = SubjectRepository(db)
    attendance_repo = AttendanceRepository(db)
    return templates.TemplateResponse(
        "live.html",
        {
            "request": request,
            "subjects": subject_repo.get_all(active_only=True),
            "active_session": attendance_repo.get_active_session(),
        },
    )


@router.get("/subjects", response_class=HTMLResponse)
async def subjects_page(request: Request, db: Session = Depends(get_db)):
    repo = SubjectRepository(db)
    return templates.TemplateResponse(
        "subjects.html", {"request": request, "subjects": repo.get_all()}
    )


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, db: Session = Depends(get_db)):
    attendance_repo = AttendanceRepository(db)
    subject_repo = SubjectRepository(db)
    person_repo = PersonRepository(db)
    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "sessions": attendance_repo.get_all_sessions(limit=50),
            "subjects": subject_repo.get_all(active_only=True),
            "persons": person_repo.get_all(active_only=True),
        },
    )
