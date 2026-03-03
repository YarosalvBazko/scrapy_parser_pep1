from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.models import Donation
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import investing_process

router = APIRouter()


@router.get(
    "/",
    response_model=list[DonationFullInfoDB],
    summary="Get All Donations",
    description="Показать список всех пожертвований.",
    tags=["donations"]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session)
):
    donations = await session.execute(
        select(Donation)
    )
    return donations.scalars().all()


@router.post(
    "/",
    response_model=DonationDB,
    response_model_exclude_none=True,
    summary="Create Donation",
    description="Создать пожертвование.",
    tags=["donations"]
)
async def create_donation(
        donation_data: DonationCreate,
        session: AsyncSession = Depends(get_async_session)
):
    new_donation = Donation(
        full_amount=donation_data.full_amount,
        comment=donation_data.comment
    )

    session.add(new_donation)
    await session.flush()

    await investing_process(new_donation, session)

    await session.refresh(new_donation)
    return new_donation
