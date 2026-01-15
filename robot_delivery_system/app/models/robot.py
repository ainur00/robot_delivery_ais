from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    status = Column(Enum('IDLE', 'BUSY', name='robot_status'), default='IDLE')
    current_map_id = Column(Integer, ForeignKey('maps.id'))
    current_position_x = Column(Float, default=0.0)
    current_position_y = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    current_map = relationship("Map", back_populates="robots")
    transport_requests = relationship("TransportRequest", back_populates="robot")