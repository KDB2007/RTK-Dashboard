from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_agent, get_db
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.command import Command
from app.schemas.command import BatchUploadRequest, BatchUploadResponse

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/batch", status_code=201)
async def batch_upload(
    body: BatchUploadRequest,
    request: Request,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    if len(body.commands) > 500:
        return {"error": "Batch size exceeds 500"}, status.HTTP_400_BAD_REQUEST

    commands = [
        Command(
            agent_id=agent.id,
            original_cmd=c.original_cmd,
            rtk_cmd=c.rtk_cmd,
            input_tokens=c.input_tokens,
            output_tokens=c.output_tokens,
            saved_tokens=c.saved_tokens,
            savings_pct=c.savings_pct,
            exec_time_ms=c.exec_time_ms,
            project_path=c.project_path,
            ran_at=c.ran_at,
        )
        for c in body.commands
    ]
    db.add_all(commands)
    await db.flush()

    agent.last_sync_at = datetime.now(timezone.utc)
    await db.flush()

    result = await db.execute(select(func.max(Command.id)))
    max_id = result.scalar() or 0

    db.add(AuditLog(
        agent_id=agent.id,
        action="agent.sync",
        details={"count": len(commands), "cursor": max_id},
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()

    return BatchUploadResponse(synced_count=len(commands), cursor=max_id)
