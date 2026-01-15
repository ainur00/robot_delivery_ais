from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('transport_requests.id'), unique=True)
    path_data = Column(String(10000))  # JSON с координатами траектории
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    request = relationship("TransportRequest", back_populates="trajectory")