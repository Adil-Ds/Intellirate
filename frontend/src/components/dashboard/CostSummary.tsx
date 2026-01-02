import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { useCostSummary } from '@/hooks/useDashboardWidgets';

export function CostSummary() {
    const { data, loading, error } = useCostSummary();

    if (loading) {
        return (
            <Card className="animate-pulse">
                <div className="h-48 bg-slate-800/50 rounded"></div>
            </Card>
        );
    }

    if (error) {
        return (
            <Card>
                <p className="text-status-danger text-sm">{error}</p>
            </Card>
        );
    }

    const TrendIcon = data && data.trend_percent >= 0 ? TrendingUp : TrendingDown;
    const trendColor = data && data.trend_percent >= 0 ? 'text-status-danger' : 'text-status-success';

    return (
        <Card className="relative overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-neon-pink/5 to-transparent pointer-events-none" />

            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <div className="p-2 rounded-lg bg-neon-pink/20">
                            <DollarSign className="text-neon-pink" size={20} />
                        </div>
                        <h3 className="text-lg font-semibold text-white">Cost Summary</h3>
                    </div>
                </div>

                {/* Main Cost */}
                <div className="mb-4">
                    <p className="text-sm text-slate-400 mb-1">Monthly Cost</p>
                    <h2 className="text-3xl font-bold text-white mb-2">
                        ${data?.monthly_cost_usd?.toFixed(2) || '0.00'}
                    </h2>
                    <div className={`flex items-center gap-1 text-sm ${trendColor}`}>
                        <TrendIcon size={16} />
                        <span>{data?.trend_percent || 0}% vs last month</span>
                    </div>
                </div>

                {/* Additional Metrics */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30">
                        <span className="text-sm text-slate-400">Cost per Request</span>
                        <span className="text-sm font-semibold text-white">
                            ${data?.cost_per_request?.toFixed(4) || '0.0000'}
                        </span>
                    </div>

                    {/* Sparkline */}
                    {data && data.daily_costs && data.daily_costs.length > 0 && (
                        <div className="p-3 rounded-lg bg-slate-800/30">
                            <p className="text-xs text-slate-400 mb-2">30-Day Trend</p>
                            <div className="flex items-end gap-1 h-12">
                                {data.daily_costs.map((cost, index) => {
                                    const maxCost = Math.max(...data.daily_costs);
                                    const height = maxCost > 0 ? (cost / maxCost) * 100 : 0;
                                    return (
                                        <motion.div
                                            key={index}
                                            initial={{ height: 0 }}
                                            animate={{ height: `${height}%` }}
                                            transition={{ delay: index * 0.01 }}
                                            className="flex-1 bg-gradient-to-t from-neon-pink to-neon-purple rounded-sm min-h-[2px]"
                                            title={`$${cost.toFixed(2)}`}
                                        />
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </Card>
    );
}
