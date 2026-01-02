# Chapter: Introduction to Data Science in IntelliRate Gateway

## Abstract

This chapter explores the application of data science principles, methodologies, and techniques within the IntelliRate API Gateway system. We examine how the project leverages statistical analysis, machine learning algorithms, data preprocessing, feature engineering, and predictive modeling to deliver intelligent API management capabilities. The discussion encompasses the complete data science workflow from data collection to model deployment, demonstrating how theoretical concepts translate into practical system features.

---

## 1. Introduction to Data Science in API Systems

### 1.1 What is Data Science?

Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines elements of statistics, mathematics, computer science, and domain expertise to analyze complex data and make data-driven decisions.

The core components of data science include:
- **Data Collection:** Gathering raw data from various sources
- **Data Processing:** Cleaning, transforming, and preparing data
- **Exploratory Analysis:** Understanding data patterns and distributions
- **Statistical Modeling:** Building mathematical representations of data
- **Machine Learning:** Training algorithms to learn patterns from data
- **Visualization:** Communicating insights through visual representations
- **Deployment:** Putting models into production systems

### 1.2 Data Science in IntelliRate

The IntelliRate Gateway exemplifies practical data science application by:

**Anomaly Detection:** Using unsupervised learning to identify unusual API usage patterns that may indicate abuse or security threats.

**Predictive Modeling:** Employing supervised learning to recommend optimal rate limits based on user behavior and historical data.

**Time Series Forecasting:** Applying statistical models to predict future traffic patterns for capacity planning.

**Real-time Analytics:** Processing streaming data to generate actionable insights about system performance and user behavior.

**Feature Engineering:** Transforming raw request data into meaningful features for machine learning models.

### 1.3 The Data Science Lifecycle in IntelliRate

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Data Science Lifecycle                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   [1. Data Collection]                                               │
│         ↓                                                            │
│   [2. Data Preprocessing]                                            │
│         ↓                                                            │
│   [3. Exploratory Data Analysis]                                     │
│         ↓                                                            │
│   [4. Feature Engineering]                                           │
│         ↓                                                            │
│   [5. Model Selection & Training]                                    │
│         ↓                                                            │
│   [6. Model Evaluation]                                              │
│         ↓                                                            │
│   [7. Deployment & Monitoring]                                       │
│         ↓                                                            │
│   [8. Continuous Improvement]                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Collection and Storage

### 2.1 Types of Data in IntelliRate

**Structured Data:**
Data organized in a predefined schema with clear relationships:

```sql
-- Request logs table
CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    user_tier VARCHAR(50),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    model VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms FLOAT,
    status_code INTEGER,
    ip_address VARCHAR(45)
);
```

**Semi-Structured Data:**
JSON payloads with flexible schemas:

```json
{
  "request": {
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "response": {
    "choices": [...],
    "usage": {"prompt_tokens": 50, "completion_tokens": 200}
  }
}
```

**Time-Series Data:**
Temporal measurements for traffic analysis:

```
Timestamp           | Requests | Avg_Latency | Error_Rate
2025-12-30 10:00:00 |    150   |    85.5     |   0.02
2025-12-30 10:01:00 |    165   |    92.3     |   0.01
2025-12-30 10:02:00 |    142   |    78.9     |   0.03
2025-12-30 10:03:00 |    180   |   110.2     |   0.05
```

### 2.2 Data Collection Methods

**Request Logging:**
Every API request is captured with comprehensive metadata:

```python
async def log_request(
    request: Request,
    response: Response,
    user: AuthenticatedUser,
    start_time: float
) -> None:
    """Log request details to database"""
    
    log_entry = RequestLog(
        timestamp=datetime.utcnow(),
        user_id=user.uid,
        user_email=user.email,
        user_tier=user.tier,
        endpoint=request.url.path,
        method=request.method,
        model=request.json().get('model'),
        prompt_tokens=response.json().get('usage', {}).get('prompt_tokens'),
        completion_tokens=response.json().get('usage', {}).get('completion_tokens'),
        latency_ms=(time.time() - start_time) * 1000,
        status_code=response.status_code,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    await db.insert(log_entry)
```

**Aggregation for Analytics:**

```python
async def aggregate_hourly_metrics() -> List[dict]:
    """Aggregate request data into hourly buckets"""
    
    query = """
        SELECT 
            date_trunc('hour', timestamp) as hour,
            COUNT(*) as request_count,
            COUNT(DISTINCT user_id) as unique_users,
            AVG(latency_ms) as avg_latency,
            SUM(total_tokens) as total_tokens,
            SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)::float / COUNT(*) as error_rate
        FROM request_logs
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY date_trunc('hour', timestamp)
        ORDER BY hour
    """
    
    return await db.fetch_all(query)
```

### 2.3 Data Volume and Velocity

**Storage Considerations:**

| Data Type | Volume/Day | Retention | Storage |
|-----------|------------|-----------|---------|
| Request Logs | ~100K rows | 90 days | PostgreSQL |
| Aggregated Metrics | ~1K rows | 1 year | PostgreSQL |
| ML Predictions Cache | ~50K keys | 5 minutes | Redis |
| Rate Limit Counters | ~10K keys | 1 minute | Redis |

**Data Velocity:**
```python
# Real-time metrics
REQUESTS_PER_SECOND_AVG = 50
REQUESTS_PER_SECOND_PEAK = 500
DATA_POINTS_PER_REQUEST = 15  # Fields logged

# Daily data volume
DAILY_DATA_POINTS = REQUESTS_PER_SECOND_AVG * 86400 * DATA_POINTS_PER_REQUEST
# ≈ 64.8 million data points
```

---

## 3. Data Preprocessing and Cleaning

