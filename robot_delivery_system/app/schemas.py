# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Robot schemas
class RobotBase(BaseModel):
    name: str
    current_map_id: int
    status: str = "IDLE"

class RobotCreate(RobotBase):
    pass

class RobotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    current_map_id: Optional[int] = None
    current_position_x: Optional[float] = None
    current_position_y: Optional[float] = None

class Robot(RobotBase):
    id: int
    created_at: datetime
    current_position_x: Optional[float] = None
    current_position_y: Optional[float] = None
    
    class Config:
        from_attributes = True

# Map schemas
class MapBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None

class MapCreate(MapBase):
    pass

class Map(MapBase):
    id: int
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# TransportRequest schemas
class TransportRequestBase(BaseModel):
    user_id: int
    robot_id: int
    target_x: float
    target_y: float

class TransportRequestCreate(TransportRequestBase):
    pass

class TransportRequest(TransportRequestBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Trajectory schemas
class TrajectoryBase(BaseModel):
    request_id: int
    path_data: str  # JSON string

class TrajectoryCreate(TrajectoryBase):
    pass

class Trajectory(TrajectoryBase):
    id: int
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    request_id: int
    command: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    executed_at: datetime
    
    class Config:
        from_attributes = True