import { Cloud, MapPin, RefreshCw, Activity } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { useSystemStatus } from '@/hooks/useDashboardWidgets';

const statusColors = {
    operational: 'text-status-success',
    cloud_disabled: 'text-slate-400',
    degraded: 'text-status-warning',
    offline: 'text-status-danger'
};

export function SystemStatusTable() {
    const { data, loading, error } = useSystemStatus();

    if (loading && !data) {
        return (
            <Card className="animate-pulse">
                <div className="h-48 bg-slate-800/50 rounded"></div>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="p-4">
                <p className="text-status-danger text-sm">Failed to load system status</p>
            </Card>
        );
    }

    if (!data) {
        return null;
    }

    const statusItems = [
        {
            id: 'overall_status',
            label: 'Overall Status',
            value: data.overall_status === 'operational' ? 'Operational' : 'Cloud Disabled',
            icon: Activity,
            color: statusColors[data.overall_status as keyof typeof statusColors] || 'text-slate-400',
            bgColor: data.overall_status === 'operational' ? 'bg-status-success/20' : 'bg-slate-700/20'
        },
        {
            id: 'cloud_provider',
            label: 'Cloud Provider',
            value: data.cloud_provider,
            icon: Cloud,
            color: 'text-neon-cyan',
            bgColor: 'bg-neon-cyan/20'
        },
        {
            id: 'region',
            label: 'Region',
            value: data.region,
            icon: MapPin,
            color: 'text-neon-purple',
            bgColor: 'bg-neon-purple/20'
        },
        {
            id: 'fallback',
            label: 'Fallback',
            value: data.fallback_enabled ? 'Enabled' : 'Disabled',
            icon: RefreshCw,
            color: data.fallback_enabled ? 'text-status-success' : 'text-status-danger',
            bgColor: data.fallback_enabled ? 'bg-status-success/20' : 'bg-status-danger/20'
        }
    ];

    return (
        <Card className="overflow-hidden">
            <div className="divide-y divide-slate-700/50">
                {statusItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <div
                            key={item.id}
                            className="flex items-center justify-between px-4 py-3 hover:bg-slate-800/30 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${item.bgColor}`}>
                                    <Icon className={item.color} size={16} />
                                </div>
                                <span className="text-sm text-slate-400">{item.label}</span>
                            </div>
                            <span className={`text-sm font-semibold ${item.color}`}>
                                {item.value}
                            </span>
                        </div>
                    );
                })}
            </div>
        </Card>
    );
}
