import { Cloud, MapPin, RefreshCw, Activity } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { useSystemStatus } from '@/hooks/useDashboardWidgets';

const statusColors = {
    operational: 'text-status-success',
    cloud_disabled: 'text-slate-400',
    degraded: 'text-status-warning',
    offline: 'text-status-danger'
};

export function SystemStatusCards() {
    const { data, loading, error } = useSystemStatus();

    console.log('SystemStatusCards:', { data, loading, error });

    if (loading && !data) {
        return (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                    <Card key={i} className="animate-pulse h-24">
                        <div className="h-full bg-slate-800/50 rounded"></div>
                    </Card>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="col-span-full p-4">
                    <p className="text-status-danger text-sm">Failed to load system status: {error}</p>
                </Card>
            </div>
        );
    }

    if (!data) {
        return null;
    }

    const cards = [
        {
            id: 'overall_status',
            label: 'Overall Status',
            value: data.overall_status === 'operational' ? 'Operational' : data.overall_status.replace('_', ' '),
            icon: Activity,
            color: statusColors[data.overall_status as keyof typeof statusColors] || 'text-slate-400',
            bgColor: data.overall_status === 'operational' ? 'bg-status-success/10' : 'bg-slate-700/30'
        },
        {
            id: 'cloud_provider',
            label: 'Cloud Provider',
            value: data.cloud_provider,
            icon: Cloud,
            color: 'text-neon-cyan',
            bgColor: 'bg-neon-cyan/10'
        },
        {
            id: 'region',
            label: 'Region',
            value: data.region,
            icon: MapPin,
            color: 'text-neon-purple',
            bgColor: 'bg-neon-purple/10'
        },
        {
            id: 'fallback',
            label: 'Fallback',
            value: data.fallback_enabled ? 'Enabled' : 'Disabled',
            icon: RefreshCw,
            color: data.fallback_enabled ? 'text-status-success' : 'text-status-danger',
            bgColor: data.fallback_enabled ? 'bg-status-success/10' : 'bg-status-danger/10'
        }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map((card) => {
                const Icon = card.icon;
                return (
                    <Card key={card.id} className="relative overflow-hidden">
                        <div className={`absolute inset-0 ${card.bgColor} opacity-50 pointer-events-none`} />
                        <div className="relative z-10 flex items-center gap-3 p-4">
                            <div className={`p-2 rounded-lg ${card.bgColor}`}>
                                <Icon className={card.color} size={20} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs text-slate-400 mb-0.5">{card.label}</p>
                                <p className={`text-sm font-semibold ${card.color} truncate`}>
                                    {card.value}
                                </p>
                            </div>
                        </div>
                    </Card>
                );
            })}
        </div>
    );
}
