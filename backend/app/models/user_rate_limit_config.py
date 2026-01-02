"""
User Rate Limit Configuration Model
Stores custom rate limits set by admins
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UserRateLimitConfig(Base):
    """Model for storing custom user rate limit configurations"""
    
    __tablename__ = "user_rate_limit_configs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Rate Limit Configuration
    tier = Column(String(50), nullable=False)  # free, pro, enterprise
    custom_limit = Column(Integer, nullable=False)  # requests per month
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserRateLimitConfig {self.user_id} - Tier: {self.tier}, Limit: {self.custom_limit}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier,
            "custom_limit": self.custom_limit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
