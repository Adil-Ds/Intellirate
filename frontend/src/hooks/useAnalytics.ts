import { useEffect, useState } from 'react';
import { getUserStats, getTrafficData, getLogs, getAnomalies, getDashboardMetrics } from '@/services/api';

interface UseDataResult<T> {
    data: T | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
}

export const useSystemAnalytics = (): UseDataResult<any> => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getTrafficData();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
};

export const useUserAnalytics = (): UseDataResult<any> => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getUserStats();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
};

export const useSystemLogs = (limit = 100): UseDataResult<any[]> => {
    const [data, setData] = useState<any[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getLogs(limit);
            console.log('📋 Logs API Response:', result);
            console.log('📋 Logs is array?', Array.isArray(result));
            console.log('📋 Logs length:', result?.length);
            setData(result);
            setError(null);
        } catch (err) {
            console.error('❌ Logs fetch error:', err);
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [limit]);

    return { data, loading, error, refetch: fetchData };
};

export const useAnomalies = (): UseDataResult<any[]> => {
    const [data, setData] = useState<any[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getAnomalies();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
};

export const useDashboardMetrics = (): UseDataResult<any> => {
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getDashboardMetrics();
            console.log('📊 Dashboard Metrics Response:', result);
            setData(result);
            setError(null);
        } catch (err) {
            console.error('❌ Dashboard metrics error:', err);
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    return { data, loading, error, refetch: fetchData };
};
