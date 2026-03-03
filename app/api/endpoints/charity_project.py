from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.models import CharityProject, Donation
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investment import investing_process
from app.api.validators import (
    check_name_duplicate,
    check_project_exists,
    check_project_not_closed,
    check_project_not_invested,
    check_full_amount_not_less_invested
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
    summary="Get All Charity Projects",
    description="Показать список всех целевых проектов.",
    tags=["charity_projects"]
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session)
):
    projects = await session.execute(
        select(CharityProject)
    )
    return projects.scalars().all()


@router.post(
    "/",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary="Create Charity Project",
    description="Создать целевой проект.",
    tags=["charity_projects"]
)
async def create_charity_project(
        project_data: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    await check_name_duplicate(project_data.name, session)

    new_project = CharityProject(
        name=project_data.name,
        description=project_data.description,
        full_amount=project_data.full_amount
    )

    session.add(new_project)
    await session.flush()

    await investing_process(new_project, session)

    await session.refresh(new_project)
    return new_project


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    summary="Update Charity Project",
    description="Редактировать целевой проект.",
    tags=["charity_projects"]
)
async def update_charity_project(
        project_id: int,
        project_data: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    project = await check_project_exists(project_id, session)
    await check_project_not_closed(project)

    if project_data.name is not None and project_data.name != project.name:
        await check_name_duplicate(project_data.name, session)

    if project_data.full_amount is not None:
        await check_full_amount_not_less_invested(project_data.full_amount, project)

    for field, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    
    # Проверяем, не закрылся ли проект после обновления full_amount
    if project.full_amount <= project.invested_amount:
        project.fully_invested = True
        project.close_date = project.create_date

    await session.commit()
    await session.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    summary="Delete Charity Project",
    description="Удалить целевой проект.",
    tags=["charity_projects"]
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await check_project_exists(project_id, session)
    await check_project_not_invested(project)

    await session.delete(project)
    await session.commit()

    return project
