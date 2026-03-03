from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DonationBase(BaseModel):
    full_amount: int = Field(..., gt=0)
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    model_config = ConfigDict(extra="forbid")


class DonationDB(DonationBase):
    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationBase):
    id: int
    create_date: datetime
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
