import { ReactNode, useState } from 'react';
import { ChevronDown, ChevronUp, BarChart3 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { ModelMetrics } from '@/hooks/useMLMetrics';

interface ModelMetricCardProps {
    modelName: string;
    icon: ReactNode;
    metrics: ModelMetrics;
    version: string;
    lastTrained: string;
    gradientFrom: string;
    gradientTo: string;
    metricLabels: { [key: string]: string };
    chartComponent?: ReactNode;
}

export function ModelMetricCard({
    modelName,
    icon,
    metrics,
    version,
    lastTrained,
    gradientFrom,
    gradientTo,
    metricLabels,
    chartComponent
}: ModelMetricCardProps) {
    const [showCharts, setShowCharts] = useState(false);

    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch {
            return dateString;
        }
    };

    const getMetricColor = (key: string, value: number) => {
        // For error metrics (lower is better)
        if (key.includes('mape') || key.includes('mae') || key.includes('rmse')) {
            if (value < 20) return 'text-status-success';
            if (value < 40) return 'text-status-warning';
            return 'text-status-danger';
        }
        // For accuracy metrics (higher is better)
        if (value > 90) return 'text-status-success';
        if (value > 75) return 'text-status-warning';
        return 'text-status-danger';
    };

    return (
        <div className="fadeIn">
            <Card className="relative overflow-hidden border-2 hover:border-opacity-50 transition-all"
                style={{ borderColor: `${gradientFrom}40` }}>
                {/* Gradient background */}
                <div
                    className="absolute inset-0 opacity-10"
                    style={{
                        background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`
                    }}
                />

                <div className="relative z-10">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div
                                className="p-3 rounded-lg"
                                style={{
                                    background: `linear-gradient(135deg, ${gradientFrom}20, ${gradientTo}20)`,
                                    boxShadow: `0 0 20px ${gradientFrom}40`
                                }}
                            >
                                {icon}
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-white">{modelName}</h3>
                                <p className="text-xs text-slate-400">{version}</p>
                            </div>
                        </div>
                    </div>

                    {/* Metrics */}
                    <div className="space-y-3">
                        {Object.entries(metrics).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">
                                    {metricLabels[key] || key}
                                </span>
                                <span className={`text-base font-semibold ${getMetricColor(key, value)}`}>
                                    {typeof value === 'number' ? (
                                        value < 1 ? value.toFixed(3) : value.toFixed(2)
                                    ) : value}
                                    {key.includes('accuracy') || key.includes('precision') || key.includes('recall')
                                        || key.includes('coverage') || key.includes('detection') || key.includes('mape')
                                        ? '%' : ''}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Footer */}
                    <div className="mt-6 pt-4 border-t border-slate-700/50 space-y-3">
                        <p className="text-xs text-slate-500">
                            Last trained: {formatDate(lastTrained)}
                        </p>

                        {/* Show Charts Button */}
                        {chartComponent && (
                            <button
                                onClick={() => setShowCharts(!showCharts)}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-all"
                                style={{
                                    background: showCharts
                                        ? `linear-gradient(135deg, ${gradientFrom}30, ${gradientTo}30)`
                                        : `linear-gradient(135deg, ${gradientFrom}10, ${gradientTo}10)`,
                                    borderColor: `${gradientFrom}50`,
                                    borderWidth: '1px'
                                }}
                            >
                                <BarChart3 size={16} className="text-white" />
                                <span className="text-sm font-medium text-white">
                                    {showCharts ? 'Hide' : 'Show'} Performance Charts
                                </span>
                                {showCharts ? (
                                    <ChevronUp size={16} className="text-white" />
                                ) : (
                                    <ChevronDown size={16} className="text-white" />
                                )}
                            </button>
                        )}
                    </div>
                </div>
            </Card>

            {/* Expandable Charts Section */}
            {showCharts && chartComponent && (
                <div className="mt-4 slideUp">
                    {chartComponent}
                </div>
            )}
        </div>
    );
}
