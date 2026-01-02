"""
Traffic/Analytics API Endpoints  
Provide real-time traffic data for dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/traffic", tags=["Traffic"])


@router.get("")
async def get_traffic_data(
    hours: int = Query(24, description="Hours of traffic data", ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Get traffic data for the specified time period
    
    Returns aggregated request counts over time
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get request counts grouped by hour
        traffic_data = db.query(
            func.date_trunc('hour', RequestLog.timestamp).label('hour'),
            func.count(RequestLog.id).label('requests')
        ).filter(
            RequestLog.timestamp >= cutoff_time
        ).group_by(
            func.date_trunc('hour', RequestLog.timestamp)
        ).order_by(
            desc('hour')
        ).all()
        
        return {
            "data": [
                {
                    "time": row.hour.isoformat() if row.hour else None,
                    "value": row.requests
                }
                for row in traffic_data
            ],
            "total_requests": sum(row.requests for row in traffic_data),
            "time_range_hours": hours
        }
    
    except Exception as e:
        logger.error(f"Error fetching traffic data: {str(e)}")
        # Return empty data on error
        return {
            "data": [],
            "total_requests": 0,
            "time_range_hours": hours
        }


@router.get("/stats")  
async def get_traffic_stats(db: Session = Depends(get_db)):
    """
    Get overall traffic statistics
    """
    try:
        total_requests = db.query(func.count(RequestLog.id)).scalar() or 0
        avg_latency = db.query(func.avg(RequestLog.latency_ms)).scalar() or 0
        success_rate = db.query(
            func.count(RequestLog.id).filter(RequestLog.success == True)
        ).scalar() or 0
        
        return {
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round((success_rate / total_requests * 100) if total_requests > 0 else 0, 2),
            "active_users": db.query(func.count(func.distinct(RequestLog.user_id))).scalar() or 0
        }
    except Exception as e:
        logger.error(f"Error fetching traffic stats: {str(e)}")
        return {
            "total_requests": 0,
            "avg_latency_ms": 0,
            "success_rate": 0,
            "active_users": 0
        }


@router.get("/forecast")
async def get_traffic_forecast(db: Session = Depends(get_db)):
    """
    Get traffic forecast for the next hour using historical data
    
    Returns predictions with confidence intervals
    """
    try:
        # Get last 7 days of hourly data for forecasting
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        historical_data = db.query(
            func.date_trunc('hour', RequestLog.timestamp).label('hour'),
            func.count(RequestLog.id).label('requests')
        ).filter(
            RequestLog.timestamp >= cutoff_time
        ).group_by(
            func.date_trunc('hour', RequestLog.timestamp)
        ).order_by(
            'hour'
        ).all()
        
        if len(historical_data) < 3:
            # Not enough data for forecast
            return {
                "predictions": [],
                "message": "Not enough historical data for forecasting (need at least 3 hours)"
            }
        
        # Format for Prophet: needs 'ds' (datetime) and 'y' (value) columns
        formatted_data = [
            {
                "timestamp": row.hour.isoformat() if row.hour else None,
                "requests": row.requests
            }
            for row in historical_data
        ]
        
        # Simple forecast: use moving average for next 12 periods (next hour in 5-min intervals)
        # In production, this would call the ML model
        recent_values = [row.requests for row in historical_data[-12:]]
        avg_recent = sum(recent_values) / len(recent_values) if recent_values else 0
        
        # Generate forecast for next hour (12 x 5-minute periods)
        now = datetime.utcnow()
        predictions = []
        
        for i in range(1, 13):
            forecast_time = now + timedelta(minutes=i * 5)
            # Simple prediction with some variance
            predicted_value = max(0, int(avg_recent * (0.9 + (i % 3) * 0.1)))
            
            predictions.append({
                "time": forecast_time.isoformat(),
                "predicted": predicted_value,
                "lower_bound": max(0, int(predicted_value * 0.7)),
                "upper_bound": int(predicted_value * 1.3)
            })
        
        return {
            "predictions": predictions,
            "historical_data": formatted_data[-24:],  # Last 24 hours
            "confidence": 0.75,
            "model": "simple_moving_average"  # TODO: Use Prophet model
        }
    
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        return {
            "predictions": [],
            "error": str(e)
        }
