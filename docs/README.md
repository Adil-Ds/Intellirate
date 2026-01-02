# 📚 IntelliRate Gateway Documentation

Welcome to the IntelliRate Gateway documentation! This directory contains all project documentation organized for easy navigation.

---

## 📖 Quick Navigation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5-30 minutes
  - Local development setup (no cloud required)
  - AWS SageMaker deployment
  - Troubleshooting common issues

### Deployment Guides
- **[Groq Integration Deployment](GROQ_DEPLOYMENT.md)** - Complete guide for Groq API proxy setup
  - Environment configuration
  - Firebase authentication setup
  - Rate limiting configuration
  - Traffic logging and analytics
  - Frontend integration examples

- **[AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)** - Step-by-step AWS SageMaker setup
  - SageMaker endpoint deployment
  - Model versioning and rollback
  - Cost optimization strategies
  
- **[Cloud Deployment Overview](CLOUD_DEPLOYMENT.md)** - Comprehensive cloud ML integration
  - Architecture overview
  - Prerequisites and setup
  - Monitoring and maintenance
  
- **[Cloud Setup Guide](CLOUD_SETUP_GUIDE.md)** - AWS credentials and infrastructure setup

### Project Overview
- **[Project Walkthrough](PROJECT_WALKTHROUGH.md)** - Complete system overview
  - Architecture diagram and explanation
  - Component breakdown
  - Data flow and request lifecycle
  - Key features demonstration

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│              (AI Data Analyzer, Web Apps, etc.)              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 IntelliRate Gateway (FastAPI)                │
│  ┌──────────────┬───────────────┬────────────────────────┐  │
│  │ Firebase Auth│ Rate Limiting │  Traffic Analytics     │  │
│  │              │   (Redis)     │   (PostgreSQL)         │  │
│  └──────────────┴───────────────┴────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Groq API     │ │ AWS         │ │ Local ML     │
│ Proxy        │ │ SageMaker   │ │ Models       │
│              │ │ Endpoints   │ │ (Fallback)   │
└──────────────┘ └─────────────┘ └──────────────┘
```

---

## 🎯 Documentation by Use Case

### I want to run the project locally
→ Start with **[Quick Start Guide](QUICKSTART.md)** (Option 1)

### I want to deploy to AWS
→ Follow **[AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)** and **[Cloud Setup Guide](CLOUD_SETUP_GUIDE.md)**

### I want to integrate with Groq API
→ See **[Groq Integration Deployment](GROQ_DEPLOYMENT.md)**

### I want to understand the architecture
→ Read **[Project Walkthrough](PROJECT_WALKTHROUGH.md)** and **[Cloud Deployment Overview](CLOUD_DEPLOYMENT.md)**

### I need to troubleshoot issues
→ Check troubleshooting sections in **[Quick Start Guide](QUICKSTART.md)**

---

## 📁 Additional Documentation Locations

- **Frontend Documentation**: `../frontend/README.md`
  - React dashboard setup
  - Component documentation
  - UI/UX guidelines

- **Backend API Documentation**: Available when running the backend
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

## 🔑 Key Concepts

### Machine Learning Models
The IntelliRate Gateway integrates three ML models:

1. **Isolation Forest** - Anomaly detection for abuse prevention
2. **XGBoost** - Dynamic rate limit optimization
3. **Prophet** - Traffic forecasting

### Deployment Modes
- **Local Mode** (`USE_CLOUD_ML=false`) - Uses local sklearn models
- **Cloud Mode** (`USE_CLOUD_ML=true`) - Uses AWS SageMaker endpoints
- **Hybrid Mode** (`ENABLE_ML_FALLBACK=true`) - Automatic fallback to local models

### Core Features
- ✅ Real-time abuse detection
- ✅ Dynamic rate limiting per user tier
- ✅ Traffic forecasting and analytics
- ✅ Firebase authentication
- ✅ Groq API proxying
- ✅ Request logging and analytics

---

## 🚀 Quick Links

| Resource | Link |
|----------|------|
| Main README | `../README.md` |
| Quick Start | [QUICKSTART.md](QUICKSTART.md) |
| Groq Setup | [GROQ_DEPLOYMENT.md](GROQ_DEPLOYMENT.md) |
| AWS Setup | [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) |
| Cloud Overview | [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) |
| Frontend Docs | `../frontend/README.md` |

---

## 📞 Support

For issues or questions:
- Review the troubleshooting sections in each guide
- Check the [main README](../README.md) for common issues
- Submit issues on GitHub

---

## 📝 Documentation Maintenance

This documentation is organized as follows:
- **Setup & Installation** - Getting started guides
- **Deployment** - Cloud and production deployment
- **Integration** - Third-party service integration
- **Architecture** - System design and concepts

Last updated: 2025-12-30
