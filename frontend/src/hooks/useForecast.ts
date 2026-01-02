import { useState, useEffect } from 'react';
import { getForecast } from '@/services/api';

interface UseForecastResult {
    data: any | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
}

export const useForecast = (): UseForecastResult => {
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await getForecast();
            console.log('🔮 Forecast API Response:', result);
            setData(result);
            setError(null);
        } catch (err) {
            console.error('❌ Forecast fetch error:', err);
            setError(err as Error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Auto-refresh every 60 seconds (forecasts don't change as frequently)
        const interval = setInterval(fetchData, 60000);
        return () => clearInterval(interval);
    }, []);

    return { data, loading, error, refetch: fetchData };
};
