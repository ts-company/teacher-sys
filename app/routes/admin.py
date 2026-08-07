from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.auth import validate_user
from app.models.attendance import Attendance
from app.models.users_model import User
from app.schemas.user import Attend, Mark
from app.database import get_db
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/admin")

@router.get("/")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/get_students")
def add_user(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    students = db.query(User).filter(User.role == "student").all()

    return [
        {
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "phone_number": s.phone_number,
            "parent_phone_number": s.parent_phone_number,
            "stage": s.stage,
            "level": s.level
        }
        for s in students
    ]

@router.get("/details/{id}")
def add_user(request: Request,
                id: int,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = db.query(Attendance).filter(Attendance.user_id == id).all()

    attendance = [
        {
            "id": r.id,
            "time": r.time,
            "mark": r.mark
        }
        for r in result
    ]
    return templates.TemplateResponse("details.html", {"request": request, "attendance": attendance})

@router.post("/mark_attend")
def mark_attend(request: Request, payload: Attend, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    new_attendance = Attendance(
        user_id = payload.id,
        time = payload.time,
    )
    try:
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return {"success": True}

@router.post("/give_mark/{attendance_id}")
def give_mark(request: Request, attendance_id: int, payload: Mark, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    try:
        attendance.mark = payload.mark
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return {"success": True}