### 3.1 Data Quality Issues

**Common Issues in IntelliRate Data:**

1. **Missing Values:**
   ```python
   # Some requests may not have token counts (errors)
   raw_data = {
       'tokens': None,  # Missing for failed requests
       'latency_ms': 0,  # Invalid value
   }
   ```

2. **Outliers:**
   ```python
   # Extreme latency values (network issues)
   latency_values = [85, 92, 78, 5000, 88, 95]  # 5000ms is outlier
   ```

3. **Inconsistent Formats:**
   ```python
   # User ID formats may vary
   user_ids = ['uid123', 'UID-123', 'firebase:uid123']
   ```

### 3.2 Data Cleaning Techniques

**Handling Missing Values:**

```python
import pandas as pd
import numpy as np

def clean_request_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess request log data"""
    
    # 1. Handle missing token counts (impute with median)
    df['total_tokens'] = df['total_tokens'].fillna(
        df['total_tokens'].median()
    )
    
    # 2. Remove rows with invalid latency
    df = df[df['latency_ms'] > 0]
    
    # 3. Standardize user IDs
    df['user_id'] = df['user_id'].str.lower().str.strip()
    
    # 4. Convert timestamps to consistent timezone
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # 5. Remove duplicate rows
    df = df.drop_duplicates(subset=['timestamp', 'user_id', 'endpoint'])
    
    return df
```

**Outlier Detection and Treatment:**

```python
from scipy import stats

def remove_outliers(df: pd.DataFrame, column: str, z_threshold: float = 3) -> pd.DataFrame:
    """Remove outliers using Z-score method"""
    
    z_scores = np.abs(stats.zscore(df[column]))
    return df[z_scores < z_threshold]

def cap_outliers(df: pd.DataFrame, column: str, percentile: float = 99) -> pd.DataFrame:
    """Cap outliers at specified percentile"""
    
    cap_value = df[column].quantile(percentile / 100)
    df[column] = df[column].clip(upper=cap_value)
    return df

# Example usage
df['latency_ms'] = cap_outliers(df, 'latency_ms', percentile=99)
```

### 3.3 Data Transformation

**Normalization:**

```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Min-Max Scaling (0 to 1)
min_max_scaler = MinMaxScaler()
df['latency_normalized'] = min_max_scaler.fit_transform(df[['latency_ms']])

# Z-Score Standardization (mean=0, std=1)
standard_scaler = StandardScaler()
df['latency_standardized'] = standard_scaler.fit_transform(df[['latency_ms']])
```

**Log Transformation:**

```python
# For highly skewed distributions (e.g., request counts)
df['log_requests'] = np.log1p(df['requests_per_minute'])

# Before: [1, 10, 100, 1000, 10000]
# After:  [0.69, 2.40, 4.62, 6.91, 9.21]
```

**Categorical Encoding:**

```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# Label Encoding for ordinal data
tier_encoder = LabelEncoder()
df['tier_encoded'] = tier_encoder.fit_transform(df['user_tier'])
# 'free' → 0, 'pro' → 1, 'enterprise' → 2

# One-Hot Encoding for nominal data
method_encoded = pd.get_dummies(df['method'], prefix='method')
# 'GET' → [1, 0, 0, 0]
# 'POST' → [0, 1, 0, 0]
# 'PUT' → [0, 0, 1, 0]
# 'DELETE' → [0, 0, 0, 1]
```

---

## 4. Exploratory Data Analysis (EDA)

### 4.1 Descriptive Statistics

**Summary Statistics:**

```python
def generate_summary_statistics(df: pd.DataFrame) -> dict:
    """Generate descriptive statistics for request data"""
    
    return {
        'total_requests': len(df),
        'unique_users': df['user_id'].nunique(),
        'date_range': {
            'start': df['timestamp'].min(),
            'end': df['timestamp'].max()
        },
        'latency_stats': {
            'mean': df['latency_ms'].mean(),
            'median': df['latency_ms'].median(),
            'std': df['latency_ms'].std(),
            'p95': df['latency_ms'].quantile(0.95),
            'p99': df['latency_ms'].quantile(0.99)
        },
        'token_stats': {
            'total': df['total_tokens'].sum(),
            'avg_per_request': df['total_tokens'].mean()
        },
        'error_rate': (df['status_code'] >= 400).mean(),
        'tier_distribution': df['user_tier'].value_counts().to_dict()
    }
```

**Sample Output:**
```json
{
  "total_requests": 150000,
  "unique_users": 2500,
  "latency_stats": {
    "mean": 125.5,
    "median": 98.2,
    "std": 85.3,
    "p95": 285.0,
    "p99": 450.0
  },
  "tier_distribution": {
    "free": 1800,
    "pro": 550,
    "enterprise": 150
  }
}
```

### 4.2 Distribution Analysis

