"""
Request Log Model - Captures all traffic for analytics
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class RequestLog(Base):
    """Model for logging all API requests and responses"""
    
    __tablename__ = "request_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Request Identification
    request_id = Column(String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # User Information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255))
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True))
    
    # Request Details
    endpoint = Column(String(100))
    method = Column(String(10), default="POST")
    
    # AI Model Parameters
    model = Column(String(100))
    temperature = Column(Float)
    max_tokens = Column(Integer)
    message_count = Column(Integer)
    
    # Response Details
    status_code = Column(Integer)
    success = Column(Boolean)
    error = Column(Text)
    
    # Token Usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Performance Metrics
    latency_ms = Column(Integer)
    groq_latency_ms = Column(Integer)
    
    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    def __repr__(self):
        return f"<RequestLog {self.request_id} - User: {self.user_id}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "endpoint": self.endpoint,
            "method": self.method,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "message_count": self.message_count,
            "status_code": self.status_code,
            "success": self.success,
            "error": self.error,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "groq_latency_ms": self.groq_latency_ms,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }


# Create indexes for better query performance
Index('idx_user_timestamp', RequestLog.user_id, RequestLog.timestamp)
Index('idx_success_timestamp', RequestLog.success, RequestLog.timestamp)
