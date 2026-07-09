from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.agent import Agent
from app.models.command import Command
from app.models.user import User
from app.schemas.dashboard import CommandBreakdown, CommandRecord, SummaryResponse, TrendPoint

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def _resolve_user_id(user: User, target: str | None) -> str:
    if target is None or target == user.id:
        return user.id
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return target


@router.get("/summary")
async def summary(
    user_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = await _resolve_user_id(user, user_id)
    agent_ids = select(Agent.id).where(Agent.user_id == uid).subquery()

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

    machine_count = await db.scalar(
        select(func.count(Agent.id)).where(Agent.user_id == uid)
    ) or 0

    five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    active = await db.scalar(
        select(func.count(Agent.id)).where(
            Agent.user_id == uid,
            Agent.last_sync_at >= five_min_ago,
        )
    ) or 0

    savings_pct = (saved_total / input_total * 100) if input_total > 0 else 0.0

    return SummaryResponse(
        total_commands=cmd_count,
        total_input_tokens=input_total,
        total_output_tokens=output_total,
        total_saved_tokens=saved_total,
        total_exec_time=exec_time_total,
        savings_pct=round(savings_pct, 1),
        machine_count=machine_count,
        active_machines=active,
    )


@router.get("/commands")
async def command_breakdown(
    user_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = await _resolve_user_id(user, user_id)
    agent_ids = select(Agent.id).where(Agent.user_id == uid).subquery()


    rest = func.substr(Command.rtk_cmd, 5)
    space = func.instr(rest, ' ')
    first_word = func.substr(rest, 1, func.nullif(space, 0) - 1)
    first_word = func.coalesce(first_word, rest)

    rows = await db.execute(
        select(
            first_word.label("cmd_type"),
            func.count(Command.id).label("count"),
            func.sum(Command.input_tokens).label("input_total"),
            func.sum(Command.output_tokens).label("output_total"),
            func.sum(Command.saved_tokens).label("saved"),
            (cast(func.sum(Command.saved_tokens), Float) / func.nullif(func.sum(Command.input_tokens), 0) * 100).label("pct"),
        )
        .where(Command.agent_id.in_(agent_ids))
        .group_by(first_word)
        .order_by(func.sum(Command.saved_tokens).desc())
        .limit(20)
    )

    result = []
    for row in rows:
        result.append(CommandBreakdown(
            cmd_type=(row.cmd_type or "other").strip().rstrip(':'),
            count=row.count,
            input_tokens=row.input_total or 0,
            output_tokens=row.output_total or 0,
            saved_tokens=row.saved or 0,
            savings_pct=round(row.pct, 1) if row.pct else 0.0,
        ))
    return result


@router.get("/history")
async def command_history(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = await _resolve_user_id(user, user_id)
    agent_ids = select(Agent.id).where(Agent.user_id == uid).subquery()

    rows = await db.execute(
        select(Command)
        .where(Command.agent_id.in_(agent_ids))
        .order_by(Command.ran_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return [CommandRecord.model_validate(r) for r in rows.scalars().all()]


@router.get("/trends")
async def trends(
    days: int = Query(default=30, le=90),
    user_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = await _resolve_user_id(user, user_id)
    agent_ids = select(Agent.id).where(Agent.user_id == uid).subquery()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = await db.execute(
        select(
            func.date(Command.ran_at).label("day"),
            func.count(Command.id).label("count"),
            func.sum(Command.saved_tokens).label("saved"),
            (cast(func.sum(Command.saved_tokens), Float) / func.nullif(func.sum(Command.input_tokens), 0) * 100).label("pct"),
        )
        .where(Command.agent_id.in_(agent_ids), Command.ran_at >= since)
        .group_by(func.date(Command.ran_at))
        .order_by(func.date(Command.ran_at))
    )

    result = []
    for row in rows:
        result.append(TrendPoint(
            date=str(row.day),
            commands=row.count,
            saved_tokens=row.saved,
            savings_pct=round(row.pct, 1) if row.pct else 0.0,
        ))
    return result