**Request Volume Distribution:**

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_distribution_analysis(df: pd.DataFrame):
    """Visualize key distributions"""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Latency Distribution
    sns.histplot(df['latency_ms'], bins=50, ax=axes[0, 0])
    axes[0, 0].set_title('Latency Distribution')
    axes[0, 0].set_xlabel('Latency (ms)')
    
    # 2. Requests per User
    user_counts = df.groupby('user_id').size()
    sns.histplot(user_counts, bins=50, ax=axes[0, 1])
    axes[0, 1].set_title('Requests per User')
    
    # 3. Hourly Request Pattern
    df['hour'] = df['timestamp'].dt.hour
    hourly_counts = df.groupby('hour').size()
    axes[1, 0].bar(hourly_counts.index, hourly_counts.values)
    axes[1, 0].set_title('Hourly Request Pattern')
    
    # 4. User Tier Distribution
    tier_counts = df['user_tier'].value_counts()
    axes[1, 1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%')
    axes[1, 1].set_title('User Tier Distribution')
    
    plt.tight_layout()
    return fig
```

### 4.3 Correlation Analysis

**Feature Correlations:**

```python
def analyze_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation matrix for numeric features"""
    
    numeric_cols = [
        'requests_per_minute',
        'unique_endpoints',
        'error_rate',
        'avg_latency',
        'total_tokens',
        'behavioral_consistency'
    ]
    
    correlation_matrix = df[numeric_cols].corr()
    
    # Visualize
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap='coolwarm',
        center=0,
        fmt='.2f'
    )
    plt.title('Feature Correlation Matrix')
    
    return correlation_matrix
```

**Sample Correlation Insights:**
```
                      requests_per_min  error_rate  avg_latency
requests_per_min               1.00        0.65        0.45
error_rate                     0.65        1.00        0.72
avg_latency                    0.45        0.72        1.00

Insight: High request volume correlates with higher error rates,
which in turn correlates with increased latency.
```

### 4.4 Time Series Analysis

**Trend and Seasonality Detection:**

```python
from statsmodels.tsa.seasonal import seasonal_decompose

def decompose_traffic_patterns(df: pd.DataFrame) -> dict:
    """Decompose traffic into trend, seasonal, and residual components"""
    
    # Resample to hourly frequency
    hourly_traffic = df.set_index('timestamp').resample('H')['request_count'].sum()
    
    # Decompose
    decomposition = seasonal_decompose(
        hourly_traffic,
        model='additive',
        period=24  # Daily seasonality
    )
    
    return {
        'trend': decomposition.trend,
        'seasonal': decomposition.seasonal,
        'residual': decomposition.resid,
        'observed': decomposition.observed
    }
```

**Traffic Pattern Visualization:**
```
Observed:   ════════════════════════════════════
                  ╱╲    ╱╲    ╱╲    ╱╲
                 ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲
                ╱    ╲╱    ╲╱    ╲╱    ╲

Trend:      ─────────────────────────────────
                                     ───────
                          ───────────
              ───────────

Seasonal:        ╱╲    ╱╲    ╱╲    ╱╲
                ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲
               ╱    ╲╱    ╲╱    ╲╱    ╲

Residual:   ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿

Peak Hours: 9 AM - 12 PM, 2 PM - 5 PM (business hours)
Low Hours:  2 AM - 6 AM (overnight)
```

---

## 5. Feature Engineering

### 5.1 What is Feature Engineering?

Feature engineering is the process of using domain knowledge to create input variables (features) that make machine learning algorithms work better. Good features can significantly improve model performance.

### 5.2 Feature Types in IntelliRate

**Raw Features (Direct Measurements):**
```python
raw_features = {
    'requests_per_minute': 150,      # Direct count
    'total_tokens_used': 5000,       # Direct sum
    'avg_latency_ms': 125.5,         # Direct average
    'error_count': 3,                # Direct count
    'unique_endpoints': 8            # Direct count
}
```

**Derived Features (Calculated):**
```python
derived_features = {
    'error_rate_percentage': error_count / total_requests * 100,
    'tokens_per_request': total_tokens / total_requests,
    'requests_per_second': requests_per_minute / 60,
    'endpoint_diversity_score': unique_endpoints / total_possible_endpoints
}
```

**Temporal Features:**
```python
temporal_features = {
    'hour_of_day': timestamp.hour,           # 0-23
    'day_of_week': timestamp.dayofweek,      # 0-6
    'is_weekend': timestamp.dayofweek >= 5,  # Boolean
    'is_business_hours': 9 <= timestamp.hour <= 17  # Boolean
}
```

**Aggregated Features:**
```python
aggregated_features = {
    'requests_last_hour': count_requests(user_id, last_hour),
    'requests_last_24h': count_requests(user_id, last_24h),
    'avg_daily_requests': total_requests / active_days,
    'peak_hour_ratio': peak_hour_requests / avg_hour_requests
}
```

### 5.3 Feature Engineering for Abuse Detection

**Behavioral Features:**

```python
def engineer_abuse_detection_features(
    user_id: str,
    window_minutes: int = 60
) -> dict:
    """Create features for abuse detection model"""
    
    recent_logs = get_user_logs(user_id, window_minutes)
    
    return {
        # Volume-based features
        'requests_per_minute': len(recent_logs) / window_minutes,
        'burst_count': count_bursts(recent_logs, threshold=10),
        
        # Diversity features
        'unique_endpoints_accessed': len(set(log['endpoint'] for log in recent_logs)),
        'unique_models_used': len(set(log['model'] for log in recent_logs)),
        'endpoint_diversity_score': calculate_entropy(recent_logs, 'endpoint'),
        
        # Error patterns
        'error_rate_percentage': sum(1 for log in recent_logs if log['status'] >= 400) / len(recent_logs) * 100,
        'consecutive_errors': count_consecutive_errors(recent_logs),
        
        # Timing patterns
        'request_timing_patterns': calculate_timing_variance(recent_logs),
        'avg_request_interval': np.mean(calculate_intervals(recent_logs)),
        
        # Resource usage
        'token_consumption_rate': sum(log['tokens'] for log in recent_logs) / window_minutes,
        
        # Reputation (external data)
        'ip_reputation_score': get_ip_reputation(recent_logs[0]['ip']),
        
        # Historical comparison
        'current_vs_historical_ratio': current_rate / historical_avg_rate
    }
```

**Entropy Calculation for Diversity:**

```python
from scipy.stats import entropy
from collections import Counter

def calculate_entropy(logs: List[dict], field: str) -> float:
    """Calculate Shannon entropy for a categorical field"""
    
    values = [log[field] for log in logs]
    value_counts = Counter(values)
    
    total = sum(value_counts.values())
    probabilities = [count / total for count in value_counts.values()]
    
    return entropy(probabilities, base=2)

# Low entropy (1.0): User always hits same endpoint (suspicious)
# High entropy (3.5): User accesses diverse endpoints (normal)
```

### 5.4 Feature Engineering for Rate Limit Optimization

```python
def engineer_rate_limit_features(
    user_id: str,
    days: int = 30
) -> dict:
    """Create features for rate limit model"""
    
    historical_data = get_user_history(user_id, days)
    
    return {
        # User tier (one-hot encoded)
        'is_free_tier': user.tier == 'free',
        'is_pro_tier': user.tier == 'pro',
        'is_enterprise_tier': user.tier == 'enterprise',
        
        # Historical usage patterns
        'historical_avg_requests': np.mean(historical_data['daily_requests']),
        'historical_max_requests': np.max(historical_data['daily_requests']),
        'historical_std_requests': np.std(historical_data['daily_requests']),
        
        # Behavioral metrics
        'behavioral_consistency': 1 - cv(historical_data['daily_requests']),
        'error_history': np.mean(historical_data['error_rate']),
        'payment_history_score': calculate_payment_score(user_id),
        
        # Temporal patterns
        'days_since_registration': (now - user.created_at).days,
        'active_days_ratio': len(historical_data) / days,
        'weekend_usage_ratio': weekend_requests / total_requests,
        
        # Current context
        'current_hour': datetime.now().hour,
        'is_peak_hour': is_peak_hour(datetime.now())
    }

def cv(data: np.ndarray) -> float:
    """Coefficient of Variation (normalized standard deviation)"""
    return np.std(data) / np.mean(data) if np.mean(data) > 0 else 0
```

### 5.5 Feature Selection

**Importance-Based Selection:**

```python
from sklearn.ensemble import RandomForestClassifier

def select_important_features(
    X: pd.DataFrame,
    y: pd.Series,
    threshold: float = 0.05
) -> List[str]:
    """Select features based on importance from Random Forest"""
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    importances = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Select features above threshold
    selected = importances[importances['importance'] >= threshold]['feature'].tolist()
    
    return selected

# Sample output:
# Selected features: ['requests_per_minute', 'error_rate', 'endpoint_diversity',
#                     'ip_reputation_score', 'request_timing_patterns']
```

---

## 6. Machine Learning Models

### 6.1 Supervised vs Unsupervised Learning

**Supervised Learning (XGBoost Rate Limiter):**
- Training data includes input features AND target labels
- Model learns mapping from features to target
- Example: User features → Recommended rate limit

**Unsupervised Learning (Isolation Forest):**
- Training data contains only input features (no labels)
- Model learns structure/patterns in data
- Example: Request features → Anomaly score

### 6.2 Isolation Forest for Anomaly Detection

**Algorithm Overview:**

Isolation Forest detects anomalies by isolating observations. Anomalies are easier to isolate because they:
- Have different feature values than normal points
- Require fewer splits to separate

**How It Works:**

```
Step 1: Random Feature Selection
        Select random feature and random split value

Step 2: Recursive Partitioning
        Split data recursively until isolated

Step 3: Path Length Calculation
        Anomalies have shorter path lengths

Isolation Tree:
        [requests_per_min < 100]
           /              \
         No               Yes
          |                |
   [error_rate < 5]    [Normal]
      /        \
    No          Yes
     |           |
  [Anomaly]   [Normal]

Normal point path length: 3
Anomaly point path length: 1 (isolated quickly)
```

**Implementation in IntelliRate:**

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AbuseDetector:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            n_estimators=100,           # Number of trees
            contamination=contamination, # Expected anomaly ratio
            random_state=42,
            n_jobs=-1                   # Use all CPU cores
        )
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray) -> None:
        """Train model on historical data"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
    
    def predict(self, features: dict) -> dict:
        """Predict anomaly score for new request"""
        X = np.array([[
            features['requests_per_minute'],
            features['unique_endpoints_accessed'],
            features['error_rate_percentage'],
            features['request_timing_patterns'],
            features['ip_reputation_score'],
            features['endpoint_diversity_score']
        ]])
        
        X_scaled = self.scaler.transform(X)
        
        # Get raw score (-1 for anomalies, 1 for normal)
        raw_score = self.model.decision_function(X_scaled)[0]
        
        # Convert to 0-1 anomaly score
        anomaly_score = 1 - (raw_score + 0.5)  # Normalize
        anomaly_score = np.clip(anomaly_score, 0, 1)
        
        is_abusive = self.model.predict(X_scaled)[0] == -1
        
        return {
            'anomaly_score': float(anomaly_score),
            'is_abusive': bool(is_abusive),
            'confidence': float(abs(raw_score))
        }
```

**Training Data Generation:**

```python
def generate_training_data(n_samples: int = 10000) -> np.ndarray:
    """Generate synthetic training data for Isolation Forest"""
    
    # Normal behavior patterns
    normal = np.column_stack([
        np.random.normal(50, 15, n_samples),    # requests_per_min
        np.random.randint(3, 10, n_samples),    # unique_endpoints
        np.random.normal(2, 1, n_samples),       # error_rate (low)
        np.random.uniform(0.7, 1.0, n_samples), # timing_patterns (consistent)
        np.random.uniform(0.7, 1.0, n_samples), # ip_reputation (good)
        np.random.uniform(0.3, 0.8, n_samples)  # endpoint_diversity (moderate)
    ])
    
    # Inject some anomalies (10%)
    n_anomalies = int(n_samples * 0.1)
    anomalies = np.column_stack([
        np.random.uniform(150, 500, n_anomalies),  # High request rate
        np.random.randint(1, 3, n_anomalies),      # Low endpoint diversity
        np.random.uniform(15, 50, n_anomalies),    # High error rate
        np.random.uniform(0.1, 0.4, n_anomalies),  # Irregular timing
        np.random.uniform(0.0, 0.3, n_anomalies),  # Bad IP reputation
        np.random.uniform(0.0, 0.2, n_anomalies)   # Very low diversity
    ])
    
    return np.vstack([normal, anomalies])
```

### 6.3 XGBoost for Rate Limit Optimization

**Algorithm Overview:**

XGBoost (Extreme Gradient Boosting) is an ensemble method that builds decision trees sequentially, where each tree corrects errors of previous trees.

**Gradient Boosting Process:**

```
Iteration 1: Build Tree₁, predict y₁
Iteration 2: Build Tree₂ on residuals (y - y₁), update y₂ = y₁ + α·Tree₂
Iteration 3: Build Tree₃ on residuals (y - y₂), update y₃ = y₂ + α·Tree₃
...
Final: ŷ = Σ αᵢ·Treeᵢ
```

**Implementation in IntelliRate:**

```python
import xgboost as xgb
import numpy as np

class RateLimitOptimizer:
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'is_free_tier', 'is_pro_tier', 'is_enterprise_tier',
            'historical_avg_requests', 'behavioral_consistency',
            'days_since_registration', 'error_history'
        ]
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train model on historical rate limit data"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, features: dict) -> dict:
        """Predict optimal rate limit for user"""
        X = np.array([[
            features.get('is_free_tier', 0),
            features.get('is_pro_tier', 0),
            features.get('is_enterprise_tier', 0),
            features.get('historical_avg_requests', 50),
            features.get('behavioral_consistency', 0.8),
            features.get('days_since_registration', 30),
            features.get('error_history', 0.02)
        ]])
        
        X_scaled = self.scaler.transform(X)
        predicted_limit = self.model.predict(X_scaled)[0]
        
        # Round to nearest 10
        recommended_limit = int(round(predicted_limit, -1))
        recommended_limit = max(10, min(1000, recommended_limit))  # Bounds
        
        return {
            'recommended_limit': recommended_limit,
            'confidence': self._calculate_confidence(X_scaled)
        }
    
    def _calculate_confidence(self, X: np.ndarray) -> float:
        """Estimate prediction confidence using tree variance"""
        predictions = []
        for tree in self.model.get_booster().get_dump():
            # Get individual tree predictions
            pass
        return 0.85  # Simplified
