import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { CircularProgressCard } from '@/components/ui/CircularProgress';
import { useToast } from '@/components/providers/ToastContext';
import {
    TrendingUp,
    TrendingDown,
    Sparkles,
    Edit2,
    Save,
    X,
    AlertTriangle,
    CheckCircle,
    Clock,
    Loader2,
    BarChart3,
    Shield,
    Activity,
    Key
} from 'lucide-react';
import {
    getRateLimitTiers,
    getRateLimitUsers,
    getRateLimitEvents,
    getMLRateLimitRecommendation,
    updateUserRateLimit
} from '@/services/api';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } }
};

interface TierData {
    name: string;
    limit: number;
    users: number;
    total_usage: number;
    features: string[];
}

interface UserRateLimit {
    user_id: string;
    user_email: string | null;
    tier: string;
    limit: number;
    current_usage: number;
    usage_percentage: number;
    ml_recommended_limit?: number;
    ml_confidence?: number;
    last_active: string | null;
}

interface RateLimitEvent {
    event_id: string;
    user_id: string;
    user_email: string | null;
    event_type: string;
    timestamp: string;
    usage_percentage: number;
    current_limit: number;
}

interface MLRecommendation {
    user_id: string;
    current_limit: number;
    recommended_limit: number;
    confidence: number;
    reasoning: string;
    potential_savings?: number;
    recommendation_type: string;
}

