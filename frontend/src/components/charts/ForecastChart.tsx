import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useForecast } from '@/hooks/useForecast';
import { useLiveTraffic } from '@/hooks/useLiveTraffic';
import { Card } from '@/components/ui/Card';

export function ForecastChart() {
    const { data: forecast, loading, error } = useForecast();
    const liveData = useLiveTraffic(24);

    console.log('🔮 Forecast data:', forecast);

    // Combine historical (actual) with forecast (predicted)

    // Add last 12 actual data points
    const recentActual = liveData.slice(-12).map(item => ({
        time: item.time,
        actual: item.value,
        predicted: null
    }));

    // Add forecast predictions
    const predictions = forecast?.predictions?.map((item: any) => ({
        time: new Date(item.time).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }),
        actual: null,
        predicted: item.predicted
    })) || [];

    const combinedData = [...recentActual, ...predictions];

    return (
        <Card className="h-[400px] flex flex-col">
            <div className="mb-4">
                <h3 className="text-lg font-semibold text-white">Traffic Forecast (1hr)</h3>
                <p className="text-sm text-slate-400">ML-powered predictions</p>
            </div>
            <div className="flex-1 min-h-0 h-[320px]">
                {loading ? (
                    <div className="flex items-center justify-center h-full text-slate-400">
                        Loading forecast...
                    </div>
                ) : error ? (
                    <div className="flex items-center justify-center h-full text-status-danger">
                        Failed to load forecast
                    </div>
                ) : combinedData.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-slate-400">
                        <div className="text-center">
                            <p>Building forecast model...</p>
                            <p className="text-sm mt-2">Need at least 3 hours of traffic data</p>
                        </div>
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={combinedData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                            <XAxis
                                dataKey="time"
                                stroke="#64748B"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                stroke="#64748B"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(3, 0, 20, 0.9)',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Line
                                type="monotone"
                                dataKey="actual"
                                stroke="#06B6D4"
                                strokeWidth={2}
                                dot={false}
                                name="Actual"
                                connectNulls={false}
                            />
                            <Line
                                type="monotone"
                                dataKey="predicted"
                                stroke="#7C3AED"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                                name="Predicted"
                                connectNulls={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </div>
        </Card>
    );
}
