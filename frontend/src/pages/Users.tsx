import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Search, MoreVertical } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getUserStats } from '@/services/api';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.05 }
    }
};

const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
};

export default function Users() {
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const data = await getUserStats();
                console.log('👥 User stats:', data);
                setUsers(data.users || []);
                setLoading(false);
            } catch (error) {
                console.error('Failed to fetch users:', error);
                setLoading(false);
            }
        };

        fetchUsers();
        // Refresh every 30 seconds
        const interval = setInterval(fetchUsers, 30000);
        return () => clearInterval(interval);
    }, []);

    const filteredUsers = users.filter(user =>
        user.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.user_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <motion.div
            variants={container}
            animate="show"
            className="space-y-6"
        >
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Users
                    </h1>
                    <p className="text-slate-400 mt-1">Active users and their API usage</p>
                </div>
            </div>

            <Card>
                <div className="mb-6">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search dashboard, logs, users..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/50 transition-all"
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-12 text-slate-400">Loading users...</div>
                ) : filteredUsers.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">
                        {searchTerm ? 'No users found matching your search' : 'No users found. Start using the analyzer to see users here.'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">User</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">API Key</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Request Rate</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Anomaly Score</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map((user, index) => (
                                    <motion.tr
                                        key={user.user_id}
                                        variants={item}
                                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                                    >
                                        <td className="py-4 px-4">
                                            <div className="flex items-center gap-3">
                                                <div className="font-medium text-white">{user.user_name || `User ${index + 1}`}</div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4">
                                            <code className="text-xs text-slate-400 font-mono">{user.api_key}</code>
                                        </td>
                                        <td className="py-4 px-4">
                                            <span className="text-white font-medium">{user.request_rate || 0}</span>
                                            <span className="text-xs text-slate-400 ml-1">RPM</span>
                                        </td>
                                        <td className="py-4 px-4">
                                            <span
                                                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${user.status === 'RISKY'
                                                        ? 'bg-yellow-500/20 text-yellow-400'
                                                        : 'bg-green-500/20 text-green-400'
                                                    }`}
                                            >
                                                {user.status === 'RISKY' ? '⚠' : '✓'} {user.status}
                                            </span>
                                        </td>
                                        <td className="py-4 px-4">
                                            <div className="flex items-center gap-3">
                                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all ${user.anomaly_score > 60 ? 'bg-yellow-500' : 'bg-neon-cyan'
                                                            }`}
                                                        style={{ width: `${user.anomaly_score}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4">
                                            <button className="p-1 hover:bg-white/10 rounded transition-colors">
                                                <MoreVertical size={16} className="text-slate-400" />
                                            </button>
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>
        </motion.div>
    );
}