```

**Feature Importance Analysis:**

```python
def get_feature_importance(model: xgb.XGBRegressor) -> pd.DataFrame:
    """Get feature importance from XGBoost model"""
    
    importance = pd.DataFrame({
        'feature': model.feature_names_,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance

# Sample output:
# feature                    importance
# is_enterprise_tier         0.35
# historical_avg_requests    0.25
# behavioral_consistency     0.18
# is_pro_tier                0.12
# days_since_registration    0.06
# error_history              0.04
```

### 6.4 Prophet for Traffic Forecasting

**Algorithm Overview:**

Prophet is a time series forecasting model developed by Facebook that decomposes time series into:
- **Trend (g(t)):** Non-periodic changes
- **Seasonality (s(t)):** Periodic patterns (daily, weekly, yearly)
- **Holidays (h(t)):** Special events
- **Error (ε):** Unexplained variance

**Formula:**
```
y(t) = g(t) + s(t) + h(t) + ε
```

**Implementation in IntelliRate:**

```python
from prophet import Prophet
import pandas as pd

class TrafficForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            seasonality_mode='multiplicative'
        )
    
    def fit(self, historical_data: pd.DataFrame) -> None:
        """Train model on historical traffic data"""
        # Prophet requires columns: ds (datetime), y (value)
        df = historical_data.rename(columns={
            'timestamp': 'ds',
            'request_count': 'y'
        })
        
        self.model.fit(df)
    
    def forecast(self, periods_ahead: int, freq: str = 'H') -> dict:
        """Forecast future traffic"""
        # Create future dataframe
        future = self.model.make_future_dataframe(
            periods=periods_ahead,
            freq=freq
        )
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract predictions for future periods
        future_forecast = forecast.tail(periods_ahead)
        
        predictions = future_forecast['yhat'].tolist()
        lower_bound = future_forecast['yhat_lower'].tolist()
        upper_bound = future_forecast['yhat_upper'].tolist()
        
        # Determine trend
        trend = 'stable'
        if predictions[-1] > predictions[0] * 1.1:
            trend = 'increasing'
        elif predictions[-1] < predictions[0] * 0.9:
            trend = 'decreasing'
        
        return {
            'predictions': predictions,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'trend': trend,
            'timestamps': future_forecast['ds'].tolist()
        }
    
    def get_components(self) -> dict:
        """Extract trend and seasonality components"""
        return {
            'trend': self.model.trend,
            'weekly_seasonality': self.model.seasonalities.get('weekly'),
            'daily_seasonality': self.model.seasonalities.get('daily')
        }
```

**Forecast Visualization:**

```
Traffic Forecast (Next 24 Hours):

Requests|                                      ╱───────
  500   |                               ╱─────╱
        |                        ╱─────╱
  400   |                 ╱─────╱
        |          ╱─────╱      Upper Bound
  300   |   ──────╱─────────────────────────── Prediction
        |   ─────────────────────────────────── Lower Bound
  200   |
        |
  100   |─────╲
        |      ╲─────╲
    0   └────────────────────────────────────────────── Time
        Now  +4h   +8h   +12h   +16h   +20h   +24h
        
Peak Expected: +10h (330 requests/hour)
Trend: Increasing (15% growth expected)
```

---

## 7. Model Evaluation

### 7.1 Evaluation Metrics

**For Anomaly Detection (Binary Classification):**

```python
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)

