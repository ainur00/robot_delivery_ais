from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import Trajectory, TrajectoryCreate
from app.services.trajectory_service import (
    create_trajectory, get_trajectory_by_request
)
from app.services.transport_request_service import update_request_status

router = APIRouter(prefix="/trajectories", tags=["trajectories"])


@router.post("/", response_model=Trajectory)
def create_new_trajectory(trajectory: TrajectoryCreate, db: Session = Depends(get_db)):
    """Создание новой траектории (для OCP-планировщика)"""
    try:
        # Создаем траекторию
        new_trajectory = create_trajectory(db, trajectory)
        
        # Обновляем статус заявки на READY
        update_request_status(db, trajectory.request_id, 'READY')
        
        return new_trajectory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/request/{request_id}", response_model=Trajectory)
def read_trajectory_by_request(request_id: int, db: Session = Depends(get_db)):
    """Получение траектории по ID заявки"""
    trajectory = get_trajectory_by_request(db, request_id)
    if not trajectory:
        raise HTTPException(status_code=404, detail="Траектория еще не рассчитана")
    return trajectory
