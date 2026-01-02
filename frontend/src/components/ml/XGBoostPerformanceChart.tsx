import Plot from 'react-plotly.js';
import { Card } from '@/components/ui/Card';
import { ModelMetrics } from '@/hooks/useMLMetrics';

interface XGBoostPerformanceChartProps {
    metrics: ModelMetrics;
}

export function XGBoostPerformanceChart({ metrics }: XGBoostPerformanceChartProps) {
    // Gauge chart for accuracy
    const gaugeData: any = [
        {
            type: 'indicator',
            mode: 'gauge+number+delta',
            value: metrics.accuracy,
            title: { text: 'Accuracy (%)', font: { color: '#E2E8F0', size: 16 } },
            delta: { reference: 90, increasing: { color: '#10B981' } },
            gauge: {
                axis: { range: [0, 100], tickcolor: '#94A3B8' },
                bar: { color: '#A855F7' },
                bgcolor: 'rgba(15, 23, 42, 0.5)',
                borderwidth: 2,
                bordercolor: '#334155',
                steps: [
                    { range: [0, 60], color: 'rgba(239, 68, 68, 0.2)' },
                    { range: [60, 80], color: 'rgba(251, 191, 36, 0.2)' },
                    { range: [80, 100], color: 'rgba(16, 185, 129, 0.2)' }
                ],
                threshold: {
                    line: { color: '#10B981', width: 4 },
                    thickness: 0.75,
                    value: 95
                }
            }
        }
    ];

    const gaugeLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 40, b: 20, l: 40, r: 40 },
        font: {
            color: '#E2E8F0',
            family: 'Inter, system-ui, sans-serif'
        },
        height: 250
    };

    // Bar chart for precision, recall, R²
    const metricsBarData: any = [
        {
            type: 'bar',
            x: ['Precision', 'Recall', 'R² Score'],
            y: [
                metrics.precision * 100,
                metrics.recall * 100,
                metrics.r2 * 100
            ],
            marker: {
                color: ['#A855F7', '#EC4899', '#8B5CF6'],
                line: {
                    color: '#0F172A',
                    width: 1.5
                }
            },
            text: [
                `${(metrics.precision * 100).toFixed(1)}%`,
                `${(metrics.recall * 100).toFixed(1)}%`,
                `${(metrics.r2 * 100).toFixed(1)}%`
            ],
            textposition: 'outside',
            textfont: {
                color: '#E2E8F0',
                size: 12
            }
        }
    ];

    const metricsBarLayout = {
        title: {
            text: 'Classification Metrics',
            font: { color: '#E2E8F0', size: 14 }
        },
        xaxis: {
            gridcolor: '#334155',
            color: '#94A3B8'
        },
        yaxis: {
            gridcolor: '#334155',
            color: '#94A3B8',
            title: { text: 'Percentage', font: { color: '#94A3B8' } },
            range: [0, 100]
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
        margin: { t: 50, b: 50, l: 60, r: 40 },
        font: {
            color: '#E2E8F0',
            family: 'Inter, system-ui, sans-serif'
        },
        height: 300
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-4">
                <Plot
                    data={gaugeData}
                    layout={gaugeLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '250px' }}
                />
            </Card>
            <Card className="p-4">
                <Plot
                    data={metricsBarData}
                    layout={metricsBarLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                />
            </Card>
        </div>
    );
}
