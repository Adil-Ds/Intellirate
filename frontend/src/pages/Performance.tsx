import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, Shield, GitCompare } from 'lucide-react';
import Plot from 'react-plotly.js';
import { Card } from '@/components/ui/Card';
import { useMLMetrics } from '@/hooks/useMLMetrics';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

type TabType = 'prophet' | 'xgboost' | 'isolation_forest' | 'comparison';

export default function Performance() {
    const { metrics, loading } = useMLMetrics();
    const [activeTab, setActiveTab] = useState<TabType>('comparison');

    const tabs = [
        { id: 'comparison' as const, name: 'Comparison', icon: GitCompare },
        { id: 'prophet' as const, name: 'Prophet', icon: TrendingUp },
        { id: 'xgboost' as const, name: 'XGBoost', icon: Target },
        { id: 'isolation_forest' as const, name: 'Isolation Forest', icon: Shield },
    ];

    if (loading || !metrics) {
        return (
            <div className="flex items-center justify-center h-96">
                <p className="text-slate-400">Loading performance metrics...</p>
            </div>
        );
    }

    // Comparison Charts
    const renderComparisonView = () => {
        // Accuracy/R² Comparison
        const accuracyData: any = [
            {
                type: 'bar',
                x: ['Prophet', 'XGBoost', 'Isolation Forest'],
                y: [
                    metrics.prophet.metrics.r2 * 100,
                    metrics.xgboost.metrics.accuracy,
                    (metrics.isolation_forest.metrics.f1_score + metrics.isolation_forest.metrics.precision + metrics.isolation_forest.metrics.recall) / 3
                ],
                name: 'Overall Performance',
                marker: {
                    color: ['#06B6D4', '#A855F7', '#10B981'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${(metrics.prophet.metrics.r2 * 100).toFixed(1)}%`,
                    `${metrics.xgboost.metrics.accuracy.toFixed(1)}%`,
                    `${((metrics.isolation_forest.metrics.f1_score + metrics.isolation_forest.metrics.precision + metrics.isolation_forest.metrics.recall) / 3).toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const accuracyLayout: any = {
            title: { text: 'Overall Model Performance Comparison', font: { color: '#E2E8F0', size: 18 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8', tickfont: { size: 12 } },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Performance (%)', font: { color: '#94A3B8' } },
                range: [0, 100]
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 60, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 400
        };

        // Precision Comparison
        const precisionData: any = [
            {
                type: 'bar',
                x: ['XGBoost', 'Isolation Forest'],
                y: [
                    metrics.xgboost.metrics.precision * 100,
                    metrics.isolation_forest.metrics.precision
                ],
                name: 'Precision',
                marker: {
                    color: ['#A855F7', '#10B981'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${(metrics.xgboost.metrics.precision * 100).toFixed(1)}%`,
                    `${metrics.isolation_forest.metrics.precision.toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const precisionLayout: any = {
            title: { text: 'Precision Comparison', font: { color: '#E2E8F0', size: 18 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8' },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Precision (%)', font: { color: '#94A3B8' } },
                range: [0, 100]
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 60, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 400
        };

        // Recall Comparison
        const recallData: any = [
            {
                type: 'bar',
                x: ['XGBoost', 'Isolation Forest'],
                y: [
                    metrics.xgboost.metrics.recall * 100,
                    metrics.isolation_forest.metrics.recall
                ],
                name: 'Recall',
                marker: {
                    color: ['#EC4899', '#06B6D4'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${(metrics.xgboost.metrics.recall * 100).toFixed(1)}%`,
                    `${metrics.isolation_forest.metrics.recall.toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const recallLayout: any = {
            title: { text: 'Recall Comparison', font: { color: '#E2E8F0', size: 18 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8' },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Recall (%)', font: { color: '#94A3B8' } },
                range: [0, 100]
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 60, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 400
        };

        return (
            <div className="space-y-6">
                <Card className="p-6">
                    <Plot
                        data={accuracyData}
                        layout={accuracyLayout}
                        config={{ responsive: true, displayModeBar: false }}
                        style={{ width: '100%' }}
                    />
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="p-6">
                        <Plot
                            data={precisionData}
                            layout={precisionLayout}
                            config={{ responsive: true, displayModeBar: false }}
                            style={{ width: '100%' }}
                        />
                    </Card>

                    <Card className="p-6">
                        <Plot
                            data={recallData}
                            layout={recallLayout}
                            config={{ responsive: true, displayModeBar: false }}
                            style={{ width: '100%' }}
                        />
                    </Card>
                </div>
            </div>
        );
    };

    // Prophet Charts
    const renderProphetView = () => {
        const metricsData: any = [
            {
                type: 'bar',
                x: ['MAPE', 'MAE', 'RMSE', 'R² Score', 'Coverage'],
                y: [
                    metrics.prophet.metrics.mape,
                    metrics.prophet.metrics.mae,
                    metrics.prophet.metrics.rmse,
                    metrics.prophet.metrics.r2 * 100,
                    metrics.prophet.metrics.coverage
                ],
                marker: {
                    color: ['#06B6D4', '#3B82F6', '#8B5CF6', '#10B981', '#EC4899'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${metrics.prophet.metrics.mape.toFixed(2)}%`,
                    metrics.prophet.metrics.mae.toFixed(2),
                    metrics.prophet.metrics.rmse.toFixed(2),
                    `${(metrics.prophet.metrics.r2 * 100).toFixed(1)}%`,
                    `${metrics.prophet.metrics.coverage.toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const layout: any = {
            title: { text: 'Prophet Model Metrics', font: { color: '#E2E8F0', size: 20 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8' },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Value', font: { color: '#94A3B8' } }
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 80, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 500
        };

        return (
            <Card className="p-6">
                <Plot
                    data={metricsData}
                    layout={layout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                />
            </Card>
        );
    };

    // XGBoost Charts
    const renderXGBoostView = () => {
        const metricsData: any = [
            {
                type: 'bar',
                x: ['Accuracy', 'Precision', 'Recall', 'MAE', 'R² Score'],
                y: [
                    metrics.xgboost.metrics.accuracy,
                    metrics.xgboost.metrics.precision * 100,
                    metrics.xgboost.metrics.recall * 100,
                    metrics.xgboost.metrics.mae,
                    metrics.xgboost.metrics.r2 * 100
                ],
                marker: {
                    color: ['#A855F7', '#EC4899', '#8B5CF6', '#06B6D4', '#10B981'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${metrics.xgboost.metrics.accuracy.toFixed(1)}%`,
                    `${(metrics.xgboost.metrics.precision * 100).toFixed(1)}%`,
                    `${(metrics.xgboost.metrics.recall * 100).toFixed(1)}%`,
                    metrics.xgboost.metrics.mae.toFixed(2),
                    `${(metrics.xgboost.metrics.r2 * 100).toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const layout: any = {
            title: { text: 'XGBoost Model Metrics', font: { color: '#E2E8F0', size: 20 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8' },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Value', font: { color: '#94A3B8' } }
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 80, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 500
        };

        return (
            <Card className="p-6">
                <Plot
                    data={metricsData}
                    layout={layout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                />
            </Card>
        );
    };

    // Isolation Forest Charts
    const renderIsolationForestView = () => {
        const metricsData: any = [
            {
                type: 'bar',
                x: ['Precision', 'Recall', 'F1 Score', 'Detection Rate'],
                y: [
                    metrics.isolation_forest.metrics.precision,
                    metrics.isolation_forest.metrics.recall,
                    metrics.isolation_forest.metrics.f1_score,
                    metrics.isolation_forest.metrics.detection_rate
                ],
                marker: {
                    color: ['#10B981', '#06B6D4', '#8B5CF6', '#EC4899'],
                    line: { color: '#0F172A', width: 2 }
                },
                text: [
                    `${metrics.isolation_forest.metrics.precision.toFixed(1)}%`,
                    `${metrics.isolation_forest.metrics.recall.toFixed(1)}%`,
                    `${metrics.isolation_forest.metrics.f1_score.toFixed(1)}%`,
                    `${metrics.isolation_forest.metrics.detection_rate.toFixed(1)}%`
                ],
                textposition: 'outside',
                textfont: { color: '#E2E8F0', size: 14 }
            }
        ];

        const layout: any = {
            title: { text: 'Isolation Forest Model Metrics', font: { color: '#E2E8F0', size: 20 } },
            xaxis: { gridcolor: '#334155', color: '#94A3B8' },
            yaxis: {
                gridcolor: '#334155',
                color: '#94A3B8',
                title: { text: 'Percentage (%)', font: { color: '#94A3B8' } },
                range: [0, 100]
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            margin: { t: 60, b: 80, l: 70, r: 40 },
            font: { color: '#E2E8F0', family: 'Inter, system-ui, sans-serif' },
            height: 500
        };

        return (
            <Card className="p-6">
                <Plot
                    data={metricsData}
                    layout={layout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                />
            </Card>
        );
    };

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-6"
        >
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 flex items-center gap-2">
                    <BarChart3 className="text-neon-cyan" size={32} />
                    Performance Analytics
                </h1>
                <p className="text-slate-400 mt-1">Deep dive into model performance metrics and comparisons</p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${isActive
                                    ? 'bg-gradient-to-r from-neon-purple to-neon-cyan text-white shadow-lg shadow-neon-purple/30'
                                    : 'bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-700/50'
                                }`}
                        >
                            <Icon size={18} />
                            <span className="font-medium">{tab.name}</span>
                        </button>
                    );
                })}
            </div>

            {/* Tab Content */}
            <div className="fadeIn">
                {activeTab === 'comparison' && renderComparisonView()}
                {activeTab === 'prophet' && renderProphetView()}
                {activeTab === 'xgboost' && renderXGBoostView()}
                {activeTab === 'isolation_forest' && renderIsolationForestView()}
            </div>
        </motion.div>
    );
}
