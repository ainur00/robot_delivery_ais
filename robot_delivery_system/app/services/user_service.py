from sqlalchemy.orm import Session
from app import models
from app.schemas import UserCreate

# create
def create_user(db: Session, user: UserCreate):
    """Создание нового пользователя"""
    # Проверяем, не существует ли уже пользователь с таким email
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError(f"Пользователь с email {user.email} уже существует")
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# read
def get_user(db: Session, user_id: int):
    """Получение пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Получение пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Получение пользователя по email"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Получение списка пользователей"""
    return db.query(models.User).offset(skip).limit(limit).all()

# update
def update_user(db: Session, user_id: int, user_data: dict):
    """Обновление данных пользователя"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise ValueError(f"Пользователь с ID {user_id} не найден")
    
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# delete
def delete_user(db: Session, user_id: int):
    """Удаление пользователя по ID"""
    user = get_user(db, user_id)
    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден")
    
    # Проверяем, есть ли активные заявки у пользователя
    active_requests = db.query(models.TransportRequest).filter(
        models.TransportRequest.user_id == user_id,
        models.TransportRequest.status.in_(['PENDING', 'PLANNING', 'IN_PROGRESS'])
    ).first()
    
    if active_requests:
        raise ValueError(f"Невозможно удалить пользователя {user_id}: есть активные заявки")
    
    db.delete(user)
    db.commit()
    return user
