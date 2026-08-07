from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.users_model import User
from app.core.security import hash_password
from app.core.auth import create_access_token
from app.database import get_db
from app.schemas.user import UserCreate
from app.config import BASE_DIR
from datetime import datetime, timezone

templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/signup")

@router.get("/")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/get_signup")
async def signup(usercreate: UserCreate,
                db: Session = Depends(get_db)):

    user = db.query(User).filter(or_(User.username==usercreate.username, User.phone_number==usercreate.phone_number)).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or phone number already exists")

    new_user = User(
        first_name=usercreate.first_name,
        last_name=usercreate.last_name,
        username=usercreate.username,
        password=hash_password(usercreate.password),
        phone_number=usercreate.phone_number,
        parent_phone_number=usercreate.parent_phone_number,
        stage=usercreate.stage,
        level=usercreate.level,
        role="student"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    token = create_access_token({
        "sub": str(new_user.id),
        "role": new_user.role
    })

    response = JSONResponse({"role": new_user.role})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    # for deployment
    # samesite = "none",
    # secure = True,

    return response