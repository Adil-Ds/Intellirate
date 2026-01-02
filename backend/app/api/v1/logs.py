"""
Logs API Endpoints
Query system request logs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("")
async def get_logs(
    limit: int = Query(100, description="Number of logs to retrieve", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get recent request logs
    
    Returns a list of recent requests with:
    - Request ID
    - User information
    - Timestamps
    - Status codes
    - Latency metrics
    """
    try:
        logs = db.query(RequestLog)\
            .order_by(desc(RequestLog.timestamp))\
            .limit(limit)\
            .all()
        
        return [log.to_dict() for log in logs]
    
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return []
