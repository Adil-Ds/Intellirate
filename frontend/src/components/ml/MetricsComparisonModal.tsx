import { X, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { BatchRetrainResults } from '@/hooks/useModelRetrain';

interface MetricsComparisonModalProps {
    isOpen: boolean;
    onClose: () => void;
    results: BatchRetrainResults | null;
}

export function MetricsComparisonModal({
    isOpen,
    onClose,
    results
}: MetricsComparisonModalProps) {
    if (!isOpen || !results) return null;

    const calculateImprovement = (before: number, after: number) => {
        const change = ((after - before) / before) * 100;
        return change;
    };

    const getImprovementIcon = (change: number) => {
        if (Math.abs(change) < 0.5) return <Minus className="text-slate-400" size={16} />;
        if (change > 0) return <TrendingUp className="text-status-success bounceArrow" size={16} />;
        return <TrendingDown className="text-status-danger bounceArrow" size={16} />;
    };

    const getChangeColor = (change: number) => {
        if (Math.abs(change) < 0.5) return 'text-slate-400';
        if (change > 0) return 'text-status-success';
        return 'text-status-danger';
    };

    const modelNames: { [key: string]: string } = {
        prophet: 'Prophet',
        xgboost: 'XGBoost',
        isolation_forest: 'Isolation Forest'
    };

    const metricLabels: { [key: string]: { [key: string]: string } } = {
        prophet: {
            mape: 'MAPE',
            mae: 'MAE',
            rmse: 'RMSE',
            r2: 'R² Score',
            coverage: 'Coverage'
        },
        xgboost: {
            accuracy: 'Accuracy',
            precision: 'Precision',
            recall: 'Recall',
            mae: 'MAE',
            r2: 'R² Score'
        },
        isolation_forest: {
            precision: 'Precision',
            recall: 'Recall',
            f1_score: 'F1 Score',
            detection_rate: 'Detection Rate'
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto slideUp">
                {/* Header */}
                <div className="flex items-center justify-between mb-6 sticky top-0 bg-slate-900/95 pb-4 border-b border-slate-700/50">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Model Retraining Results</h2>
                        <p className="text-sm text-slate-400 mt-1">Before vs After Comparison</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
                    >
                        <X className="text-slate-400" size={20} />
                    </button>
                </div>

                {/* Results for each model */}
                <div className="space-y-6">
                    {Object.entries(results.results).map(([modelKey, result]) => {
                        if (!result || !result.success) return null;

                        return (
                            <div key={modelKey} className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/50">
                                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                    {modelNames[modelKey]}
                                    <span className="text-xs text-slate-400 font-normal">({result.version})</span>
                                </h3>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {Object.entries(result.before).map(([metricKey, beforeValue]) => {
                                        const afterValue = result.after[metricKey];
                                        const improvement = calculateImprovement(beforeValue, afterValue);
                                        const isErrorMetric = metricKey.includes('mape') || metricKey.includes('mae') || metricKey.includes('rmse');
                                        const effectiveImprovement = isErrorMetric ? -improvement : improvement;

                                        return (
                                            <div key={metricKey} className="p-4 rounded-lg bg-slate-900/50">
                                                <p className="text-xs text-slate-400 mb-2">
                                                    {metricLabels[modelKey]?.[metricKey] || metricKey}
                                                </p>

                                                <div className="flex items-center justify-between mb-2">
                                                    <div>
                                                        <p className="text-xs text-slate-500">Before</p>
                                                        <p className="text-lg font-semibold text-slate-300">
                                                            {beforeValue < 1 ? beforeValue.toFixed(3) : beforeValue.toFixed(2)}
                                                        </p>
                                                    </div>

                                                    <div className="flex items-center gap-1">
                                                        {getImprovementIcon(effectiveImprovement)}
                                                        <span className={`text-sm font-semibold ${getChangeColor(effectiveImprovement)}`}>
                                                            {effectiveImprovement > 0 ? '+' : ''}{effectiveImprovement.toFixed(1)}%
                                                        </span>
                                                    </div>

                                                    <div>
                                                        <p className="text-xs text-slate-500">After</p>
                                                        <p className="text-lg font-semibold text-white pulseValue">
                                                            {afterValue < 1 ? afterValue.toFixed(3) : afterValue.toFixed(2)}
                                                        </p>
                                                    </div>
                                                </div>

                                                {/* Progress bar */}
                                                {Math.abs(effectiveImprovement) > 0.5 && (
                                                    <div className="mt-2">
                                                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                                            <div
                                                                className={`h-full expandBar ${effectiveImprovement > 0
                                                                        ? 'bg-gradient-to-r from-status-success to-neon-cyan'
                                                                        : 'bg-gradient-to-r from-status-danger to-orange-500'
                                                                    }`}
                                                                style={{
                                                                    width: `${Math.min(Math.abs(effectiveImprovement), 100)}%`
                                                                }}
                                                            />
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Close button */}
                <div className="mt-6 pt-4 border-t border-slate-700/50">
                    <button
                        onClick={onClose}
                        className="w-full px-6 py-3 bg-gradient-to-r from-neon-purple to-neon-cyan text-white rounded-lg hover:opacity-90 transition-opacity font-semibold"
                    >
                        Close
                    </button>
                </div>
            </Card>
        </div>
    );
}
