from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.auth import validate_user
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserEdit
from app.models.users_model import User
from app.database import get_db
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/users")

@router.post("/add_user")
def add_user(request: Request,
                user_create: UserCreate,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.query(User).filter(User.username==user_create.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    new_user = User(
        name=user_create.name,
        username=user_create.username,
        password=hash_password(user_create.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
    }

@router.get("/get_users")
def get_users(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "username": user.username,
        }
        for user in users
    ]

@router.patch("/edit_user/{id}")
def edit_user(request: Request, id: int, edit_user: UserEdit, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.query(User).filter(User.id == id).first()
    if edit_user.name is not None:
        user.name = edit_user.name
    if edit_user.username is not None:
        user.username = edit_user.username
    if edit_user.password is not None:
        user.password = edit_user.password

    db.commit()
    db.refresh(user)
    return {"details": f"user {id} was edited"}

@router.delete("/delete_user/{id}")
def delete_user(request: Request, id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User does not exist"
        )
    db.delete(user)
    db.commit()
    return {"details": f"user {id} deleted"}

@router.get("/")
async def get_page(request: Request):
    token = request.cookies.get("access_token")
    user_id, user_role = validate_user(token)
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return templates.TemplateResponse("add_user.html", {"request": request})