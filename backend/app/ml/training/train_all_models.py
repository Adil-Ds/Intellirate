"""
Train all ML models locally and save them to ml-models directory
Usage: python train_all_models.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
import logging

from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from prophet import Prophet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_abuse_training_data(n_samples=10000):
    """Generate synthetic data for abuse detection"""
    logger.info(f"Generating {n_samples} samples for abuse detection...")
    
    np.random.seed(42)
    
    # Normal behavior (80%)
    normal_size = int(n_samples * 0.8)
    normal_data = {
        'requests_per_minute': np.random.normal(50, 15, normal_size).clip(0, 200),
        'unique_endpoints_accessed': np.random.normal(5, 2, normal_size).clip(1, 20),
        'error_rate_percentage': np.random.normal(2, 1, normal_size).clip(0, 10),
        'request_timing_patterns': np.random.beta(5, 2, normal_size),  # Consistent patterns
        'ip_reputation_score': np.random.beta(8, 2, normal_size),  # Good reputation
        'endpoint_diversity_score': np.random.beta(3, 5, normal_size)  # Low diversity
    }
    
    # Abusive behavior (20%)
    abusive_size = n_samples - normal_size
    abusive_data = {
        'requests_per_minute': np.random.normal(200, 50, abusive_size).clip(100, 500),
        'unique_endpoints_accessed': np.random.normal(15, 5, abusive_size).clip(10, 50),
        'error_rate_percentage': np.random.normal(25, 10, abusive_size).clip(10, 80),
        'request_timing_patterns': np.random.beta(2, 5, abusive_size),  # Inconsistent
        'ip_reputation_score': np.random.beta(2, 8, abusive_size),  # Bad reputation
        'endpoint_diversity_score': np.random.beta(6, 2, abusive_size)  # High diversity
    }
    
    # Combine
    data = pd.DataFrame({
        key: np.concatenate([normal_data[key], abusive_data[key]])
        for key in normal_data.keys()
    })
    
    return data


def train_isolation_forest(data):
    """Train Isolation Forest for abuse detection"""
    logger.info("Training Isolation Forest model...")
    
    # Split data for validation
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
    
    model = IsolationForest(
        contamination=0.2,  # Expected 20% anomalies
        n_estimators=50,    # Reduced from 100 to prevent overfitting
        max_samples=128,    # Reduced from 256
        random_state=42
    )
    
    model.fit(train_data)
    
    # Evaluate on TEST set (not training set)
    test_predictions = model.predict(test_data)
    
    # Calculate metrics using known labels from test data generation
    n_normal_test = int(len(test_data) * 0.8)
    true_labels = np.concatenate([np.ones(n_normal_test), -np.ones(len(test_data) - n_normal_test)])
    
    precision = precision_score(true_labels, test_predictions, pos_label=-1, zero_division=0)
    recall = recall_score(true_labels, test_predictions, pos_label=-1, zero_division=0)
    
    logger.info(f"✓ Isolation Forest trained.")
    logger.info(f"  - Test Precision: {precision:.3f}")
    logger.info(f"  - Test Recall: {recall:.3f}")
    
    return model, precision, recall


def generate_rate_limit_training_data(n_samples=5000):
    """Generate synthetic data for rate limit optimization"""
    logger.info(f"Generating {n_samples} samples for rate limit optimization...")
    
    np.random.seed(42)
    
    data = []
    
    for _ in range(n_samples):
        tier = np.random.choice([0, 1, 2])  # free, premium, enterprise
        
        if tier == 0:  # Free
            base_limit = 60
            avg_requests = np.clip(np.random.normal(40, 10), 10, 80)
            consistency = np.random.beta(3, 5)
        elif tier == 1:  # Premium
            base_limit = 150
            avg_requests = np.clip(np.random.normal(100, 30), 50, 200)
            consistency = np.random.beta(5, 3)
        else:  # Enterprise
            base_limit = 500
            avg_requests = np.clip(np.random.normal(300, 100), 100, 600)
            consistency = np.random.beta(7, 2)
        
        # Add some variation based on behavior
        adjustment = consistency * 1.5 + np.random.normal(0, 0.1)
        optimal_limit = base_limit * adjustment
        
        data.append({
            'user_tier': tier,
            'historical_avg_requests': avg_requests,
            'behavioral_consistency': consistency,
            'endpoint_usage_patterns': np.random.beta(4, 4),
            'time_of_day_patterns': np.random.beta(4, 4),
            'burst_frequency': np.random.beta(3, 5),
            'optimal_limit': optimal_limit
        })
    
    return pd.DataFrame(data)


def train_xgboost(data):
    """Train XGBoost for rate limit optimization"""
    logger.info("Training XGBoost model...")
    
    X = data.drop('optimal_limit', axis=1)
    y = data['optimal_limit']
    
    # Split for proper train/test evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = XGBRegressor(
        n_estimators=100,
        max_depth=4,           # Reduced from 6 to prevent overfitting
        learning_rate=0.05,     # Reduced from 0.1 for better generalization
        reg_alpha=0.5,          # L1 regularization
        reg_lambda=1.0,         # L2 regularization
        subsample=0.8,          # Use 80% of data per tree
        colsample_bytree=0.8,   # Use 80% of features per tree
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate on TEST set
    test_predictions = model.predict(X_test)
    train_predictions = model.predict(X_train)
    
    test_mae = np.mean(np.abs(test_predictions - y_test))
    test_r2 = r2_score(y_test, test_predictions)
    train_r2 = r2_score(y_train, train_predictions)
    
    logger.info(f"✓ XGBoost trained.")
    logger.info(f"  - Test R² Score: {test_r2:.3f}")
    logger.info(f"  - Train R² Score: {train_r2:.3f}")
    logger.info(f"  - Test MAE: {test_mae:.2f} requests")
    logger.info(f"  - Overfitting Gap: {(train_r2 - test_r2):.3f}")
    
    return model, test_r2, test_mae


def generate_traffic_training_data(n_days=30):
    """Generate synthetic time-series data for traffic forecasting"""
    logger.info(f"Generating {n_days} days of traffic data...")
    
    np.random.seed(42)
    
    # Generate timestamps (5-minute intervals)
    start_date = datetime.now() - timedelta(days=n_days)
    timestamps = pd.date_range(start=start_date, periods=n_days*288, freq='5min')
    
    # Base traffic with daily and weekly patterns
    t = np.arange(len(timestamps))
    
    # Daily pattern (peak during work hours)
    hour_of_day = timestamps.hour + timestamps.minute / 60
    daily_pattern = 50 + 40 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
    
    # Weekly pattern (lower on weekends)
    weekly_pattern = 1 - 0.3 * (timestamps.dayofweek >= 5).astype(float)
    
    # Trend (slight growth over time)
    trend = 100 + t * 0.01
    
    # Combine patterns with noise
    requests = (trend + daily_pattern) * weekly_pattern + np.random.normal(0, 10, len(timestamps))
    requests = np.clip(requests, 20, 500).astype(int)
    
    data = pd.DataFrame({
        'ds': timestamps,
        'y': requests
    })
    
    return data


def train_prophet(data):
    """Train Prophet for traffic forecasting"""
    logger.info("Training Prophet model...")
    
    # Split for train/test
    train_size = int(len(data) * 0.8)
    train_data = data[:train_size]
    test_data = data[train_size:]
    
    model = Prophet(
        changepoint_prior_scale=0.01,      # Reduced from 0.05 to reduce overfitting
        seasonality_prior_scale=5,         # Reduced from 10
        seasonality_mode='additive',       # Changed from multiplicative for stability
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    
    model.fit(train_data)
    
    # Predict on test set
    test_forecast = model.predict(test_data)
    
    # Calculate MAPE on test data
    test_predictions = test_forecast['yhat'].values
    actual = test_data['y'].values
    mape = np.mean(np.abs((actual - test_predictions) / actual)) * 100
    
    logger.info(f"✓ Prophet trained.")
    logger.info(f"  - Test MAPE: {mape:.2f}%")
    logger.info(f"  - Trend: {test_forecast['trend'].iloc[-1]:.1f}")
    
    return model, mape


def main():
    """Main training pipeline"""
    logger.info("="*60)
    logger.info("Starting ML Model Training Pipeline")
    logger.info("="*60)
    
    # Create output directories
    output_dir = Path("ml-models")
    (output_dir / "isolation_forest").mkdir(parents=True, exist_ok=True)
    (output_dir / "xgboost").mkdir(parents=True, exist_ok=True)
    (output_dir / "prophet").mkdir(parents=True, exist_ok=True)
    
    # Track metrics
    metrics = {}
    
    # 1. Train Isolation Forest
    logger.info("\n[1/3] Isolation Forest for Abuse Detection")
    logger.info("-" * 60)
    abuse_data = generate_abuse_training_data()
    isolation_forest, precision, recall = train_isolation_forest(abuse_data)
    metrics['isolation_forest'] = {'precision': precision, 'recall': recall}
    
    output_path = output_dir / "isolation_forest" / "model_v1.pkl"
    joblib.dump(isolation_forest, output_path)
    logger.info(f"✓ Saved to: {output_path}")
    
    # 2. Train XGBoost
    logger.info("\n[2/3] XGBoost for Rate Limit Optimization")
    logger.info("-" * 60)
    rate_limit_data = generate_rate_limit_training_data()
    xgboost_model, r2, mae = train_xgboost(rate_limit_data)
    metrics['xgboost'] = {'r2_score': r2, 'mae': mae}
    
    output_path = output_dir / "xgboost" / "model_v1.pkl"
    joblib.dump(xgboost_model, output_path)
    logger.info(f"✓ Saved to: {output_path}")
    
    # 3. Train Prophet
    logger.info("\n[3/3] Prophet for Traffic Forecasting")
    logger.info("-" * 60)
    traffic_data = generate_traffic_training_data()
    prophet_model, mape = train_prophet(traffic_data)
    metrics['prophet'] = {'mape': mape}
    
    output_path = output_dir / "prophet" / "model_v1.pkl"
    joblib.dump(prophet_model, output_path)
    logger.info(f"✓ Saved to: {output_path}")
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("✅ ALL MODELS TRAINED SUCCESSFULLY")
    logger.info("="*60)
    logger.info(f"\nModels saved to: {output_dir.absolute()}")
    
    # Print accuracy summary
    logger.info("\n" + "="*60)
    logger.info("📊 MODEL ACCURACY METRICS")
    logger.info("="*60)
    logger.info("\n[1] Isolation Forest (Abuse Detection):")
    logger.info(f"    Precision: {metrics['isolation_forest']['precision']:.1%} - How many detected anomalies are true abuse")
    logger.info(f"    Recall:    {metrics['isolation_forest']['recall']:.1%} - How many actual abuses are detected")
    logger.info("\n[2] XGBoost (Rate Limit Optimization):")
    logger.info(f"    R² Score:  {metrics['xgboost']['r2_score']:.1%} - Variance explained by model")
    logger.info(f"    MAE:       {metrics['xgboost']['mae']:.1f} requests - Average prediction error")
    logger.info("\n[3] Prophet (Traffic Forecasting):")
    logger.info(f"    MAPE:      {metrics['prophet']['mape']:.2f}% - Mean absolute percentage error")
    
    logger.info("\n" + "="*60)
    logger.info("\nNext steps:")
    logger.info("1. Test models locally: python scripts/test_local_models.py")
    logger.info("2. Deploy to AWS: python scripts/deploy_to_aws.py --model all")


if __name__ == "__main__":
    main()
