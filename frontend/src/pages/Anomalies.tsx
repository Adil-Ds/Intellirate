import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getAnomalies, getAnomalyStats } from '@/services/api';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } }
};

const item = {
    hidden: { x: -20, opacity: 0 },
    show: { x: 0, opacity: 1 }
};

interface Anomaly {
    id: string;
    type: string;
    severity: string;
    description: string;
    timestamp: string;
    impact: string;
    user_id?: string;
    details?: any;
}

export default function Anomalies() {
    const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
    const [stats, setStats] = useState({ active_anomalies: 0, resolved_today: 0, avg_response_time: '0ms' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [anomaliesData, statsData] = await Promise.all([
                    getAnomalies(),
                    getAnomalyStats()
                ]);
                console.log('🚨 Anomalies:', anomaliesData);
                console.log('📊 Stats:', statsData);
                setAnomalies(anomaliesData.anomalies || []);
                setStats(statsData);
                setLoading(false);
            } catch (error) {
                console.error('Failed to fetch anomalies:', error);
                setLoading(false);
            }
        };

        fetchData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleInvestigate = (anomaly: Anomaly) => {
        // Open logs page filtered by user_id if available
        if (anomaly.user_id) {
            window.open(`/logs?user=${anomaly.user_id}`, '_blank');
        } else {
            // Just open logs page
            window.open('/logs', '_blank');
        }
    };

    const getSeverityStyles = (severity: string) => {
        switch (severity) {
            case 'High':
                return {
                    badge: 'bg-status-danger/20 text-status-danger',
                    icon: 'bg-status-danger/10 text-status-danger',
                    border: 'hover:border-status-danger/30'
                };
            case 'Medium':
                return {
                    badge: 'bg-status-warning/20 text-status-warning',
                    icon: 'bg-status-warning/10 text-status-warning',
                    border: 'hover:border-status-warning/30'
                };
            default:
                return {
                    badge: 'bg-blue-500/20 text-blue-400',
                    icon: 'bg-blue-500/10 text-blue-400',
                    border: 'hover:border-blue-500/30'
                };
        }
    };

    return (
        <motion.div variants={container} animate="show" className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Anomaly Detection
                </h1>
                <p className="text-slate-400 mt-1">AI-powered threat and anomaly monitoring</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="text-center">
                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-status-danger/10 flex items-center justify-center mb-3">
                            <AlertTriangle className="text-status-danger" size={28} />
                        </div>
                        <h3 className="text-3xl font-bold text-white">{anomalies.length}</h3>
                        <p className="text-slate-400 text-sm mt-1">Active Anomalies</p>
                    </div>
                </Card>

                <Card className="text-center">
                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-status-warning/10 flex items-center justify-center mb-3">
                            <TrendingUp className="text-status-warning" size={28} />
                        </div>
                        <h3 className="text-3xl font-bold text-white">{stats.resolved_today}</h3>
                        <p className="text-slate-400 text-sm mt-1">Resolved Today</p>
                    </div>
                </Card>

                <Card className="text-center">
                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-neon-cyan/10 flex items-center justify-center mb-3">
                            <Clock className="text-neon-cyan" size={28} />
                        </div>
                        <h3 className="text-3xl font-bold text-white">{stats.avg_response_time}</h3>
                        <p className="text-slate-400 text-sm mt-1">Avg Response Time</p>
                    </div>
                </Card>
            </div>

            {loading ? (
                <div className="text-center text-slate-400 py-12">
                    <p>Loading anomalies...</p>
                </div>
            ) : anomalies.length === 0 ? (
                <Card>
                    <div className="text-center py-12">
                        <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mb-4 mx-auto">
                            <TrendingUp className="text-green-400" size={28} />
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">All Clear!</h3>
                        <p className="text-slate-400">No anomalies detected in your traffic</p>
                    </div>
                </Card>
            ) : (
                <div className="space-y-4">
                    {anomalies.map((anomaly) => {
                        const styles = getSeverityStyles(anomaly.severity);
                        return (
                            <motion.div key={anomaly.id} variants={item}>
                                <Card className={`${styles.border} transition-all`}>
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex items-start gap-4 flex-1">
                                            <div className={`p-3 rounded-lg ${styles.icon}`}>
                                                <AlertTriangle size={24} />
                                            </div>
                                            <div className="flex-1 space-y-2">
                                                <div className="flex items-center gap-3">
                                                    <h3 className="text-lg font-semibold text-white">{anomaly.type}</h3>
                                                    <span className={`text-xs px-3 py-1 rounded-full font-semibold ${styles.badge}`}>
                                                        {anomaly.severity}
                                                    </span>
                                                </div>
                                                <p className="text-slate-300 text-sm leading-relaxed">{anomaly.description}</p>
                                                <div className="flex items-center gap-2 text-sm">
                                                    <span className="text-slate-500">{anomaly.timestamp}</span>
                                                    <span className="text-slate-600">•</span>
                                                    <span className="text-neon-cyan font-medium">{anomaly.impact}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleInvestigate(anomaly)}
                                            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-semibold transition-all hover:scale-105 whitespace-nowrap"
                                        >
                                            Investigate
                                        </button>
                                    </div>
                                </Card>
                            </motion.div>
                        );
                    })}
                </div>
            )}
        </motion.div>
    );
}
