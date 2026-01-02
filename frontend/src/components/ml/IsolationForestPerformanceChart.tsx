import Plot from 'react-plotly.js';
import { Card } from '@/components/ui/Card';
import { ModelMetrics } from '@/hooks/useMLMetrics';

interface IsolationForestPerformanceChartProps {
    metrics: ModelMetrics;
}

export function IsolationForestPerformanceChart({ metrics }: IsolationForestPerformanceChartProps) {
    // Funnel chart showing detection pipeline
    const funnelData: any = [
        {
            type: 'funnel',
            y: ['Total Requests', 'Detected Anomalies', 'True Positives', 'Confirmed Threats'],
            x: [100, metrics.detection_rate, metrics.precision, metrics.f1_score],
            textposition: 'inside',
            textinfo: 'value+percent',
            marker: {
                color: ['#10B981', '#06B6D4', '#8B5CF6', '#EC4899'],
                line: {
                    width: [2, 2, 2, 0],
                    color: ['#0F172A', '#0F172A', '#0F172A', '#0F172A']
                }
            },
            textfont: {
                color: '#FFFFFF',
                size: 14
            },
            connector: {
                line: {
                    color: '#334155',
                    width: 2
                }
            }
        }
    ];

    const funnelLayout = {
        title: {
            text: 'Anomaly Detection Pipeline',
            font: { color: '#E2E8F0', size: 14 }
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 50, b: 40, l: 40, r: 40 },
        font: {
            color: '#E2E8F0',
            family: 'Inter, system-ui, sans-serif'
        },
        height: 300
    };

    // Radar chart for all metrics
    const radarData: any = [
        {
            type: 'scatterpolar',
            r: [
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.detection_rate
            ],
            theta: ['Precision (%)', 'Recall (%)', 'F1 Score (%)', 'Detection Rate (%)'],
            fill: 'toself',
            name: 'Metrics',
            marker: {
                color: '#10B981',
                size: 8
            },
            line: {
                color: '#10B981',
                width: 2
            }
        }
    ];

    const radarLayout = {
        polar: {
            radialaxis: {
                visible: true,
                range: [0, 100],
                gridcolor: '#334155',
                color: '#94A3B8'
            },
            angularaxis: {
                gridcolor: '#334155',
                color: '#E2E8F0'
            },
            bgcolor: 'rgba(15, 23, 42, 0.5)'
        },
        showlegend: false,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 40, b: 40, l: 60, r: 60 },
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
                    data={funnelData}
                    layout={funnelLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                />
            </Card>
            <Card className="p-4">
                <Plot
                    data={radarData}
                    layout={radarLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                />
            </Card>
        </div>
    );
}
