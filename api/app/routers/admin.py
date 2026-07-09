from fastapi import APIRouter, Depends
from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, require_admin
from app.models.agent import Agent
from app.models.command import Command
from app.models.user import User
from app.schemas.admin import UserSummary
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users = await db.execute(select(User).order_by(User.created_at))
    result = []
    for u in users.scalars().all():
        agent_ids = select(Agent.id).where(Agent.user_id == u.id).subquery()

        cmd_count = await db.scalar(
            select(func.count(Command.id)).where(Command.agent_id.in_(agent_ids))
        ) or 0

        input_total = await db.scalar(
            select(func.coalesce(func.sum(Command.input_tokens), 0)).where(Command.agent_id.in_(agent_ids))
        ) or 0

        output_total = await db.scalar(
            select(func.coalesce(func.sum(Command.output_tokens), 0)).where(Command.agent_id.in_(agent_ids))
        ) or 0

        saved_total = await db.scalar(
            select(func.coalesce(func.sum(Command.saved_tokens), 0)).where(Command.agent_id.in_(agent_ids))
        ) or 0

        exec_time_total = await db.scalar(
            select(func.coalesce(func.sum(Command.exec_time_ms), 0)).where(Command.agent_id.in_(agent_ids))
        ) or 0

        savings_pct = (saved_total / input_total * 100) if input_total > 0 else 0.0

        result.append(UserSummary(
            user_id=u.id,
            email=u.email,
            name=u.name,
            total_commands=cmd_count,
            total_input_tokens=input_total,
            total_output_tokens=output_total,
            total_saved_tokens=saved_total,
            total_exec_time=exec_time_total,
            savings_pct=round(savings_pct, 1),
        ))
    return result
