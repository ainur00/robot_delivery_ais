from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import Robot, RobotBase, Map
from app.services.robot_service import (
    get_all_robots, get_available_robots, 
    update_robot_status, update_robot_position,
    create_robot
)

import os

router = APIRouter(prefix="/robots", tags=["robots"])


@router.post("/", response_model=Robot)
def create_new_robot(robot: RobotBase, db: Session = Depends(get_db)):
    """Создание нового робота"""
    try:
        return create_robot(db, robot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Robot])
def read_robots(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Получение списка всех роботов"""
    return get_all_robots(db, skip=skip, limit=limit)


@router.get("/available", response_model=List[Robot])
def read_available_robots(db: Session = Depends(get_db)):
    """Получение списка доступных (IDLE) роботов"""
    return get_available_robots(db)

@router.get("/{robot_id}", response_model=Robot)
def read_robot(robot_id: int, db: Session = Depends(get_db)):
    """Получение робота по ID"""
    from app.services.robot_service import get_robot
    
    robot = get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Робот не найден")
    return robot

@router.get("/{robot_id}/map", response_model=Map)
def get_robot_map(robot_id: int, db: Session = Depends(get_db)):
    """Получение карты робота по его ID"""
    from app.services.robot_service import get_robot
    robot = get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Робот не найден")
    
    if not robot.current_map_id:
        raise HTTPException(status_code=404, detail="У робота нет назначенной карты")
    
    from app.services.map_service import get_map
    map_obj = get_map(db, robot.current_map_id)
    if not map_obj:
        raise HTTPException(status_code=404, detail="Карта не найдена")
    
    return map_obj

@router.get("/{robot_id}/map/image")
def get_robot_map_image(robot_id: int, db: Session = Depends(get_db)):
    """Получение файла карты робота"""
    from app.services.robot_service import get_robot
    robot = get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Робот не найден")
    
    if not robot.current_map_id:
        raise HTTPException(status_code=404, detail="У робота нет назначенной карты")
    
    from app.services.map_service import get_map
    map_obj = get_map(db, robot.current_map_id)
    if not map_obj:
        raise HTTPException(status_code=404, detail="Карта не найдена")
    
    # Проверяем существование файла
    if not os.path.exists(map_obj.file_path):
        raise HTTPException(status_code=404, detail="Файл карты не найден")
    
    # Отдаём файл как изображение PNG
    return FileResponse(
        map_obj.file_path,
        media_type="image/png",
        filename=f"map_{map_obj.id}.png"
    )

@router.patch("/{robot_id}/occupy", response_model=Robot)
def occupy_robot(robot_id: int, db: Session = Depends(get_db)):
    """Занять робота (сделать BUSY)"""
    try:
        return update_robot_status(db, robot_id, "BUSY")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{robot_id}/position", response_model=Robot)
def update_robot_position_endpoint(robot_id: int, x: float, y: float, db: Session = Depends(get_db)):
    """Обновление позиции робота (для эмулятора)"""
    try:
        return update_robot_position(db, robot_id, x, y)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))