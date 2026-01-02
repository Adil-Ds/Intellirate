import { useState, useEffect } from 'react';
import apiClient from '@/services/api';

export interface MLInsights {
    pending_recommendations: number;
    applied_recommendations: number;
    total_savings_usd: number;
    avg_confidence: number;
}

export interface ActivityEvent {
    id: number;
    timestamp: string;
    type: string;
    severity: 'success' | 'warning' | 'danger' | 'info';
    description: string;
    user_id: string;
    metadata: {
        endpoint?: string;
        method?: string;
        status_code?: number;
    };
}

export interface CostSummary {
    monthly_cost_usd: number;
    cost_per_request: number;
    trend_percent: number;
    daily_costs: number[];
}

export function useMLInsights() {
    const [data, setData] = useState<MLInsights | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('/api/v1/analytics/ml-insights-summary');
            setData(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch ML insights');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
}

export function useActivityFeed(autoRefresh = true) {
    const [data, setData] = useState<ActivityEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            const response = await apiClient.get('/api/v1/analytics/activity-feed?limit=10');
            setData(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch activity feed');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();

        if (autoRefresh) {
            const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    return { data, loading, error, refetch: fetchData };
}

export function useCostSummary() {
    const [data, setData] = useState<CostSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('/api/v1/analytics/cost-summary');
            setData(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch cost summary');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
}

export interface SystemStatus {
    overall_status: string;
    cloud_provider: string;
    region: string;
    fallback_enabled: boolean;
}

export function useSystemStatus() {
    const [data, setData] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('/api/v1/analytics/system-status');
            setData(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch system status');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
}
