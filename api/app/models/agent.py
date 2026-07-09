from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, gen_uuid


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    api_key_hash = Column(String, nullable=False)
    os = Column(String, default="")
    rtk_version = Column(String, default="")
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="agents")
