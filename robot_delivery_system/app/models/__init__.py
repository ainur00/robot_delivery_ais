from app.database import Base
from .robot import Robot
from .map import Map
from .user import User
from .transport_request import TransportRequest
from .trajectory import Trajectory

# Экспортируем Base и все модели
__all__ = [
    'Base',
    'Robot',
    'Map', 
    'User',
    'TransportRequest',
    'Trajectory'
    'Test'
]