import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Health check
export const healthCheck = async () => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
};

// Analytics
export const getTrafficData = async () => {
    const response = await apiClient.get('/api/v1/traffic');
    return response.data;
};

export const getTrafficStats = async () => {
    const response = await apiClient.get('/api/v1/traffic/stats');
    return response.data;
};

export const getDashboardMetrics = async () => {
    const response = await apiClient.get('/api/v1/traffic/stats');
    return response.data;
};

export const getUserStats = async () => {
    const response = await apiClient.get('/api/v1/users/stats');
    return response.data;
};

// Logs
export const getLogs = async (limit = 100) => {
    const response = await apiClient.get('/api/v1/logs', { params: { limit } });
    return response.data;
};

// ML/Anomalies
export const getAnomalies = async () => {
    const response = await apiClient.get('/api/v1/anomalies');
    return response.data;
};

export const getAnomalyStats = async () => {
    const response = await apiClient.get('/api/v1/anomalies/stats');
    return response.data;
};

export const getForecast = async () => {
    const response = await apiClient.get('/api/v1/traffic/forecast');
    return response.data;
};

// Rate Limits
export const getRateLimitTiers = async () => {
    const response = await apiClient.get('/api/v1/rate-limits/tiers');
    return response.data;
};

export const getRateLimitUsers = async (tier?: string) => {
    const params = tier ? { tier } : {};
    const response = await apiClient.get('/api/v1/rate-limits/users', { params });
    return response.data;
};

export const getRateLimitEvents = async (limit = 20, userId?: string) => {
    const params: any = { limit };
    if (userId) params.user_id = userId;
    const response = await apiClient.get('/api/v1/rate-limits/events', { params });
    return response.data;
};

export const getMLRateLimitRecommendation = async (userId: string) => {
    const response = await apiClient.get(`/api/v1/rate-limits/user/${userId}/ml-recommendation`);
    return response.data;
};

export const updateUserRateLimit = async (userId: string, limit: number, tier: string) => {
    const response = await apiClient.put(`/api/v1/rate-limits/user/${userId}`, { limit, tier });
    return response.data;
};

export default apiClient;
