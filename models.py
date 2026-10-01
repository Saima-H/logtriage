from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from db import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    severity = Column(String, nullable=False, default="unknown")
    suggestion = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)