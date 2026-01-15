from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import User, UserCreate, UserLogin
from app.services.user_service import create_user, get_user_by_username

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        return create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=User)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему - возвращает пользователя с его ID"""
    user = get_user_by_username(db, credentials.username)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    return user  # Клиент получает ID и другие данные пользователя
    