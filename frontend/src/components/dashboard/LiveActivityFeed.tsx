import { motion } from 'framer-motion';
import { Activity, AlertTriangle, CheckCircle, Info, Clock } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { useActivityFeed } from '@/hooks/useDashboardWidgets';
import { formatDistanceToNow } from 'date-fns';

const severityConfig = {
    success: {
        color: 'text-status-success',
        bgColor: 'bg-status-success/10',
        icon: CheckCircle
    },
    warning: {
        color: 'text-status-warning',
        bgColor: 'bg-status-warning/10',
        icon: AlertTriangle
    },
    danger: {
        color: 'text-status-danger',
        bgColor: 'bg-status-danger/10',
        icon: AlertTriangle
    },
    info: {
        color: 'text-neon-cyan',
        bgColor: 'bg-neon-cyan/10',
        icon: Info
    }
};

export function LiveActivityFeed() {
    const { data, loading, error } = useActivityFeed(true); // Auto-refresh enabled

    if (loading && !data.length) {
        return (
            <Card className="animate-pulse">
                <div className="h-96 bg-slate-800/50 rounded"></div>
            </Card>
        );
    }

    if (error && !data.length) {
        return (
            <Card>
                <p className="text-status-danger text-sm">{error}</p>
            </Card>
        );
    }

    return (
        <Card className="relative overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent pointer-events-none" />

            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <div className="p-2 rounded-lg bg-neon-cyan/20">
                            <Activity className="text-neon-cyan" size={20} />
                        </div>
                        <h3 className="text-lg font-semibold text-white">Live Activity</h3>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Clock size={12} />
                        <span>Auto-refresh</span>
                    </div>
                </div>

                {/* Activity Feed */}
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(100, 116, 139, 0.5) transparent' }}>
                    {data.length === 0 ? (
                        <div className="text-center py-8 text-slate-400">
                            <Activity className="mx-auto mb-2 opacity-50" size={32} />
                            <p className="text-sm">No recent activity</p>
                        </div>
                    ) : (
                        data.map((event, index) => {
                            const config = severityConfig[event.severity] || severityConfig.info;
                            const Icon = config.icon;

                            return (
                                <motion.div
                                    key={event.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 transition-colors"
                                >
                                    <div className={`p-1.5 rounded-lg ${config.bgColor} mt-0.5`}>
                                        <Icon className={config.color} size={14} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm text-white leading-snug">
                                            {event.description}
                                        </p>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-xs text-slate-500">
                                                {event.user_id.substring(0, 8)}...
                                            </span>
                                            <span className="text-xs text-slate-600">•</span>
                                            <span className="text-xs text-slate-500">
                                                {event.timestamp ? formatDistanceToNow(new Date(event.timestamp), { addSuffix: true }) : 'Just now'}
                                            </span>
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })
                    )}
                </div>
            </div>
        </Card>
    );
}
