from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession
) -> None:
    project = await session.execute(
        select(CharityProject).where(
            CharityProject.name == project_name
        )
    )
    if project.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким именем уже существует!"
        )


async def check_project_exists(
    project_id: int,
    session: AsyncSession
) -> CharityProject:
    project = await session.execute(
        select(CharityProject).where(
            CharityProject.id == project_id
        )
    )
    project = project.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    return project


async def check_project_not_closed(
    project: CharityProject
) -> None:
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!"
        )


async def check_project_not_invested(
    project: CharityProject
) -> None:
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В проект были внесены средства, не подлежит удалению!"
        )


async def check_full_amount_not_less_invested(
    new_full_amount: int,
    project: CharityProject
) -> None:
    if new_full_amount < project.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Нельзя установить значение full_amount "
                "меньше уже вложенной суммы."
            )
        )
