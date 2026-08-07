from fastapi import APIRouter, Form, Depends, status, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models.users_model import User
from app.core.security import verify_password
from app.core.auth import create_access_token
from app.database import get_db

router = APIRouter()

@router.post("/login")
async def login(username: str = Form(...),
                password: str = Form(...),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })
    response = JSONResponse({"role": user.role})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none",
        secure=True,
        path="/"
    )

    return response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
    )

    return {"message": "Logged out successfully"}