export default function RateLimits() {
    const { showToast } = useToast();

    // State
    const [tiers, setTiers] = useState<TierData[]>([]);
    const [users, setUsers] = useState<UserRateLimit[]>([]);
    const [events, setEvents] = useState<RateLimitEvent[]>([]);
    const [selectedTier] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [editingUser, setEditingUser] = useState<string | null>(null);
    const [editLimit, setEditLimit] = useState<number>(0);
    const [editTier, setEditTier] = useState<string>('');
    const [mlRecommendation, setMlRecommendation] = useState<MLRecommendation | null>(null);
    const [showMLModal, setShowMLModal] = useState(false);
    const [loadingML, setLoadingML] = useState(false);
    const [sortBy, setSortBy] = useState<'usage' | 'tier' | 'user_id'>('usage');

    // Fetch data
    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [tiersData, usersData, eventsData] = await Promise.all([
                getRateLimitTiers(),
                getRateLimitUsers(selectedTier || undefined),
                getRateLimitEvents(20)
            ]);

            setTiers(tiersData.tiers || []);
            setUsers(usersData.users || []);
            setEvents(eventsData.events || []);
        } catch (error) {
            console.error('Error fetching rate limit data:', error);
            showToast('Failed to load rate limit data', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();

        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [selectedTier]);

    // Get ML recommendation
    const handleGetMLRecommendation = async (userId: string) => {
        setLoadingML(true);
        try {
            const recommendation = await getMLRateLimitRecommendation(userId);
            setMlRecommendation(recommendation);
            setShowMLModal(true);
        } catch (error: any) {
            showToast(error.response?.data?.detail || 'Failed to get ML recommendation', 'error');
        } finally {
            setLoadingML(false);
        }
    };

    // Apply ML recommendation
    const applyMLRecommendation = async () => {
        if (!mlRecommendation) return;

        try {
            // Ensure minimum limit of 10 on frontend as well
            const finalLimit = Math.max(10, mlRecommendation.recommended_limit);

            await updateUserRateLimit(
                mlRecommendation.user_id,
                finalLimit,
                determineTierFromLimit(finalLimit)
            );
            showToast('Rate limit updated successfully', 'success');
            setShowMLModal(false);
            setMlRecommendation(null);
            fetchData();
        } catch (error) {
            showToast('Failed to update rate limit', 'error');
        }
    };

    // Start editing
    const startEdit = (user: UserRateLimit) => {
        setEditingUser(user.user_id);
        setEditLimit(user.limit);
        setEditTier(user.tier);
    };

    // Save edit
    const saveEdit = async (userId: string) => {
        try {
            await updateUserRateLimit(userId, editLimit, editTier);
            showToast('Rate limit updated successfully', 'success');
            setEditingUser(null);
            fetchData();
        } catch (error) {
            showToast('Failed to update rate limit', 'error');
        }
    };

    // Cancel edit
    const cancelEdit = () => {
        setEditingUser(null);
    };

    // Helper functions
    const determineTierFromLimit = (limit: number): string => {
        if (limit >= 500000) return 'enterprise';
        if (limit >= 50000) return 'pro';
        return 'free';
    };



    const getTierColor = (tierName: string) => {
        const name = tierName.toLowerCase();
        if (name === 'free') return { text: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/20' };
        if (name === 'pro') return { text: 'text-neon-cyan', bg: 'bg-neon-cyan/10', border: 'border-neon-cyan/20' };
        return { text: 'text-neon-purple', bg: 'bg-neon-purple/10', border: 'border-neon-purple/20' };
    };

    const getUsageColor = (percentage: number) => {
        if (percentage >= 90) return 'bg-red-500';
        if (percentage >= 70) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    const getEventColor = (eventType: string) => {
        if (eventType === 'breach') return 'text-red-400 bg-red-500/10 border-red-500/20';
        if (eventType === 'warning') return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
        return 'text-green-400 bg-green-500/10 border-green-500/20';
    };

    // Sort users
    const sortedUsers = [...users].sort((a, b) => {
        if (sortBy === 'usage') return b.usage_percentage - a.usage_percentage;
        if (sortBy === 'tier') return a.tier.localeCompare(b.tier);
        return a.user_id.localeCompare(b.user_id);
    });

    return (
        <motion.div variants={container} initial="hidden" animate="show" className="space-y-3">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Rate Limits
                    </h1>
                    <p className="text-slate-400 mt-1">Manage API rate limits with ML-powered optimization</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchData}
                        className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors text-sm flex items-center gap-2"
                    >
                        <Clock size={16} className={isLoading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Circular Progress Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <CircularProgressCard
                    title="Global Limit Usage"
                    percentage={(() => {
                        // Calculate global usage percentage across all tiers
                        const totalUsage = tiers.reduce((sum, tier) => sum + tier.total_usage, 0);
                        const totalLimit = tiers.reduce((sum, tier) => sum + (tier.limit * tier.users), 0);
                        return totalLimit > 0 ? (totalUsage / totalLimit) * 100 : 0;
                    })()}
                    description={`${users.reduce((sum, u) => sum + u.current_usage, 0).toLocaleString()} of system capacity`}
                    color="#fbbf24"
                    icon={<BarChart3 size={20} />}
                />

                <CircularProgressCard
                    title="Anomalous Traffic"
                    percentage={(() => {
                        // Calculate percentage of users with anomalous behavior (>90% usage)
                        const anomalousUsers = users.filter(u => u.usage_percentage > 90).length;
                        return users.length > 0 ? (anomalousUsers / users.length) * 100 : 0;
                    })()}
                    description={`${users.filter(u => u.usage_percentage > 90).length} users exceeding limits`}
                    color="#06b6d4"
                    icon={<Activity size={20} />}
                />

                <CircularProgressCard
                    title="API Token Bucket"
                    percentage={(() => {
                        // Calculate average usage across all users
                        const avgUsage = users.length > 0
                            ? users.reduce((sum, u) => sum + u.usage_percentage, 0) / users.length
                            : 0;
                        return avgUsage;
                    })()}
                    description={`${users.length} active users consuming tokens`}
                    color="#00d9ff"
                    icon={<Key size={20} />}
                />
            </div>

            {/* Tier Overview Cards - Removed to eliminate spacing */}

            {/* Users Table */}
            <Card>
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <BarChart3 className="text-neon-cyan" size={20} />
                        <h3 className="text-lg font-semibold text-white">User Rate Limits</h3>
                        {selectedTier && (
                            <span className="px-2 py-1 bg-neon-cyan/10 text-neon-cyan text-xs rounded-full">
                                Filtered: {selectedTier}
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-400">Sort by:</span>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as any)}
                            className="bg-slate-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-neon-cyan/50 cursor-pointer hover:bg-slate-700 transition-colors"
                            style={{
                                backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'white\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")',
                                backgroundRepeat: 'no-repeat',
                                backgroundPosition: 'right 0.5rem center',
                                backgroundSize: '1.25rem',
                                paddingRight: '2.5rem',
                                appearance: 'none'
                            }}
                        >
                            <option value="usage" className="bg-slate-800 text-white">Usage %</option>
                            <option value="tier" className="bg-slate-800 text-white">Tier</option>
                            <option value="user_id" className="bg-slate-800 text-white">User ID</option>
                        </select>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">User</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Tier</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Limit</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Usage</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Progress</th>
                                <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedUsers.map((user) => {
                                const colors = getTierColor(user.tier);
                                const isEditing = editingUser === user.user_id;

                                return (
                                    <motion.tr
                                        key={user.user_id}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                                    >
                                        <td className="py-3 px-4">
                                            <div>
                                                <p className="text-sm font-medium text-white">
                                                    {user.user_email || user.user_id.slice(0, 12)}
                                                </p>
                                                <p className="text-xs text-slate-500 font-mono">{user.user_id.slice(0, 16)}...</p>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            {isEditing ? (
                                                <select
                                                    value={editTier}
                                                    onChange={(e) => setEditTier(e.target.value)}
                                                    className="bg-slate-800 border border-white/10 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-neon-cyan/50 cursor-pointer hover:bg-slate-700"
                                                >
                                                    <option value="free" className="bg-slate-800 text-white">Free</option>
                                                    <option value="pro" className="bg-slate-800 text-white">Pro</option>
                                                    <option value="enterprise" className="bg-slate-800 text-white">Enterprise</option>
                                                </select>
                                            ) : (
                                                <span className={`px-2 py-1 ${colors.bg} ${colors.text} text-xs rounded-full capitalize`}>
                                                    {user.tier}
                                                </span>
                                            )}
                                        </td>
                                        <td className="py-3 px-4">
                                            {isEditing ? (
                                                <input
                                                    type="number"
                                                    value={editLimit}
                                                    onChange={(e) => setEditLimit(parseInt(e.target.value))}
                                                    className="w-24 bg-white/5 border border-white/10 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-neon-cyan/50"
                                                />
                                            ) : (
                                                <span className="text-sm text-white">{user.limit.toLocaleString()}</span>
                                            )}
                                        </td>
                                        <td className="py-3 px-4">
                                            <div>
                                                <p className="text-sm text-white">{user.current_usage.toLocaleString()}</p>
                                                <p className="text-xs text-slate-400">{user.usage_percentage.toFixed(1)}%</p>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="w-full bg-white/10 rounded-full h-2">
                                                <div
                                                    className={`h-full rounded-full ${getUsageColor(user.usage_percentage)}`}
                                                    style={{ width: `${Math.min(100, user.usage_percentage)}%` }}
                                                />
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="flex items-center justify-end gap-2">
                                                {isEditing ? (
                                                    <>
                                                        <button
                                                            onClick={() => saveEdit(user.user_id)}
                                                            className="p-1.5 bg-green-500/20 text-green-400 rounded hover:bg-green-500/30 transition-colors"
                                                        >
                                                            <Save size={14} />
                                                        </button>
                                                        <button
                                                            onClick={cancelEdit}
                                                            className="p-1.5 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors"
                                                        >
                                                            <X size={14} />
                                                        </button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button
                                                            onClick={() => handleGetMLRecommendation(user.user_id)}
                                                            disabled={loadingML}
                                                            className="p-1.5 bg-neon-purple/20 text-neon-purple rounded hover:bg-neon-purple/30 transition-colors disabled:opacity-50"
                                                            title="Get ML Recommendation"
                                                        >
                                                            {loadingML ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                                                        </button>
                                                        <button
                                                            onClick={() => startEdit(user)}
                                                            className="p-1.5 bg-white/10 text-white rounded hover:bg-white/20 transition-colors"
                                                            title="Edit Rate Limit"
                                                        >
                                                            <Edit2 size={14} />
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                    </motion.tr>
                                );
                            })}
                        </tbody>
                    </table>

                    {sortedUsers.length === 0 && !isLoading && (
                        <div className="text-center py-8 text-slate-400">
                            No users found {selectedTier && `in ${selectedTier} tier`}
                        </div>
                    )}
                </div>
            </Card>

            {/* Rate Limit Events */}
            <Card>
                <div className="flex items-center gap-3 mb-4">
                    <Shield className="text-neon-pink" size={20} />
                    <h3 className="text-lg font-semibold text-white">Recent Rate Limit Events</h3>
                </div>
                <div className="space-y-2">
                    {events.map((event) => (
                        <div
                            key={event.event_id}
                            className={`flex items-center justify-between p-3 rounded-lg border ${getEventColor(event.event_type)}`}
                        >
                            <div className="flex items-center gap-3">
                                {event.event_type === 'breach' && <AlertTriangle size={16} />}
                                {event.event_type === 'warning' && <AlertTriangle size={16} />}
                                {event.event_type === 'reset' && <CheckCircle size={16} />}
                                <span className="font-mono text-sm">
                                    {event.user_email || event.user_id.slice(0, 12)}
                                </span>
                                <span className="text-slate-500">•</span>
                                <span className="text-sm capitalize">{event.event_type}</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-sm font-medium">{event.usage_percentage.toFixed(1)}%</span>
                                <span className="text-xs text-slate-500">
                                    {new Date(event.timestamp).toLocaleString()}
                                </span>
                            </div>
                        </div>
                    ))}
                    {events.length === 0 && (
                        <div className="text-center py-4 text-slate-400">No events in the last 7 days</div>
                    )}
                </div>
            </Card>

            {/* ML Recommendation Modal */}
            <AnimatePresence>
                {showMLModal && mlRecommendation && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-xl p-6 max-w-2xl w-full mx-4 shadow-2xl"
                        >
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 bg-neon-purple/20 rounded-lg">
                                    <Sparkles className="text-neon-purple" size={24} />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-white">ML Rate Limit Recommendation</h3>
                                    <p className="text-sm text-slate-400">Powered by XGBoost optimization</p>
                                </div>
                            </div>

                            <div className="space-y-4 mb-6">
                                {/* Current vs Recommended */}
                                <div className="gridgrid-cols-2 gap-4">
                                    <div className="flex-1 p-4 bg-white/5 rounded-lg">
                                        <p className="text-sm text-slate-400 mb-1">Current Limit</p>
                                        <p className="text-2xl font-bold text-white">
                                            {mlRecommendation.current_limit.toLocaleString()}
                                        </p>
                                    </div>
                                    <div className="flex-1 p-4 bg-neon-purple/10 border border-neon-purple/20 rounded-lg">
                                        <p className="text-sm text-neon-purple mb-1">Recommended Limit</p>
                                        <div className="flex items-baseline gap-2">
                                            <p className="text-2xl font-bold text-white">
                                                {mlRecommendation.recommended_limit.toLocaleString()}
                                            </p>
                                            {mlRecommendation.recommendation_type === 'increase' && (
                                                <TrendingUp className="text-green-400" size={20} />
                                            )}
                                            {mlRecommendation.recommendation_type === 'decrease' && (
                                                <TrendingDown className="text-red-400" size={20} />
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Confidence */}
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-slate-400">Confidence</span>
                                        <span className="text-sm font-medium text-white">
                                            {(mlRecommendation.confidence * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="w-full bg-white/10 rounded-full h-2">
                                        <div
                                            className="h-full bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full"
                                            style={{ width: `${mlRecommendation.confidence * 100}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Reasoning */}
                                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                                    <p className="text-sm font-medium text-white mb-2">Reasoning</p>
                                    <p className="text-sm text-slate-300">{mlRecommendation.reasoning}</p>
                                </div>

                                {/* Potential Savings */}
                                {mlRecommendation.potential_savings && (
                                    <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                                        <p className="text-sm text-green-400">
                                            💡 Potential cost savings: {mlRecommendation.potential_savings.toLocaleString()} requests/month
                                        </p>
                                    </div>
                                )}

                                {/* Minimum Limit Notice */}
                                {mlRecommendation.recommended_limit <= 10 && (
                                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                                        <p className="text-sm text-yellow-400">
                                            ⚠️ The recommended limit has been set to the minimum value of 10 requests to ensure service availability.
                                        </p>
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => {
                                        setShowMLModal(false);
                                        setMlRecommendation(null);
                                    }}
                                    className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={applyMLRecommendation}
                                    className="flex-1 px-4 py-2 bg-neon-purple/20 hover:bg-neon-purple/30 text-neon-purple rounded-lg transition-colors"
                                >
                                    Apply Recommendation
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {isLoading && (
                <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <Loader2 className="w-12 h-12 text-neon-cyan animate-spin" />
                </div>
            )}
        </motion.div>
    );
}
