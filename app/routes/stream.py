import asyncio
from typing import AsyncGenerator

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.attendance_repository import AttendanceRepository
from app.schemas.attendance import CaptureFramesRequest
from app.services.face_service import FaceService, get_face_service
from app.config import settings

router = APIRouter(prefix="/api/stream", tags=["stream"])

_camera: cv2.VideoCapture | None = None


def _get_camera() -> cv2.VideoCapture:
    global _camera
    if _camera is None or not _camera.isOpened():
        _camera = cv2.VideoCapture(settings.camera_index)
        _camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        _camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return _camera


async def _mjpeg_generator(
    face_svc: FaceService, session_id: int | None, db: Session
) -> AsyncGenerator[bytes, None]:
    repo = AttendanceRepository(db) if session_id else None
    cam = _get_camera()
    if not cam.isOpened():
        return
    recognition_interval = 3
    frame_count = 0
    last_faces: list = []
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        if frame_count % recognition_interval == 0:
            last_faces = face_svc.recognize_frame(frame)
            if session_id and repo:
                for face in last_faces:
                    if face["person_id"] is not None:
                        repo.create_record(
                            session_id=session_id,
                            person_id=face["person_id"],
                            confidence=face["confidence"],
                            method="auto",
                        )
        annotated = face_svc.annotate_frame(frame, last_faces)
        _, jpeg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
        frame_count += 1
        await asyncio.sleep(0.03)


@router.get("/video")
async def video_feed(
    session_id: int | None = None,
    face_svc: FaceService = Depends(get_face_service),
    db: Session = Depends(get_db),
):
    return StreamingResponse(
        _mjpeg_generator(face_svc, session_id, db),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/recognize")
async def recognize_single_frame(
    body: CaptureFramesRequest,
    face_svc: FaceService = Depends(get_face_service),
):
    if not body.frames:
        raise HTTPException(status_code=400, detail="No frames provided")
    img = face_svc.decode_base64_image(body.frames[0])
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")
    faces = face_svc.recognize_frame(img)
    return {"faces": faces, "count": len(faces)}


@router.post("/mark")
async def mark_from_frame(
    body: CaptureFramesRequest,
    session_id: int = 0,
    face_svc: FaceService = Depends(get_face_service),
    db: Session = Depends(get_db),
):
    repo = AttendanceRepository(db)
    session = repo.get_session(session_id)
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="No active session")
    if not body.frames:
        raise HTTPException(status_code=400, detail="No frames provided")
    img = face_svc.decode_base64_image(body.frames[0])
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    faces = face_svc.recognize_frame(img)
    marked: list = []
    for face in faces:
        if face["person_id"] is not None:
            record = repo.create_record(
                session_id=session_id,
                person_id=face["person_id"],
                confidence=face["confidence"],
                method="auto",
            )
            if record:
                marked.append(
                    {
                        "person_id": face["person_id"],
                        "person_name": face["person_name"],
                        "confidence": face["confidence"],
                    }
                )
    return {"marked": marked, "faces_detected": len(faces)}
