from sqlalchemy.orm import Session
from app import models
from app.schemas import TransportRequestCreate

# create
def create_transport_request(db: Session, request: TransportRequestCreate):
    """Создание новой заявки на перевозку"""
    # Проверяем, существует ли робот
    robot = db.query(models.Robot).filter(models.Robot.id == request.robot_id).first()
    if not robot:
        raise ValueError(f"Робот с ID {request.robot_id} не найден")
    
    # Проверяем, доступен ли робот
    if robot.status == 'BUSY':
        raise ValueError(f"Робот {robot.name} уже занят")
    
    # Проверяем, существует ли пользователь
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise ValueError(f"Пользователь с ID {request.user_id} не найден")
    
    # Создаем заявку
    db_request = models.TransportRequest(
        user_id=request.user_id,
        robot_id=request.robot_id,
        target_x=request.target_x,
        target_y=request.target_y,
        status='PENDING'
    )
    
    # Меняем статус робота на BUSY
    robot.status = 'BUSY'
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

# read
def get_transport_request(db: Session, request_id: int):
    """Получение заявки по ID"""
    return db.query(models.TransportRequest).filter(
        models.TransportRequest.id == request_id
    ).first()

def get_user_requests(db: Session, user_id: int):
    """Получение всех заявок пользователя"""
    return db.query(models.TransportRequest).filter(
        models.TransportRequest.user_id == user_id
    ).order_by(models.TransportRequest.created_at.desc()).all()

# update
def update_request_status(db: Session, request_id: int, status: str):
    """Обновление статуса заявки"""
    valid_statuses = ['PENDING', 'PLANNING', 'READY', 'IN_PROGRESS', 'COMPLETED', 'FAILED']
    if status not in valid_statuses:
        raise ValueError(f"Неверный статус. Допустимые: {valid_statuses}")
    
    db_request = get_transport_request(db, request_id)
    if not db_request:
        raise ValueError(f"Заявка с ID {request_id} не найдена")
    
    old_status = db_request.status
    db_request.status = status
    
    # Если заявка завершена или провалена, освобождаем робота
    if status in ['COMPLETED', 'FAILED']:
        robot = db.query(models.Robot).filter(models.Robot.id == db_request.robot_id).first()
        if robot:
            robot.status = 'IDLE'
    
    db.commit()
    db.refresh(db_request)
    return db_request

def cancel_request(db: Session, request_id: int):
    """Отмена заявки"""
    db_request = get_transport_request(db, request_id)
    if not db_request:
        raise ValueError(f"Заявка с ID {request_id} не найдена")
    
    if db_request.status in ['PENDING', 'PLANNING']:
        db_request.status = 'FAILED'
        
        # Освобождаем робота
        robot = db.query(models.Robot).filter(models.Robot.id == db_request.robot_id).first()
        if robot:
            robot.status = 'IDLE'
        
        db.commit()
        db.refresh(db_request)
    else:
        raise ValueError(f"Невозможно отменить заявку со статусом {db_request.status}")
    
    return db_request

# delete
def delete_transport_request(db: Session, request_id: int):
    """Удаление заявки по ID"""
    db_request = get_transport_request(db, request_id)
    if not db_request:
        raise ValueError(f"Заявка с ID {request_id} не найдена")
    
    # Если заявка активна, освобождаем робота
    if db_request.status in ['PENDING', 'PLANNING', 'IN_PROGRESS']:
        robot = db.query(models.Robot).filter(models.Robot.id == db_request.robot_id).first()
        if robot:
            robot.status = 'IDLE'
    
    db.delete(db_request)
    db.commit()
    return db_request
