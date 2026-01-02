from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ModelMetrics(Base):
    """
    Store ML model performance metrics over time.
    
    Tracks metrics for Prophet, XGBoost, and Isolation Forest models,
    enabling version comparison and historical analysis.
    """
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False, index=True)  # 'prophet', 'xgboost', 'isolation_forest'
    version = Column(String, nullable=False)  # 'v1', 'v2', etc.
    metrics_json = Column(JSON, nullable=False)  # Store all metrics as JSON
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ModelMetrics {self.model_name} {self.version}>"
