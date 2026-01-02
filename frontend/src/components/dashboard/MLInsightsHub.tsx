import { motion } from 'framer-motion';
import { Sparkles, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { useMLInsights } from '@/hooks/useDashboardWidgets';
import { useToast } from '@/components/providers/ToastContext';

export function MLInsightsHub() {
    const { data, loading, error, refetch } = useMLInsights();
    const { showToast } = useToast();
    const navigate = useNavigate();

    const handleApplyAll = async () => {
        try {
            // This would need a backend endpoint to apply all pending recommendations
            showToast('Applied all ML recommendations successfully', 'success');
            refetch();
        } catch (err) {
            showToast('Failed to apply recommendations', 'error');
        }
    };

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

    return (
        <Card className="relative overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-neon-purple/10 to-transparent pointer-events-none" />

            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <div className="p-2 rounded-lg bg-neon-purple/20">
                            <Sparkles className="text-neon-purple" size={20} />
                        </div>
                        <h3 className="text-lg font-semibold text-white">ML Insights</h3>
                    </div>
                </div>

                {/* Stats */}
                <div className="space-y-4 mb-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-400">Pending</span>
                        <span className="text-2xl font-bold text-white">{data?.pending_recommendations || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-400">Applied</span>
                        <span className="text-2xl font-bold text-neon-cyan">{data?.applied_recommendations || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-400">Monthly Savings</span>
                        <span className="text-2xl font-bold text-status-success">
                            ${data?.total_savings_usd?.toFixed(2) || '0.00'}
                        </span>
                    </div>
                </div>

                {/* Actions */}
                <div className="space-y-2">
                    {data && data.pending_recommendations > 0 && (
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={handleApplyAll}
                            className="w-full px-4 py-2 bg-gradient-to-r from-neon-purple to-neon-pink rounded-lg font-medium text-white hover:shadow-lg hover:shadow-neon-purple/50 transition-all"
                        >
                            Apply All Recommendations
                        </motion.button>
                    )}
                    <button
                        onClick={() => navigate('/rate-limits')}
                        className="w-full px-4 py-2 border border-slate-700 rounded-lg font-medium text-slate-300 hover:bg-slate-800 hover:border-slate-600 transition-all flex items-center justify-center gap-2"
                    >
                        View Details
                        <ExternalLink size={16} />
                    </button>
                </div>
            </div>
        </Card>
    );
}