def evaluate_anomaly_detector(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_scores: np.ndarray
) -> dict:
    """Evaluate anomaly detection model"""
    
    return {
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1_score': f1_score(y_true, y_pred),
        'roc_auc': roc_auc_score(y_true, y_scores),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
    }

# Sample output:
# {
#   'precision': 0.92,   # Of detected anomalies, 92% were real
#   'recall': 0.85,      # Of real anomalies, 85% were detected
#   'f1_score': 0.88,    # Harmonic mean of precision and recall
#   'roc_auc': 0.94      # Area under ROC curve
# }
```

**Confusion Matrix:**
```
                     Predicted
                   Normal  Anomaly
Actual   Normal    9200     80      (80 False Positives)
         Anomaly    150     570     (150 False Negatives)

Precision = 570 / (570 + 80) = 87.7%
Recall = 570 / (570 + 150) = 79.2%
```

**For Rate Limit Prediction (Regression):**

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_rate_limit_model(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> dict:
    """Evaluate rate limit prediction model"""
    
    return {
        'mae': mean_absolute_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2_score': r2_score(y_true, y_pred),
        'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    }

# Sample output:
# {
#   'mae': 8.5,          # Average error: 8.5 requests/min
#   'rmse': 12.3,        # Root mean squared error
#   'r2_score': 0.89,    # 89% variance explained
#   'mape': 7.2          # Mean absolute percentage error: 7.2%
# }
```

