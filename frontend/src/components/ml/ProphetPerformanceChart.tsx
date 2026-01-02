import Plot from 'react-plotly.js';
import { Card } from '@/components/ui/Card';
import { ModelMetrics } from '@/hooks/useMLMetrics';

interface ProphetPerformanceChartProps {
    metrics: ModelMetrics;
}

export function ProphetPerformanceChart({ metrics }: ProphetPerformanceChartProps) {
    // Radar chart for Prophet metrics
    const radarData: any = [
        {
            type: 'scatterpolar',
            r: [
                100 - metrics.mape, // Invert MAPE (lower is better)
                100 - (metrics.mae / 50) * 100, // Normalize MAE
                100 - (metrics.rmse / 60) * 100, // Normalize RMSE
                metrics.r2 * 100, // R² as percentage
                metrics.coverage // Coverage percentage
            ],
            theta: ['MAPE (inv)', 'MAE (inv)', 'RMSE (inv)', 'R² Score', 'Coverage'],
            fill: 'toself',
            name: 'Metrics',
            marker: {
                color: '#06B6D4',
                size: 8
            },
            line: {
                color: '#06B6D4',
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
        }
    };

    // Bar chart for error metrics
    const barData: any = [
        {
            type: 'bar',
            x: ['MAPE (%)', 'MAE', 'RMSE'],
            y: [metrics.mape, metrics.mae, metrics.rmse],
            marker: {
                color: ['#06B6D4', '#3B82F6', '#8B5CF6'],
                line: {
                    color: '#0F172A',
                    width: 1.5
                }
            },
            text: [
                `${metrics.mape.toFixed(2)}%`,
                metrics.mae.toFixed(2),
                metrics.rmse.toFixed(2)
            ],
            textposition: 'outside',
            textfont: {
                color: '#E2E8F0'
            }
        }
    ];

    const barLayout = {
        title: {
            text: 'Error Metrics (Lower is Better)',
            font: { color: '#E2E8F0', size: 14 }
        },
        xaxis: {
            gridcolor: '#334155',
            color: '#94A3B8'
        },
        yaxis: {
            gridcolor: '#334155',
            color: '#94A3B8',
            title: { text: 'Value', font: { color: '#94A3B8' } }
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
        margin: { t: 50, b: 50, l: 60, r: 40 },
        font: {
            color: '#E2E8F0',
            family: 'Inter, system-ui, sans-serif'
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-4">
                <Plot
                    data={radarData}
                    layout={radarLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                />
            </Card>
            <Card className="p-4">
                <Plot
                    data={barData}
                    layout={barLayout}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                />
            </Card>
        </div>
    );
}
