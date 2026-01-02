"""
Generate and save training datasets as CSV files
This script generates the same synthetic data used to train the ML models
and saves it to CSV files for inspection and documentation.

Usage: python generate_training_datasets.py
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

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
        'request_timing_patterns': np.random.beta(5, 2, normal_size),
        'ip_reputation_score': np.random.beta(8, 2, normal_size),
        'endpoint_diversity_score': np.random.beta(3, 5, normal_size)
    }
    
    # Abusive behavior (20%)
    abusive_size = n_samples - normal_size
    abusive_data = {
        'requests_per_minute': np.random.normal(200, 50, abusive_size).clip(100, 500),
        'unique_endpoints_accessed': np.random.normal(15, 5, abusive_size).clip(10, 50),
        'error_rate_percentage': np.random.normal(25, 10, abusive_size).clip(10, 80),
        'request_timing_patterns': np.random.beta(2, 5, abusive_size),
        'ip_reputation_score': np.random.beta(2, 8, abusive_size),
        'endpoint_diversity_score': np.random.beta(6, 2, abusive_size)
    }
    
    # Combine
    data = pd.DataFrame({
        key: np.concatenate([normal_data[key], abusive_data[key]])
        for key in normal_data.keys()
    })
    
    # Add label column for clarity
    data['label'] = ['normal'] * normal_size + ['abusive'] * abusive_size
    
    return data


def generate_rate_limit_training_data(n_samples=5000):
    """Generate synthetic data for rate limit optimization"""
    logger.info(f"Generating {n_samples} samples for rate limit optimization...")
    
    np.random.seed(42)
    
    data = []
    tier_names = {0: 'free', 1: 'premium', 2: 'enterprise'}
    
    for _ in range(n_samples):
        tier = np.random.choice([0, 1, 2])
        
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
        
        adjustment = consistency * 1.5 + np.random.normal(0, 0.1)
        optimal_limit = base_limit * adjustment
        
        data.append({
            'user_tier': tier,
            'tier_name': tier_names[tier],
            'base_limit': base_limit,
            'historical_avg_requests': avg_requests,
            'behavioral_consistency': consistency,
            'endpoint_usage_patterns': np.random.beta(4, 4),
            'time_of_day_patterns': np.random.beta(4, 4),
            'burst_frequency': np.random.beta(3, 5),
            'optimal_limit': optimal_limit
        })
    
    return pd.DataFrame(data)


def generate_traffic_training_data(n_days=30):
    """Generate synthetic time-series data for traffic forecasting"""
    logger.info(f"Generating {n_days} days of traffic data...")
    
    np.random.seed(42)
    
    # Generate timestamps (5-minute intervals)
    start_date = datetime.now() - timedelta(days=n_days)
    timestamps = pd.date_range(start=start_date, periods=n_days*288, freq='5min')
    
    # Base traffic with patterns
    t = np.arange(len(timestamps))
    
    # Daily pattern
    hour_of_day = timestamps.hour + timestamps.minute / 60
    daily_pattern = 50 + 40 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
    
    # Weekly pattern
    weekly_pattern = 1 - 0.3 * (timestamps.dayofweek >= 5).astype(float)
    
    # Trend
    trend = 100 + t * 0.01
    
    # Combine with noise
    requests = (trend + daily_pattern) * weekly_pattern + np.random.normal(0, 10, len(timestamps))
    requests = np.clip(requests, 20, 500).astype(int)
    
    data = pd.DataFrame({
        'ds': timestamps,
        'y': requests,
        'hour': timestamps.hour,
        'day_of_week': timestamps.day_name(),
        'is_weekend': (timestamps.dayofweek >= 5).astype(int)
    })
    
    return data


def main():
    """Generate and save all training datasets"""
    logger.info("="*60)
    logger.info("Training Data CSV Generator")
    logger.info("="*60)
    
    # Create output directory
    output_dir = Path("training_data")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Abuse Detection Data
    logger.info("\n[1/3] Generating abuse detection training data...")
    abuse_data = generate_abuse_training_data()
    output_path = output_dir / "abuse_detection_training_data.csv"
    abuse_data.to_csv(output_path, index=False)
    logger.info(f"✓ Saved {len(abuse_data):,} records to: {output_path}")
    logger.info(f"   - Normal: {sum(abuse_data['label'] == 'normal'):,} records")
    logger.info(f"   - Abusive: {sum(abuse_data['label'] == 'abusive'):,} records")
    
    # 2. Rate Limit Optimization Data
    logger.info("\n[2/3] Generating rate limit optimization training data...")
    rate_limit_data = generate_rate_limit_training_data()
    output_path = output_dir / "rate_limit_optimization_training_data.csv"
    rate_limit_data.to_csv(output_path, index=False)
    logger.info(f"✓ Saved {len(rate_limit_data):,} records to: {output_path}")
    logger.info(f"   - Free tier: {sum(rate_limit_data['user_tier'] == 0):,} records")
    logger.info(f"   - Premium tier: {sum(rate_limit_data['user_tier'] == 1):,} records")
    logger.info(f"   - Enterprise tier: {sum(rate_limit_data['user_tier'] == 2):,} records")
    
    # 3. Traffic Forecasting Data
    logger.info("\n[3/3] Generating traffic forecasting training data...")
    traffic_data = generate_traffic_training_data()
    output_path = output_dir / "traffic_forecasting_training_data.csv"
    traffic_data.to_csv(output_path, index=False)
    logger.info(f"✓ Saved {len(traffic_data):,} records to: {output_path}")
    logger.info(f"   - Date range: {traffic_data['ds'].min()} to {traffic_data['ds'].max()}")
    logger.info(f"   - Frequency: 5-minute intervals")
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("✅ ALL TRAINING DATA GENERATED")
    logger.info("="*60)
    logger.info(f"\nFiles saved to: {output_dir.absolute()}")
    logger.info("\nFiles created:")
    logger.info("  1. abuse_detection_training_data.csv")
    logger.info("  2. rate_limit_optimization_training_data.csv")
    logger.info("  3. traffic_forecasting_training_data.csv")
    logger.info("\nYou can now inspect these CSV files in Excel or any data viewer.")


if __name__ == "__main__":
    main()