**For Time Series Forecasting:**

```python
def evaluate_forecast(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> dict:
    """Evaluate time series forecast"""
    
    return {
        'mae': mean_absolute_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
        'coverage': calculate_prediction_interval_coverage(y_true, lower, upper)
    }
```

### 7.2 Cross-Validation

**K-Fold Cross-Validation:**

```python
from sklearn.model_selection import cross_val_score, KFold

def cross_validate_model(model, X: np.ndarray, y: np.ndarray, k: int = 5):
    """Perform k-fold cross-validation"""
    
    kfold = KFold(n_splits=k, shuffle=True, random_state=42)
    
    scores = cross_val_score(
        model, X, y,
        cv=kfold,
        scoring='neg_mean_absolute_error'
    )
    
    return {
        'mean_score': -scores.mean(),
        'std_score': scores.std(),
        'fold_scores': (-scores).tolist()
    }

# Sample output:
# {
#   'mean_score': 8.2,
#   'std_score': 1.5,
#   'fold_scores': [7.5, 8.8, 8.1, 9.2, 7.4]
# }
```

**Time Series Cross-Validation:**

```python
from sklearn.model_selection import TimeSeriesSplit

def time_series_cv(model, X: np.ndarray, y: np.ndarray, n_splits: int = 5):
    """Cross-validation for time series (respects temporal order)"""
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        scores.append(mean_absolute_error(y_test, y_pred))
    
    return {
        'mean_score': np.mean(scores),
        'std_score': np.std(scores),
        'fold_scores': scores
    }
```

### 7.3 Model Selection

**Hyperparameter Tuning:**

```python
from sklearn.model_selection import GridSearchCV

def tune_xgboost(X: np.ndarray, y: np.ndarray) -> dict:
    """Grid search for optimal XGBoost parameters"""
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.3],
        'subsample': [0.7, 0.8, 0.9]
    }
    
    grid_search = GridSearchCV(
        xgb.XGBRegressor(random_state=42),
        param_grid,
        cv=5,
        scoring='neg_mean_absolute_error',
        n_jobs=-1
    )
    
    grid_search.fit(X, y)
    
    return {
        'best_params': grid_search.best_params_,
        'best_score': -grid_search.best_score_,
        'cv_results': grid_search.cv_results_
    }

# Sample output:
# {
#   'best_params': {
#     'n_estimators': 100,
#     'max_depth': 5,
#     'learning_rate': 0.1,
#     'subsample': 0.8
#   },
#   'best_score': 7.8  # MAE
# }
```

---

## 8. Model Deployment

### 8.1 Model Serialization

**Saving Trained Models:**

```python
import joblib
import os

def save_model(model, model_name: str, version: str) -> str:
    """Save model with versioning"""
    
    model_dir = f"ml-models/{model_name}"
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = f"{model_dir}/model_v{version}.joblib"
    joblib.dump(model, model_path)
    
    # Save metadata
    metadata = {
        'version': version,
        'created_at': datetime.utcnow().isoformat(),
        'model_type': type(model).__name__,
        'feature_names': getattr(model, 'feature_names_', None)
    }
    
    with open(f"{model_dir}/metadata_v{version}.json", 'w') as f:
        json.dump(metadata, f)
    
    return model_path

def load_model(model_name: str, version: str = 'latest'):
    """Load model by name and version"""
    
    model_dir = f"ml-models/{model_name}"
    
    if version == 'latest':
        # Find latest version
        versions = [f for f in os.listdir(model_dir) if f.startswith('model_v')]
        latest = sorted(versions)[-1]
        model_path = f"{model_dir}/{latest}"
    else:
        model_path = f"{model_dir}/model_v{version}.joblib"
    
    return joblib.load(model_path)
```

### 8.2 AWS SageMaker Deployment

