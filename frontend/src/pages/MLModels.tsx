import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, Target, Shield, RefreshCw } from 'lucide-react';
import { ModelMetricCard } from '@/components/ml/ModelMetricCard';
import { RetrainModelsModal } from '@/components/ml/RetrainModelsModal';
import { MetricsComparisonModal } from '@/components/ml/MetricsComparisonModal';
import { useMLMetrics } from '@/hooks/useMLMetrics';
import { useModelRetrain } from '@/hooks/useModelRetrain';
import { useToast } from '@/components/providers/ToastContext';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

export default function MLModels() {
    const { metrics, loading, error, fetchMetrics, saveOldMetrics } = useMLMetrics();
    const { retraining, retrainResults, retrainModels, resetResults } = useModelRetrain();
    const { showToast } = useToast();
    const [showRetrainModal, setShowRetrainModal] = useState(false);
    const [showComparisonModal, setShowComparisonModal] = useState(false);

    const handleRetrain = async (models: string[]) => {
        try {
            saveOldMetrics();
            await retrainModels(models);
            setShowRetrainModal(false);
            setShowComparisonModal(true);
            showToast('Models retrained successfully!', 'success');
            await fetchMetrics();
        } catch (err: any) {
            showToast(err.message || 'Failed to retrain models', 'error');
        }
    };

    const handleCloseComparison = () => {
        setShowComparisonModal(false);
        resetResults();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <RefreshCw className="animate-spin text-neon-cyan mx-auto mb-4" size={40} />
                    <p className="text-slate-400">Loading ML metrics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <p className="text-status-danger mb-4">{error}</p>
                    <button
                        onClick={fetchMetrics}
                        className="px-4 py-2 bg-neon-cyan text-white rounded-lg hover:opacity-90"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!metrics) return null;

    const metricLabels = {
        prophet: {
            mape: 'MAPE (%)',
            mae: 'MAE',
            rmse: 'RMSE',
            r2: 'R² Score',
            coverage: 'Coverage (%)'
        },
        xgboost: {
            accuracy: 'Accuracy (%)',
            precision: 'Precision',
            recall: 'Recall',
            mae: 'MAE',
            r2: 'R² Score'
        },
        isolation_forest: {
            precision: 'Precision (%)',
            recall: 'Recall (%)',
            f1_score: 'F1 Score (%)',
            detection_rate: 'Detection Rate (%)'
        }
    };

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-6"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 flex items-center gap-2">
                        <Sparkles className="text-neon-purple" size={32} />
                        ML Model Metrics
                    </h1>
                    <p className="text-slate-400 mt-1">Monitor model performance and trigger retraining</p>
                </div>
                <button
                    onClick={() => setShowRetrainModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-neon-purple to-neon-cyan text-white rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2 font-semibold shadow-lg shadow-neon-purple/30"
                >
                    <RefreshCw size={18} />
                    Retrain Models
                </button>
            </div>

            {/* Model Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Prophet Card */}
                <ModelMetricCard
                    modelName="Prophet"
                    icon={<TrendingUp className="text-neon-cyan" size={24} />}
                    metrics={metrics.prophet.metrics}
                    version={metrics.prophet.version}
                    lastTrained={metrics.prophet.last_trained}
                    gradientFrom="#06B6D4"
                    gradientTo="#3B82F6"
                    metricLabels={metricLabels.prophet}
                />

                {/* XGBoost Card */}
                <ModelMetricCard
                    modelName="XGBoost"
                    icon={<Target className="text-neon-purple" size={24} />}
                    metrics={metrics.xgboost.metrics}
                    version={metrics.xgboost.version}
                    lastTrained={metrics.xgboost.last_trained}
                    gradientFrom="#A855F7"
                    gradientTo="#EC4899"
                    metricLabels={metricLabels.xgboost}
                />

                {/* Isolation Forest Card */}
                <ModelMetricCard
                    modelName="Isolation Forest"
                    icon={<Shield className="text-status-success" size={24} />}
                    metrics={metrics.isolation_forest.metrics}
                    version={metrics.isolation_forest.version}
                    lastTrained={metrics.isolation_forest.last_trained}
                    gradientFrom="#10B981"
                    gradientTo="#06B6D4"
                    metricLabels={metricLabels.isolation_forest}
                />
            </div>

            {/* Modals */}
            <RetrainModelsModal
                isOpen={showRetrainModal}
                onClose={() => setShowRetrainModal(false)}
                onRetrain={handleRetrain}
                retraining={retraining}
            />

            <MetricsComparisonModal
                isOpen={showComparisonModal}
                onClose={handleCloseComparison}
                results={retrainResults}
            />
        </motion.div>
    );
}
