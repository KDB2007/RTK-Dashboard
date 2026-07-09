from datetime import datetime

from pydantic import BaseModel


class RegisterAgentRequest(BaseModel):
    name: str
    os: str = ""
    rtk_version: str = ""


class RegisterAgentResponse(BaseModel):
    agent_id: str
    api_key: str


class AgentResponse(BaseModel):
    id: str
    name: str
    os: str
    rtk_version: str
    last_sync_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
