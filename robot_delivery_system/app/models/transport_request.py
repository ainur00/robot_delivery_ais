from sqlalchemy import Column, Integer, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TransportRequest(Base):
    __tablename__ = "transport_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    robot_id = Column(Integer, ForeignKey('robots.id'))
    target_x = Column(Float, nullable=False)
    target_y = Column(Float, nullable=False)
    status = Column(
        Enum('PENDING', 'PLANNING', 'READY', 'IN_PROGRESS', 'COMPLETED', 'FAILED', name='request_status'),
        default='PENDING'
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="transport_requests")
    robot = relationship("Robot", back_populates="transport_requests")
    trajectory = relationship("Trajectory", back_populates="request", uselist=False)