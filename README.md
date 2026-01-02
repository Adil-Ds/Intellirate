# 🚀 Intelli_Rate Gateway

**AI-Powered API Gateway with AWS ML Integration**

An intelligent API gateway system featuring machine learning-based abuse detection, dynamic rate limiting, and traffic forecasting, powered by AWS SageMaker.

---

## 🌟 Features

### Core Capabilities
- ✅ **Real-time Abuse Detection** - Isolation Forest ML model identifies anomalous behavior
- ✅ **Dynamic Rate Limiting** - XGBoost optimizes rate limits per user tier
- ✅ **Traffic Forecasting** - Prophet predicts future load patterns
- ✅ **Cloud-Native ML** - Models hosted on AWS SageMaker
- ✅ **Intelligent Fallback** - Automatic local model execution if cloud fails
- ✅ **Multi-Layer Caching** - Redis caching with 5-minute TTL
- ✅ **Auto-Scaling** - SageMaker endpoints with auto-scaling support

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ML Platform**: AWS SageMaker
- **ML Libraries**: scikit-learn, XGBoost, Prophet
- **Deployment**: Docker + Docker Compose
- **Automation**: N8N workflows

---

## 📁 Project Structure

```
intellirate-gateway/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Configuration
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── ml/              # ML integration
│   ├── scripts/             # Deployment scripts
│   └── tests/               # Test suite
├── cloud/                   # AWS configs
│   ├── deployment/          # Model containers
│   ├── monitoring/          # Dashboards
│   └── terraform/           # Infrastructure as Code
├── ml-models/               # Trained models
│   ├── isolation_forest/
│   ├── xgboost/
│   └── prophet/
├── docs/                    # Documentation
└── docker-compose.yml       # Service orchestration
```

---

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- AWS account (for cloud ML)

### 1. Clone & Setup
```bash
git clone <repo-url>
cd Intelli_Rate
cp .env.example .env
```

### 2. Start Local Development (Without Cloud ML)
```bash
# Edit .env: Set USE_CLOUD_ML=false
docker-compose up -d

# Access API: http://localhost:8000/docs
```

### 3. Deploy to AWS SageMaker (Optional)
```bash
# See docs/QUICKSTART.md for detailed guide
cd backend
python scripts/deploy_to_aws.py --model all --region us-east-1 --bucket <your-bucket>
```

> 📚 **For detailed setup instructions, see [docs/QUICKSTART.md](docs/QUICKSTART.md)**

---

## 📖 API Endpoints

### Abuse Detection
```bash
POST /api/v1/ml/detect-abuse
{
  "features": {
    "requests_per_minute": 150,
    "unique_endpoints_accessed": 20,
    "error_rate_percentage": 15.5,
    "request_timing_patterns": 0.8,
    "ip_reputation_score": 0.3,
    "endpoint_diversity_score": 0.6
  }
}

Response:
{
  "anomaly_score": 0.85,
  "is_abusive": true,
  "confidence": 0.92,
  "source": "cloud"
}
```

### Rate Limit Optimization
```bash
POST /api/v1/ml/optimize-rate-limit
{
  "user_features": {
    "user_tier": "premium",
    "historical_avg_requests": 100,
    "behavioral_consistency": 0.85
  }
}

Response:
{
  "recommended_limit": 150,
  "confidence": 0.88,
  "source": "cloud"
}
```

### Traffic Forecasting
```bash
POST /api/v1/ml/forecast-traffic
{
  "historical_data": [...],
  "periods_ahead": 6
}

Response:
{
  "predictions": [...],
  "trend": "increasing",
  "confidence": 0.85
}
```

---

## 🧠 ML Models

| Model | Purpose | Input Features | Output |
|-------|---------|----------------|--------|
| **Isolation Forest** | Abuse Detection | 6 behavioral features | Anomaly score (0-1) |
| **XGBoost** | Rate Limit Optimization | User tier, history, patterns | Recommended limit |
| **Prophet** | Traffic Forecasting | Time-series data | Future request counts |

---

## 🔧 Configuration

### Environment Variables
See `.env.example` for full configuration options:
- `USE_CLOUD_ML`: Toggle cloud vs local ML
- `ENABLE_ML_FALLBACK`: Auto-fallback to local models
- `ML_PREDICTION_CACHE_TTL`: Cache duration (seconds)

### Docker Services
- **backend**: FastAPI application (port 8000)
- **postgres**: Database (port 5432)
- **redis**: Cache (port 6379)
- **n8n**: Workflow automation (port 5678)

---

## 📊 Monitoring

### Cloud Monitoring
- **Endpoint Health**: `/api/v1/ml/health`
- **AWS Console**: SageMaker > Endpoints
- **Metrics**: Request count, latency, error rate

### Logs
```bash
# Application logs
docker-compose logs -f backend

# Cloud ML logs
aws logs tail /aws/sagemaker/Endpoints/isolation-forest-endpoint --follow
```

---

## 🧪 Testing

```bash
# Unit tests
cd backend
pytest tests/

# Integration tests
pytest tests/test_cloud_ml.py

# Test cloud endpoints
python scripts/test_cloud_endpoints.py
```

---

## 💰 Cost Estimation

**Monthly costs for typical usage (1M predictions):**
- SageMaker predictions: ~$0.50
- Instance runtime (ml.t2.medium × 3): ~$105/month
- S3 Storage: $1
- **Total**: ~$106.50/month

**Free tier**: AWS Free Tier includes 250 hours/month for 2 months

---

## 📚 Documentation

### 📖 Complete Documentation Index
Visit **[docs/README.md](docs/README.md)** for full documentation navigation.

### Quick Links
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5-30 minutes
- **[Project Walkthrough](docs/PROJECT_WALKTHROUGH.md)** - Complete system overview
- **[Groq Integration](docs/GROQ_DEPLOYMENT.md)** - Groq API proxy setup
- **[AWS Deployment](docs/AWS_DEPLOYMENT_GUIDE.md)** - SageMaker deployment
- **[Cloud Setup](docs/CLOUD_SETUP_GUIDE.md)** - AWS infrastructure setup
- **[Cloud Deployment Overview](docs/CLOUD_DEPLOYMENT.md)** - ML integration guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

---

## 🛠️ Development

### Local Model Training
```bash
cd backend/app/ml/training
python train_all_models.py
```

### Deploy New Model Version
```bash
python scripts/deploy_to_aws.py --model isolation_forest --region us-east-1 --bucket your-bucket
```

### Rollback
```bash
python scripts/rollback_deployment.py --model xgboost --version v1
```

---

## 🎓 Academic Value

This project demonstrates:
- ✅ Microservices architecture
- ✅ Cloud-native ML deployment
- ✅ Resilience patterns (fallback, retry, caching)
- ✅ Infrastructure as Code (Terraform)
- ✅ DevOps best practices
- ✅ Real-time prediction serving
- ✅ Cost optimization strategies

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Contributors

Built as an academic project demonstrating enterprise-grade ML integration.

---

## 🆘 Support

- **Issues**: Submit via GitHub Issues
- **Documentation**: See `/docs` folder
- **Cloud Setup Help**: docs/CLOUD_DEPLOYMENT.md
