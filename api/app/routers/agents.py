from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_agent, get_current_user, get_db
from app.core.security import generate_api_key, hash_api_key
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.agent import AgentResponse, RegisterAgentRequest, RegisterAgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/register", status_code=201)
async def register_agent(
    body: RegisterAgentRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    api_key = generate_api_key()
    agent = Agent(
        user_id=user.id,
        name=body.name,
        api_key_hash=hash_api_key(api_key),
        os=body.os,
        rtk_version=body.rtk_version,
    )
    db.add(agent)
    db.add(AuditLog(
        user_id=user.id,
        agent_id=agent.id,
        action="agent.registered",
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()
    await db.refresh(agent)

    return RegisterAgentResponse(agent_id=agent.id, api_key=api_key)


@router.get("")
async def list_agents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.user_id == user.id).order_by(Agent.created_at.desc()))
    agents = result.scalars().all()
    return [AgentResponse.model_validate(a) for a in agents]


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id, Agent.user_id == user.id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentResponse.model_validate(agent)
