# IntelliRate Frontend

Modern React dashboard for the IntelliRate Gateway ML API.

## Features

- 🎨 Beautiful glassmorphism UI design
- 📊 Real-time health monitoring dashboard
- 🛡️ Abuse detection testing interface
- ⚡ Rate limit optimization
- 📈 Traffic forecasting visualization
- 🔄 Live API integration with backend

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Tech Stack

- React 18
- Vite
- Axios
- Modern CSS with custom variables
- Glassmorphism design

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` and provides interfaces for:

- ML health monitoring
- Abuse detection testing
- Rate limit optimization
- Traffic forecasting

See `src/services/api.js` for API documentation.
