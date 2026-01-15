from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models
from app.schemas import RobotCreate, RobotUpdate

# create
def create_robot(db: Session, robot: RobotCreate):
    """Создание нового робота"""
    db_robot = models.Robot(
        name=robot.name,
        current_map_id=robot.current_map_id if hasattr(robot, 'current_map_id') else None,
        current_position_x=robot.current_position_x if hasattr(robot, 'current_position_x') else 0.0,
        current_position_y=robot.current_position_y if hasattr(robot, 'current_position_y') else 0.0,
        status=robot.status if hasattr(robot, 'status') else 'IDLE'
    )
    db.add(db_robot)
    db.commit()
    db.refresh(db_robot)
    return db_robot

# read
def get_robot(db: Session, robot_id: int):
    """Получение робота по ID"""
    return db.query(models.Robot).filter(models.Robot.id == robot_id).first()

def get_all_robots(db: Session, skip: int = 0, limit: int = 100):
    """Получение списка роботов"""
    return db.query(models.Robot).offset(skip).limit(limit).all()

def get_available_robots(db: Session):
    """Получение доступных роботов (IDLE)"""
    return db.query(models.Robot).filter(models.Robot.status == 'IDLE').all()

# update
def update_robot(db: Session, robot_id: int, robot_update: RobotUpdate):
    """Обновление данных робота"""
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        raise ValueError(f"Робот с ID {robot_id} не найден")
    
    update_data = robot_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_robot, key, value)
    
    db.commit()
    db.refresh(db_robot)
    return db_robot

def update_robot_position(db: Session, robot_id: int, x: float, y: float):
    """Обновление позиции робота"""
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        raise ValueError(f"Робот с ID {robot_id} не найден")
    
    db_robot.current_position_x = x
    db_robot.current_position_y = y
    db.commit()
    db.refresh(db_robot)
    return db_robot

def update_robot_status(db: Session, robot_id: int, status: str):
    """Обновление статуса робота"""
    valid_statuses = ['IDLE', 'BUSY']
    if status not in valid_statuses:
        raise ValueError(f"Неверный статус. Допустимые: {valid_statuses}")
    
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        raise ValueError(f"Робот с ID {robot_id} не найден")
    
    db_robot.status = status
    db.commit()
    db.refresh(db_robot)
    return db_robot

# delete
def delete_robot(db: Session, robot_id: int):
    """Удаление робота (только если нет активных заявок)"""
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        raise ValueError(f"Робот с ID {robot_id} не найден")
    
    # Проверяем, есть ли у робота активные заявки
    active_requests = db.query(models.TransportRequest).filter(
        models.TransportRequest.robot_id == robot_id,
        models.TransportRequest.status.in_(['PENDING', 'PLANNING', 'IN_PROGRESS'])
    ).first()
    
    if active_requests:
        raise ValueError(f"Невозможно удалить робота {robot_id}: есть активные заявки")
    
    db.delete(db_robot)
    db.commit()
    return db_robot
