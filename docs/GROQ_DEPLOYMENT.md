# IntelliRate API Gateway - Groq Integration Deployment Guide

## Overview

The IntelliRate Gateway now acts as a complete proxy between the AI Data Analyzer frontend and Groq API, capturing **ALL** traffic for analytics while enforcing authentication and rate limiting.

## Quick Start

### 1. Environment Setup

Copy the `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required Environment Variables:**

```env
# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

# Firebase Admin SDK
FIREBASE_PROJECT_ID=dataanlyzer
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@dataanlyzer.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n[YOUR_PRIVATE_KEY_HERE]\n-----END PRIVATE KEY-----"


# Database
DATABASE_URL=postgresql://intellirate_user:intellirate_pass@localhost:5432/intellirate_db

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS - Add your analyzer frontend origins
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://dataanlyzer.web.app","https://dataanlyzer.firebaseapp.com"]

# Rate Limits (requests per minute by tier)
RATE_LIMIT_FREE=10
RATE_LIMIT_PRO=100
RATE_LIMIT_ENTERPRISE=1000
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Setup

Start PostgreSQL and Redis:

```bash
docker-compose up -d postgres redis
```

Run migrations:

```bash
cd backend
alembic upgrade head
```

This creates the `request_logs` table for traffic capture.

### 4. Run the Gateway

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The gateway will be available at `http://localhost:8000`.

### 5. Verify Installation

Check health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "groq": "configured",
    "database": "connected"
  },
  "features": {
    "groq_proxy_enabled": true
  }
}
```

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Main Endpoints

### 1. POST /api/v1/analyze

**Purpose**: Proxy AI analysis requests to Groq API

**Headers**:
```
Authorization: Bearer <firebase-id-token>
X-User-Id: <firebase-uid>
X-User-Email: <user-email>
Content-Type: application/json
```

**Request Body**:
```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response** (pass-through from Groq):
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    }
  }],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 8,
    "total_tokens": 28
  }
}
```

### 2. GET /api/v1/analytics/user/{user_id}

Get analytics for a specific user:

```bash
curl http://localhost:8000/api/v1/analytics/user/firebase-uid-123
```

Response:
```json
{
  "user_id": "firebase-uid-123",
  "total_requests": 150,
  "total_tokens": 45000,
  "avg_latency_ms": 850.5,
  "success_rate": 0.98,
  "last_request": "2025-12-24T15:00:00Z"
}
```

### 3. GET /api/v1/analytics/usage

Get system-wide analytics:

```bash
curl http://localhost:8000/api/v1/analytics/usage?days=30
```

Response:
```json
{
  "period": "last_30_days",
  "total_requests": 5000,
  "total_tokens": 1500000,
  "unique_users": 50,
  "avg_tokens_per_request": 300
}
```

## Testing

### Test 1: Unauthorized Request

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.3-70b-versatile", "messages": []}'
```

Expected: `401 Unauthorized`

### Test 2: Valid Request (requires Firebase token)

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer <your-firebase-token>" \
  -H "X-User-Id: <your-uid>" \
  -H "X-User-Email: user@example.com" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "test"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

Expected: `200 OK` with AI response

### Test 3: Database Logging

After making requests, verify logging:

```sql
SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT 5;
```

You should see all requests logged with:
- User information
- Request parameters
- Token usage
- Latency metrics

## Frontend Integration

Update your AI Data Analyzer frontend to use the gateway:

```javascript
// Before (direct Groq call)
const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
  headers: {
    'Authorization': `Bearer ${GROQ_API_KEY}`, // Exposed!
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(request)
});

// After (via gateway)
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  headers: {
    'Authorization': `Bearer ${firebaseToken}`, // Firebase token
    'X-User-Id': user.uid,
    'X-User-Email': user.email,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(request)
});
```

## Rate Limiting

The gateway enforces per-user rate limits:

- **Free tier**: 10 requests/minute
- **Pro tier**: 100 requests/minute
- **Enterprise**: 1000 requests/minute

Tiers are determined by Firebase custom claims (`tier` field).

When limit exceeded, you'll receive:

```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT",
  "retry_after": 42
}
```

## Traffic Visibility

Every request is logged to the `request_logs` table, capturing:

✅ User ID and email  
✅ Timestamp  
✅ Model and parameters  
✅ Token usage (prompt, completion, total)  
✅ Latency (total and Groq-specific)  
✅ Success/error status  
✅ IP address and user agent  

This enables:
- Per-user usage tracking
- Token-based billing
- Performance monitoring
- Error rate analysis
- Security auditing

## Deployment to Production

### Option 1: Docker

```bash
docker-compose up -d
```

### Option 2: Cloud Platforms

**Heroku**:
```bash
git push heroku main
```

**Google Cloud Run**:
```bash
gcloud run deploy intellirate-gateway --source .
```

**AWS ECS** - Use the Dockerfile provided

### Environment Variables in Production

Ensure all sensitive variables are set securely:
- Use secrets manager for `GROQ_API_KEY` and `FIREBASE_PRIVATE_KEY`
- Set `DEBUG=false`
- Update `BACKEND_CORS_ORIGINS` with production URLs

## Troubleshooting

### Firebase Authentication Fails

- Verify `FIREBASE_PRIVATE_KEY` is properly formatted (including `\n`)
- Check `FIREBASE_PROJECT_ID` matches your Firebase project
- Ensure Firebase Admin SDK is installed: `pip install firebase-admin`

### Database Connection Issues

- Verify PostgreSQL is running: `docker-compose ps`
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Run migrations: `alembic upgrade head`

### Redis Connection Issues

- Verify Redis is running: `docker-compose ps`
- Test connection: `redis-cli ping`
- Check `REDIS_URL` format: `redis://host:port/db`

### Groq API Errors

- Verify `GROQ_API_KEY` is correct
- Check Groq API status: https://status.groq.com
- Review logs for specific error messages

## Architecture

```
AI Data Analyzer Frontend
         ↓
   [Firebase Auth]
         ↓
IntelliRate Gateway (This Project)
   ├─ Firebase Token Validation
   ├─ Rate Limiting (Redis)
   ├─ Request Logging (PostgreSQL)
   ├─ Groq API Proxy
   └─ Response Logging (PostgreSQL)
         ↓
     Groq API
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
