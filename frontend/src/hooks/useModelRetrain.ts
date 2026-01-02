import { useState } from 'react';
import apiClient from '@/services/api';
import { MLMetricsData } from './useMLMetrics';

export interface RetrainResult {
    success: boolean;
    message: string;
    before: { [key: string]: number };
    after: { [key: string]: number };
    version: string;
}

export interface BatchRetrainResults {
    success: boolean;
    message: string;
    results: {
        prophet?: RetrainResult;
        xgboost?: RetrainResult;
        isolation_forest?: RetrainResult;
    };
}

export function useModelRetrain() {
    const [retraining, setRetraining] = useState(false);
    const [retrainResults, setRetrainResults] = useState<BatchRetrainResults | null>(null);
    const [error, setError] = useState<string | null>(null);

    const retrainModels = async (models: string[]) => {
        try {
            setRetraining(true);
            setError(null);

            // Call batch retrain endpoint
            const response = await apiClient.post('/api/v1/ml/retrain/batch', models);
            setRetrainResults(response.data);

            return response.data;
        } catch (err: any) {
            const errorMsg = err.message || 'Failed to retrain models';
            setError(errorMsg);
            throw new Error(errorMsg);
        } finally {
            setRetraining(false);
        }
    };

    const resetResults = () => {
        setRetrainResults(null);
        setError(null);
    };

    return { retraining, retrainResults, error, retrainModels, resetResults };
}
