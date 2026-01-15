from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import TransportRequest, TransportRequestCreate
from app.services.transport_request_service import (
    create_transport_request, get_transport_request, 
    get_user_requests, update_request_status
)
from app.services.robot_service import update_robot_status

router = APIRouter(prefix="/requests", tags=["transport_requests"])


@router.post("/", response_model=TransportRequest, status_code=status.HTTP_201_CREATED)
def create_request(request: TransportRequestCreate, db: Session = Depends(get_db)):
    """Создание новой заявки на перевозку"""
    # user_id передается в теле запроса
    try:
        # Создаем заявку
        transport_request = create_transport_request(db, request)
        
        # Автоматически занимаем робота
        update_robot_status(db, request.robot_id, "BUSY")
        
        return transport_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TransportRequest])
def get_all_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка всех заявок"""
    from app import models
    
    return db.query(models.TransportRequest).offset(skip).limit(limit).all()

@router.get("/user/{user_id}", response_model=List[TransportRequest])
def read_user_requests(user_id: int, db: Session = Depends(get_db)):
    """Получение заявок пользователя по его ID"""
    return get_user_requests(db, user_id)

@router.get("/{request_id}", response_model=TransportRequest)
def read_request(request_id: int, db: Session = Depends(get_db)):
    """Получение заявки по ID"""
    request = get_transport_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return request

@router.patch("/{request_id}/status", response_model=TransportRequest)
def update_status(request_id: int, status: str, db: Session = Depends(get_db)):
    """Обновление статуса заявки (для пользователя и планировщика)"""
    try:
        return update_request_status(db, request_id, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{request_id}/accept", response_model=TransportRequest)
def accept_request(request_id: int, db: Session = Depends(get_db)):
    """Принятие траектории и начало выполнения (IN_PROGRESS)"""
    request = get_transport_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Проверяем, что заявка в состоянии READY
    if request.status != 'READY':
        raise HTTPException(
            status_code=400, 
            detail=f"Заявка должна быть в состоянии READY, а не {request.status}"
        )
    
    try:
        return update_request_status(db, request_id, 'IN_PROGRESS')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{request_id}/reject", response_model=TransportRequest)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    """Отклонение траектории (FAILED)"""
    request = get_transport_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Проверяем, что заявка в состоянии READY
    if request.status != 'READY':
        raise HTTPException(
            status_code=400, 
            detail=f"Заявку можно отклонить только в состоянии READY, а не {request.status}"
        )
    
    try:
        # Обновляем статус на FAILED
        updated_request = update_request_status(db, request_id, 'FAILED')
        
        # Освобождаем робота
        update_robot_status(db, request.robot_id, "IDLE")
        
        return updated_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{request_id}/complete", response_model=TransportRequest)
def complete_request(request_id: int, db: Session = Depends(get_db)):
    """Завершение заявки (COMPLETED) - для эмулятора"""
    try:
        # Обновляем статус на COMPLETED
        updated_request = update_request_status(db, request_id, 'COMPLETED')
        
        # Освобождаем робота
        update_robot_status(db, updated_request.robot_id, "IDLE")
        
        return updated_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
