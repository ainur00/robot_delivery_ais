from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key = true, index = true)
    name = Column(String(100), nullable = false)
    group = Column(String(100))