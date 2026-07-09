from datetime import datetime

from pydantic import BaseModel


class CommandUpload(BaseModel):
    original_cmd: str
    rtk_cmd: str
    input_tokens: int
    output_tokens: int
    saved_tokens: int
    savings_pct: float
    exec_time_ms: int = 0
    project_path: str = ""
    ran_at: datetime


class BatchUploadRequest(BaseModel):
    commands: list[CommandUpload]


class BatchUploadResponse(BaseModel):
    synced_count: int
    cursor: int
