import { useState, useEffect } from 'react';
import apiClient from '@/services/api';

export interface ModelMetrics {
    [key: string]: number;
}

export interface ModelData {
    metrics: ModelMetrics;
    version: string;
    last_trained: string;
}

export interface MLMetricsData {
    prophet: ModelData;
    xgboost: ModelData;
    isolation_forest: ModelData;
}

export function useMLMetrics() {
    const [metrics, setMetrics] = useState<MLMetricsData | null>(null);
    const [oldMetrics, setOldMetrics] = useState<MLMetricsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchMetrics = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('/api/v1/ml/metrics/summary');
            setMetrics(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch ML metrics');
        } finally {
            setLoading(false);
        }
    };

    const saveOldMetrics = () => {
        if (metrics) {
            setOldMetrics(metrics);
        }
    };

    useEffect(() => {
        fetchMetrics();
    }, []);

    return { metrics, oldMetrics, loading, error, fetchMetrics, saveOldMetrics };
}
