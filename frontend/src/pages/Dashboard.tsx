import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Activity, Users, AlertTriangle, Zap } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { MLInsightsHub } from '@/components/dashboard/MLInsightsHub';
import { LiveActivityFeed } from '@/components/dashboard/LiveActivityFeed';
import { CostSummary } from '@/components/dashboard/CostSummary';
import { SystemStatusTable } from '@/components/dashboard/SystemStatusTable';
import { useDashboardMetrics } from '@/hooks/useAnalytics';
import { cn } from '@/utils';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
};

// Helper function to format large numbers
const formatNumber = (num: number): string => {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};

export default function Dashboard() {
    const { data: metrics, loading, error } = useDashboardMetrics();

    // Calculate derived values with real data
    const totalRequests = metrics?.total_requests || 0;
    const avgLatency = metrics?.avg_latency_ms ? Math.round(metrics.avg_latency_ms) : 0;
    const activeUsers = metrics?.active_users || 0;

    // Format values for display
    const displayMetrics = {
        totalRequests: {
            value: formatNumber(totalRequests),
            trend: '+0%', // TODO: Calculate from historical data
        },
        avgLatency: {
            value: `${avgLatency}ms`,
            trend: '-0%', // TODO: Calculate from historical data  
        },
        anomalies: {
            value: '0', // TODO: Integrate ML anomaly detection
            trend: '+0',
        },
        activeUsers: {
            value: activeUsers.toString(),
            trend: '+0%', // TODO: Calculate from historical data
        },
    };
    return (
        <motion.div
            variants={container}
            animate="show"
            className="space-y-6"
        >
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">Dashboard</h1>
                    <p className="text-slate-400 mt-1">Real-time gateway monitoring</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="flex h-2 w-2 rounded-full bg-status-success animate-pulse-slow"></span>
                    <span className="text-sm font-medium text-status-success">System Operational</span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {loading ? (
                    <div className="col-span-full text-center text-slate-400">Loading metrics...</div>
                ) : error ? (
                    <div className="col-span-full text-center text-status-danger">Failed to load metrics</div>
                ) : (
                    <>
                        <MetricCard
                            title="Total Requests"
                            value={displayMetrics.totalRequests.value}
                            trend={displayMetrics.totalRequests.trend}
                            icon={Zap}
                            color="text-neon-cyan"
                        />
                        <MetricCard
                            title="Avg Latency"
                            value={displayMetrics.avgLatency.value}
                            trend={displayMetrics.avgLatency.trend}
                            icon={Activity}
                            color="text-neon-purple"
                        />
                        <MetricCard
                            title="Anomalies"
                            value={displayMetrics.anomalies.value}
                            trend={displayMetrics.anomalies.trend}
                            icon={AlertTriangle}
                            color="text-status-danger"
                        />
                        <MetricCard
                            title="Active Users"
                            value={displayMetrics.activeUsers.value}
                            trend={displayMetrics.activeUsers.trend}
                            icon={Users}
                            color="text-neon-pink"
                        />
                    </>
                )}
            </div>


            {/* Hybrid Dashboard Widgets - Unified Height Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
                {/* Column 1: ML Insights + System Status */}
                <div className="flex flex-col gap-6 h-full">
                    <MLInsightsHub />
                    <div className="flex-1">
                        <SystemStatusTable />
                    </div>
                </div>

                {/* Column 2: Live Activity Feed */}
                <div className="flex flex-col h-full">
                    <LiveActivityFeed />
                </div>

                {/* Column 3: Cost Summary + System Load */}
                <div className="flex flex-col gap-6 h-full">
                    <CostSummary />

                    {/* System Load Widget */}
                    <Card className="flex flex-col items-center justify-center relative flex-1">
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-neon-purple/5 pointer-events-none" />
                        <div className="relative z-10 text-center py-8">
                            <div className="w-32 h-32 rounded-full border-4 border-slate-700/50 flex items-center justify-center relative mb-4 mx-auto">
                                <svg className="absolute inset-0 w-full h-full -rotate-90 transform">
                                    <circle
                                        className="text-slate-700/50"
                                        strokeWidth="8"
                                        stroke="currentColor"
                                        fill="transparent"
                                        r="60"
                                        cx="64"
                                        cy="64"
                                    />
                                    <circle
                                        className="text-neon-purple transition-all duration-1000 ease-out"
                                        strokeWidth="8"
                                        strokeDasharray={2 * Math.PI * 60}
                                        strokeDashoffset={2 * Math.PI * 60 * (1 - 0.76)}
                                        strokeLinecap="round"
                                        stroke="currentColor"
                                        fill="transparent"
                                        r="60"
                                        cx="64"
                                        cy="64"
                                    />
                                </svg>
                                <div className="text-center">
                                    <span className="text-3xl font-bold text-white">76%</span>
                                    <p className="text-xs text-slate-400 uppercase tracking-widest mt-1">Load</p>
                                </div>
                            </div>
                            <h3 className="text-base font-semibold text-white">System Load</h3>
                            <p className="text-xs text-slate-400 mt-1 px-4">Current RPM vs Plan Limits</p>
                        </div>
                    </Card>
                </div>
            </div>
        </motion.div>
    );
}

function MetricCard({ title, value, trend, icon: Icon, color }: any) {
    const trendColor = (title === 'Anomalies' && trend.startsWith('+')) || (title === 'Avg Latency' && trend.startsWith('+'))
        ? 'text-status-danger'
        : 'text-status-success';

    const TrendIcon = trend.startsWith('+') ? ArrowUpRight : ArrowDownRight;

    return (
        <motion.div variants={item}>
            <Card>
                <div className="flex justify-between items-start mb-4">
                    <div className={cn("p-2 rounded-lg bg-white/5", color)}>
                        <Icon size={20} />
                    </div>
                    <div className={cn("flex items-center gap-1 text-sm font-medium", trendColor)}>
                        {trend}
                        <TrendIcon size={14} />
                    </div>
                </div>
                <div>
                    <h3 className="text-3xl font-bold text-white mb-1">{value}</h3>
                    <p className="text-sm text-slate-400">{title}</p>
                </div>
            </Card>
        </motion.div>
    )
}
