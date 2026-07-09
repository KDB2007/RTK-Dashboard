from sqlalchemy import Column, DateTime, ForeignKey, String, func

from app.models.base import Base, gen_uuid


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    status = Column(String, default="pending")
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
