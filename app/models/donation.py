from sqlalchemy import Column, Text
from app.models.base import BaseModel


class Donation(BaseModel):
    __tablename__ = 'donation'

    comment = Column(Text)