from sqlalchemy.orm import Session
from app import models
from app.schemas import MapCreate

# create
def create_map(db: Session, map_data: MapCreate):
    """Создание новой карты"""
    db_map = models.Map(
        name=map_data.name,
        description=map_data.description,
        file_path=map_data.file_path
    )
    db.add(db_map)
    db.commit()
    db.refresh(db_map)
    return db_map

# read
def get_map(db: Session, map_id: int):
    """Получение карты по ID"""
    return db.query(models.Map).filter(models.Map.id == map_id).first()

def get_maps(db: Session, skip: int = 0, limit: int = 100):
    """Получение списка карт"""
    return db.query(models.Map).offset(skip).limit(limit).all()

# update
def update_map(db: Session, map_id: int, map_data: dict):
    """Обновление данных карты"""
    db_map = get_map(db, map_id)
    if not db_map:
        raise ValueError(f"Карта с ID {map_id} не найдена")
    
    for key, value in map_data.items():
        if hasattr(db_map, key):
            setattr(db_map, key, value)
    
    db.commit()
    db.refresh(db_map)
    return db_map

# delete
def delete_map(db: Session, map_id: int):
    """Удаление карты"""
    db_map = get_map(db, map_id)
    if not db_map:
        raise ValueError(f"Карта с ID {map_id} не найдена")
    
    # Проверяем, есть ли роботы на этой карте
    robots_on_map = db.query(models.Robot).filter(
        models.Robot.current_map_id == map_id
    ).first()
    
    if robots_on_map:
        raise ValueError(f"Невозможно удалить карту {map_id}: на ней находятся роботы")
    
    db.delete(db_map)
    db.commit()
    return db_map