from sqlalchemy import Column, Integer, Boolean, DateTime

from app.core.db import Base
from datetime import datetime


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    close_date = Column(DateTime)
