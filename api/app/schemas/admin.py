from pydantic import BaseModel


class UserSummary(BaseModel):
    user_id: str
    email: str
    name: str
    total_commands: int
    total_input_tokens: int
    total_output_tokens: int
    total_saved_tokens: int
    total_exec_time: int
    savings_pct: float
