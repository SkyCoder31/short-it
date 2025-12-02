from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: One URL has many click events
    click_events = relationship("Click", back_populates="url_obj")

class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Store basic request info
    client_ip = Column(String, default="Unknown")
    user_agent = Column(String, default="Unknown")

    # Foreign Key: Links this click to a specific URL
    url_key = Column(String, ForeignKey("urls.key"))
    
    # Relationship: Link back to the URL object
    url_obj = relationship("URL", back_populates="click_events")