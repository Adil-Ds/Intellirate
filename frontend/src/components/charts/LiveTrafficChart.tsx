import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useLiveTraffic } from '@/hooks/useLiveTraffic';
import { Card } from '@/components/ui/Card';

export function LiveTrafficChart() {
    const data = useLiveTraffic(24);
    console.log('📈 LiveTrafficChart rendering with data length:', data.length);
    console.log('📈 LiveTrafficChart data:', data);

    return (
        <Card className="h-[400px] w-full flex flex-col">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-white">Real-time Traffic</h3>
                    <p className="text-sm text-slate-400">Requests per hour</p>
                </div>
                <span className="px-2 py-1 text-xs font-semibold text-neon-cyan bg-neon-cyan/20 rounded">LIVE</span>
            </div>
            <div className="flex-1 w-full min-h-0 h-[320px]">
                {data.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-slate-400">
                        No traffic data available
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                                </linearGradient>
                            </defs>
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
                                domain={['auto', 'auto']}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(3, 0, 20, 0.9)',
                                    border: '1px solid rgba(6, 182, 212, 0.3)',
                                    borderRadius: '8px',
                                    boxShadow: '0 0 10px rgba(6, 182, 212, 0.2)'
                                }}
                                itemStyle={{ color: '#06B6D4' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke="#06B6D4"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorValue)"
                                isAnimationActive={false}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>
        </Card>
    );
}