**Deployment Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS SageMaker                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Isolation Forest│  │    XGBoost      │  │   Prophet   │  │
│  │   Endpoint      │  │   Endpoint      │  │  Endpoint   │  │
│  │                 │  │                 │  │             │  │
│  │ ml.t2.medium    │  │ ml.t2.medium    │  │ ml.t2.medium│  │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘  │
│           │                    │                  │          │
│           └────────────────────┼──────────────────┘          │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │
                          HTTPS Requests
                                 │
                    ┌────────────┴────────────┐
                    │    IntelliRate Gateway  │
                    │    (ML Client)          │
                    └─────────────────────────┘
```

**SageMaker Client:**

```python
import boto3
import json

class SageMakerClient:
    def __init__(self, region: str = 'us-east-1'):
        self.runtime = boto3.client(
            'sagemaker-runtime',
            region_name=region
        )
        self.endpoints = {
            'isolation_forest': 'isolation-forest-endpoint',
            'xgboost': 'xgboost-limiter-endpoint',
            'prophet': 'prophet-forecaster-endpoint'
        }
    
    async def predict(
        self,
        model_name: str,
        features: dict
    ) -> dict:
        """Invoke SageMaker endpoint for prediction"""
        
        endpoint = self.endpoints[model_name]
        payload = json.dumps(features)
        
        response = self.runtime.invoke_endpoint(
            EndpointName=endpoint,
            ContentType='application/json',
            Body=payload
        )
        
        result = json.loads(response['Body'].read().decode())
        return result
```

### 8.3 Fallback Mechanism

```python
class MLPredictionService:
    def __init__(self, use_cloud: bool = True):
        self.use_cloud = use_cloud
        self.cloud_client = SageMakerClient() if use_cloud else None
        self.local_models = {
            'isolation_forest': load_model('isolation_forest'),
            'xgboost': load_model('xgboost'),
            'prophet': load_model('prophet')
        }
    
    async def predict(
        self,
        model_name: str,
        features: dict
    ) -> dict:
        """Predict with automatic fallback"""
        
        # Try cloud first
        if self.use_cloud:
            try:
                result = await asyncio.wait_for(
                    self.cloud_client.predict(model_name, features),
                    timeout=5.0
                )
                result['source'] = 'cloud'
                return result
            except (TimeoutError, ClientError) as e:
                logger.warning(f"Cloud prediction failed: {e}")
        
        # Fallback to local model
        local_model = self.local_models[model_name]
        result = local_model.predict(features)
        result['source'] = 'fallback'
        return result
```

### 8.4 Model Monitoring

**Prediction Drift Detection:**

```python
def monitor_prediction_distribution(
    recent_predictions: List[float],
    baseline_distribution: dict
) -> dict:
    """Detect if prediction distribution has drifted"""
    
    from scipy.stats import ks_2samp
    
    # Kolmogorov-Smirnov test
    statistic, pvalue = ks_2samp(
        recent_predictions,
        baseline_distribution['samples']
    )
    
    drift_detected = pvalue < 0.05
    
    return {
        'drift_detected': drift_detected,
        'ks_statistic': statistic,
        'pvalue': pvalue,
        'recent_mean': np.mean(recent_predictions),
        'baseline_mean': baseline_distribution['mean'],
        'recent_std': np.std(recent_predictions),
        'baseline_std': baseline_distribution['std']
    }
```

---

## 9. Real-Time Analytics

### 9.1 Streaming Data Processing

**Real-Time Metrics Aggregation:**

```python
from collections import defaultdict
import asyncio

class RealTimeAnalytics:
    def __init__(self):
        self.window_size = 60  # seconds
        self.request_counts = defaultdict(int)
        self.latency_samples = defaultdict(list)
        self.error_counts = defaultdict(int)
    
    async def record_request(
        self,
        user_id: str,
        latency_ms: float,
        status_code: int
    ) -> None:
        """Record incoming request metrics"""
        
        current_minute = int(time.time() / 60)
        key = (user_id, current_minute)
        
        self.request_counts[key] += 1
        self.latency_samples[key].append(latency_ms)
        
        if status_code >= 400:
            self.error_counts[key] += 1
    
    async def get_current_metrics(self, user_id: str) -> dict:
        """Get real-time metrics for user"""
        
        current_minute = int(time.time() / 60)
        key = (user_id, current_minute)
        
        latencies = self.latency_samples.get(key, [])
        
        return {
            'requests_per_minute': self.request_counts.get(key, 0),
            'avg_latency_ms': np.mean(latencies) if latencies else 0,
            'p95_latency_ms': np.percentile(latencies, 95) if latencies else 0,
            'error_rate': self.error_counts.get(key, 0) / max(1, self.request_counts.get(key, 1))
        }
```

### 9.2 Dashboard Metrics

**Analytics API Endpoints:**

```python
@app.get("/api/v1/analytics/realtime")
async def get_realtime_analytics() -> dict:
    """Real-time system analytics"""
    
    return {
        'current_rps': await get_current_requests_per_second(),
        'active_users': await count_active_users(minutes=5),
        'avg_latency_ms': await get_average_latency(minutes=5),
        'error_rate': await get_error_rate(minutes=5),
        'ml_predictions': {
            'abuse_detections': await count_abuse_detections(minutes=60),
            'rate_limit_optimizations': await count_rate_optimizations(minutes=60)
        },
        'top_endpoints': await get_top_endpoints(minutes=60, limit=10),
        'top_users': await get_top_users(minutes=60, limit=10)
    }

