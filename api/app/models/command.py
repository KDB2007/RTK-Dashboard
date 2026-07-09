from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.models.base import Base, gen_uuid


class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    original_cmd = Column(Text, nullable=False)
    rtk_cmd = Column(Text, nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    saved_tokens = Column(Integer, nullable=False)
    savings_pct = Column(Float, nullable=False)
    exec_time_ms = Column(Integer, default=0)
    project_path = Column(String, default="")
    ran_at = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
