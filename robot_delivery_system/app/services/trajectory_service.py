from sqlalchemy.orm import Session
import json
from app import models
from app.schemas import TrajectoryCreate

# create
def create_trajectory(db: Session, trajectory: TrajectoryCreate):
    """Создание траектории для заявки"""
    # Проверяем, что заявка существует
    request = db.query(models.TransportRequest).filter(
        models.TransportRequest.id == trajectory.request_id
    ).first()
    
    if not request:
        raise ValueError(f"Заявка с ID {trajectory.request_id} не найдена")
    
    # Проверяем, что для этой заявки еще нет траектории
    existing = db.query(models.Trajectory).filter(
        models.Trajectory.request_id == trajectory.request_id
    ).first()
    
    if existing:
        raise ValueError(f"Для заявки {trajectory.request_id} уже существует траектория")
    
    # Преобразуем path_data в JSON строку
    if isinstance(trajectory.path_data, dict) or isinstance(trajectory.path_data, list):
        path_json = json.dumps(trajectory.path_data)
    else:
        path_json = trajectory.path_data
    
    db_trajectory = models.Trajectory(
        request_id=trajectory.request_id,
        path_data=path_json
    )
    
    # Обновляем статус заявки на READY
    request.status = 'READY'
    
    db.add(db_trajectory)
    db.commit()
    db.refresh(db_trajectory)
    return db_trajectory

# read
def get_trajectory_by_request(db: Session, request_id: int):
    """Получение траектории по ID заявки"""
    trajectory = db.query(models.Trajectory).filter(
        models.Trajectory.request_id == request_id
    ).first()
    
    if trajectory and trajectory.path_data:
        try:
            trajectory.path_data = json.loads(trajectory.path_data)
        except:
            pass
    
    return trajectory

def get_trajectory(db: Session, trajectory_id: int):
    """Получение траектории по ID"""
    trajectory = db.query(models.Trajectory).filter(
        models.Trajectory.id == trajectory_id
    ).first()
    
    if trajectory and trajectory.path_data:
        try:
            trajectory.path_data = json.loads(trajectory.path_data)
        except:
            pass
    
    return trajectory

# update
def update_trajectory(db: Session, trajectory_id: int, path_data: dict):
    """Обновление траектории"""
    trajectory = get_trajectory(db, trajectory_id)
    if not trajectory:
        raise ValueError(f"Траектория с ID {trajectory_id} не найдена")
    
    if isinstance(path_data, dict) or isinstance(path_data, list):
        trajectory.path_data = json.dumps(path_data)
    else:
        trajectory.path_data = path_data
    
    db.commit()
    db.refresh(trajectory)
    return trajectory

# delete
def delete_trajectory(db: Session, trajectory_id: int):
    """Удаление траектории по ID"""
    trajectory = get_trajectory(db, trajectory_id)
    if not trajectory:
        raise ValueError(f"Траектория с ID {trajectory_id} не найдена")
    
    db.delete(trajectory)
    db.commit()
    return trajectory