@app.get("/api/v1/analytics/user/{user_id}")
async def get_user_analytics(user_id: str, days: int = 30) -> dict:
    """User-specific analytics"""
    
    return {
        'user_id': user_id,
        'total_requests': await count_user_requests(user_id, days),
        'total_tokens': await sum_user_tokens(user_id, days),
        'avg_latency_ms': await avg_user_latency(user_id, days),
        'error_rate': await user_error_rate(user_id, days),
        'daily_usage': await get_daily_usage(user_id, days),
        'endpoint_distribution': await get_endpoint_distribution(user_id, days),
        'model_usage': await get_model_usage(user_id, days)
    }
```

---

## 10. Statistical Concepts in IntelliRate

### 10.1 Probability Distributions

**Normal Distribution (Latency):**

```python
from scipy.stats import norm

def analyze_latency_distribution(latencies: np.ndarray) -> dict:
    """Fit normal distribution to latency data"""
    
    mu, std = norm.fit(latencies)
    
    # Probability of latency exceeding threshold
    threshold = 500  # ms
    prob_exceed = 1 - norm.cdf(threshold, mu, std)
    
    return {
        'mean': mu,
        'std': std,
        'p50': norm.ppf(0.50, mu, std),
        'p95': norm.ppf(0.95, mu, std),
        'p99': norm.ppf(0.99, mu, std),
        'prob_exceed_500ms': prob_exceed
    }
```

**Poisson Distribution (Request Arrivals):**

```python
from scipy.stats import poisson

def analyze_request_arrivals(counts: np.ndarray) -> dict:
    """Model request arrivals as Poisson process"""
    
    lambda_rate = np.mean(counts)  # Average requests per interval
    
    return {
        'lambda': lambda_rate,
        'prob_zero': poisson.pmf(0, lambda_rate),
        'prob_above_100': 1 - poisson.cdf(100, lambda_rate),
        'expected_max': poisson.ppf(0.999, lambda_rate)
    }
```

### 10.2 Hypothesis Testing

**A/B Testing for Rate Limits:**

```python
from scipy.stats import ttest_ind

def ab_test_rate_limits(
    group_a_errors: np.ndarray,  # Control group
    group_b_errors: np.ndarray   # Treatment group
) -> dict:
    """Test if new rate limits reduce error rates"""
    
    t_stat, p_value = ttest_ind(group_a_errors, group_b_errors)
    
    significant = p_value < 0.05
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': significant,
        'group_a_mean': np.mean(group_a_errors),
        'group_b_mean': np.mean(group_b_errors),
        'improvement': (np.mean(group_a_errors) - np.mean(group_b_errors)) / np.mean(group_a_errors) * 100
    }

# Sample output:
# {
#   't_statistic': 3.45,
#   'p_value': 0.001,
#   'significant': True,
#   'improvement': 15.2  # 15.2% reduction in errors
# }
```

### 10.3 Confidence Intervals

**Confidence Interval for Rate Limit Recommendation:**

```python
def calculate_confidence_interval(
    predictions: np.ndarray,
    confidence: float = 0.95
) -> dict:
    """Calculate confidence interval for predictions"""
    
    n = len(predictions)
    mean = np.mean(predictions)
    std_error = np.std(predictions, ddof=1) / np.sqrt(n)
    
    from scipy.stats import t
    t_critical = t.ppf((1 + confidence) / 2, n - 1)
    
    margin = t_critical * std_error
    
    return {
        'mean': mean,
        'lower': mean - margin,
        'upper': mean + margin,
        'confidence': confidence
    }

# Sample output:
# {
#   'mean': 85.0,
#   'lower': 78.5,
#   'upper': 91.5,
#   'confidence': 0.95
# }
# Interpretation: 95% confident optimal limit is between 78.5 and 91.5
```

---

## 11. Conclusion

### 11.1 Summary

The IntelliRate Gateway demonstrates comprehensive application of data science principles:

1. **Data Collection:** Structured logging of all API requests
2. **Data Preprocessing:** Cleaning, transformation, and normalization
3. **Exploratory Analysis:** Understanding traffic patterns and correlations
4. **Feature Engineering:** Creating meaningful inputs for ML models
5. **Machine Learning:**
   - Isolation Forest for unsupervised anomaly detection
   - XGBoost for supervised rate limit optimization
   - Prophet for time series traffic forecasting
6. **Model Evaluation:** Cross-validation and performance metrics
7. **Deployment:** SageMaker hosting with fallback mechanisms
8. **Monitoring:** Real-time analytics and drift detection

### 11.2 Key Takeaways

- **Data quality is crucial:** Clean data leads to better models
- **Feature engineering matters:** Good features improve performance significantly
- **Choose appropriate algorithms:** Match algorithm to problem type
- **Evaluate rigorously:** Use proper validation techniques
- **Monitor in production:** Models can drift over time
- **Design for resilience:** Fallbacks ensure reliability

### 11.3 Future Enhancements

- **Deep Learning:** Neural networks for complex pattern detection
- **Reinforcement Learning:** Dynamic rate limit adjustment
- **Federated Learning:** Privacy-preserving model training
- **AutoML:** Automated model selection and tuning
- **Explainable AI:** Understanding model decisions

---

## References

1. Hastie, T., Tibshirani, R., & Friedman, J. (2009). The Elements of Statistical Learning. Springer.
2. Géron, A. (2019). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow. O'Reilly.
3. VanderPlas, J. (2016). Python Data Science Handbook. O'Reilly.
4. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. IEEE International Conference on Data Mining.
5. Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD.
6. Taylor, S. J., & Letham, B. (2018). Forecasting at Scale. The American Statistician.
7. Scikit-learn Documentation. https://scikit-learn.org/stable/
8. XGBoost Documentation. https://xgboost.readthedocs.io/
9. Prophet Documentation. https://facebook.github.io/prophet/
10. AWS SageMaker Documentation. https://docs.aws.amazon.com/sagemaker/
