from datetime import datetime

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_commands: int
    total_input_tokens: int
    total_output_tokens: int
    total_saved_tokens: int
    total_exec_time: int
    savings_pct: float
    machine_count: int
    active_machines: int


class CommandBreakdown(BaseModel):
    cmd_type: str
    count: int
    input_tokens: int
    output_tokens: int
    saved_tokens: int
    savings_pct: float


class TrendPoint(BaseModel):
    date: str
    commands: int
    saved_tokens: int
    savings_pct: float


class CommandRecord(BaseModel):
    id: int
    original_cmd: str
    rtk_cmd: str
    input_tokens: int
    output_tokens: int
    saved_tokens: int
    savings_pct: float
    exec_time_ms: int
    ran_at: datetime

    class Config:
        from_attributes = True
