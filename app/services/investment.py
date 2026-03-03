from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def investing_process(
    target: CharityProject | Donation,
    session: AsyncSession
) -> None:
    """
    Распределение инвестиций между проектами и пожертвованиями.
    """
    if isinstance(target, CharityProject):
        donations = await session.execute(
            select(Donation)
            .where(not Donation.fully_invested)
            .where(Donation.invested_amount < Donation.full_amount)
            .order_by(Donation.create_date)
        )
        sources = donations.scalars().all()
        target_type = "project"
    else:
        projects = await session.execute(
            select(CharityProject)
            .where(not CharityProject.fully_invested)
            .where(CharityProject.invested_amount < CharityProject.full_amount)
            .order_by(CharityProject.create_date)
        )
        sources = projects.scalars().all()
        target_type = "donation"

    if not sources:
        return

    if target_type == "project":
        await _invest_from_donations_to_project(target, sources)
    else:
        await _invest_from_donation_to_projects(target, sources)

    await session.commit()


async def _invest_from_donations_to_project(
    project: CharityProject,
    donations: list[Donation]
) -> None:
    """
    Инвестирование из пожертвований в проект.
    """
    remaining_amount = project.full_amount - project.invested_amount

    for donation in donations:
        donation_remaining = donation.full_amount - donation.invested_amount

        if donation_remaining <= remaining_amount:
            project.invested_amount += donation_remaining
            donation.invested_amount += donation_remaining
            remaining_amount -= donation_remaining
            donation.fully_invested = True
            donation.close_date = donation.create_date
        else:
            project.invested_amount += remaining_amount
            donation.invested_amount += remaining_amount
            remaining_amount = 0

        if remaining_amount == 0:
            project.fully_invested = True
            project.close_date = project.create_date
            break

    if remaining_amount == 0:
        project.fully_invested = True
        project.close_date = project.create_date


async def _invest_from_donation_to_projects(
    donation: Donation,
    projects: list[CharityProject]
) -> None:
    """
    Инвестирование из пожертвования в проекты.
    """
    remaining_amount = donation.full_amount - donation.invested_amount

    for project in projects:
        project_remaining = project.full_amount - project.invested_amount

        if project_remaining <= remaining_amount:
            project.invested_amount += project_remaining
            donation.invested_amount += project_remaining
            remaining_amount -= project_remaining
            project.fully_invested = True
            project.close_date = project.create_date
        else:
            project.invested_amount += remaining_amount
            donation.invested_amount += remaining_amount
            remaining_amount = 0

        if remaining_amount == 0:
            donation.fully_invested = True
            donation.close_date = donation.create_date
            break

    if remaining_amount == 0:
        donation.fully_invested = True
        donation.close_date = donation.create_date
