import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Search, Download } from 'lucide-react';
import { useSystemLogs } from '@/hooks/useAnalytics';
import { useState, useMemo } from 'react';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.02 } }
};

const item = {
    hidden: { y: 10, opacity: 0 },
    show: { y: 0, opacity: 1 }
};

export default function Logs() {
    const { data: logs, loading, error } = useSystemLogs(100);
    const [searchTerm, setSearchTerm] = useState('');
    const [methodFilter, setMethodFilter] = useState('All Methods');
    const [statusFilter, setStatusFilter] = useState('All Status');

    // Transform backend log format to UI format
    const formattedLogs = useMemo(() => {
        return logs?.map((log: any) => ({
            id: log.request_id || log.id || 'N/A',
            method: log.method || 'POST',
            endpoint: log.endpoint || log.path || '/api/v1/proxy/groq',
            status: log.status_code || log.status || 200,
            latency: Math.round(log.latency_ms || 0),
            ip_address: log.ip_address || 'N/A',
            timestamp: log.timestamp ? new Date(log.timestamp) : new Date(),
        })) || [];
    }, [logs]);

    // Filter logs
    const filteredLogs = useMemo(() => {
        return formattedLogs.filter(log => {
            const matchesSearch =
                log.endpoint.toLowerCase().includes(searchTerm.toLowerCase()) ||
                log.ip_address.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesMethod = methodFilter === 'All Methods' || log.method === methodFilter;

            const matchesStatus =
                statusFilter === 'All Status' ||
                (statusFilter === '2xx' && log.status >= 200 && log.status < 300) ||
                (statusFilter === '4xx' && log.status >= 400 && log.status < 500) ||
                (statusFilter === '5xx' && log.status >= 500);

            return matchesSearch && matchesMethod && matchesStatus;
        });
    }, [formattedLogs, searchTerm, methodFilter, statusFilter]);

    // Export logs as CSV
    const handleExport = () => {
        const csvHeaders = 'TIMESTAMP,METHOD,ENDPOINT,STATUS,LATENCY,IP ADDRESS\n';
        const csvData = filteredLogs.map(log =>
            `${log.timestamp.toISOString()},${log.method},${log.endpoint},${log.status},${log.latency}ms,${log.ip_address}`
        ).join('\n');

        const blob = new Blob([csvHeaders + csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs-${new Date().toISOString()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    // Get method color
    const getMethodColor = (method: string) => {
        switch (method) {
            case 'GET': return 'text-blue-400';
            case 'POST': return 'text-green-400';
            case 'PUT': return 'text-purple-400';
            case 'DELETE': return 'text-red-400';
            case 'PATCH': return 'text-yellow-400';
            default: return 'text-slate-400';
        }
    };

    // Get status color
    const getStatusColor = (status: number) => {
        if (status >= 200 && status < 300) return 'text-green-400';
        if (status >= 400 && status < 500) return 'text-yellow-400';
        if (status >= 500) return 'text-red-400';
        return 'text-slate-400';
    };

    return (
        <motion.div variants={container} animate="show" className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Logs
                    </h1>
                    <p className="text-slate-400 mt-1">API request logs and system events</p>
                </div>
                <button
                    onClick={handleExport}
                    disabled={filteredLogs.length === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors border border-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Download size={18} />
                    Export
                </button>
            </div>

            <Card>
                <div className="mb-6 flex items-center gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search dashboard, logs, users..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/50"
                        />
                    </div>
                    <select
                        value={methodFilter}
                        onChange={(e) => setMethodFilter(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-cyan/50"
                    >
                        <option className="bg-slate-800 text-white">All Methods</option>
                        <option className="bg-slate-800 text-white">GET</option>
                        <option className="bg-slate-800 text-white">POST</option>
                        <option className="bg-slate-800 text-white">PUT</option>
                        <option className="bg-slate-800 text-white">DELETE</option>
                        <option className="bg-slate-800 text-white">PATCH</option>
                    </select>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-cyan/50"
                    >
                        <option className="bg-slate-800 text-white">All Status</option>
                        <option className="bg-slate-800 text-white">2xx</option>
                        <option className="bg-slate-800 text-white">4xx</option>
                        <option className="bg-slate-800 text-white">5xx</option>
                    </select>
                </div>

                {loading ? (
                    <div className="text-center text-slate-400 py-12">Loading logs...</div>
                ) : error ? (
                    <div className="text-center text-status-danger py-12">Failed to load logs</div>
                ) : filteredLogs.length === 0 ? (
                    <div className="text-center text-slate-400 py-12">
                        {searchTerm || methodFilter !== 'All Methods' || statusFilter !== 'All Status'
                            ? 'No logs match your filters'
                            : 'No logs available'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Timestamp</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Method</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Endpoint</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Latency</th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">IP Address</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredLogs.map((log) => (
                                    <motion.tr
                                        key={log.id}
                                        variants={item}
                                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                                    >
                                        <td className="py-3 px-4 text-sm text-slate-300 font-mono">
                                            {log.timestamp.toLocaleTimeString()}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`text-sm font-semibold ${getMethodColor(log.method)}`}>
                                                {log.method}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-slate-300 font-mono">
                                            {log.endpoint}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`text-sm font-semibold ${getStatusColor(log.status)}`}>
                                                {log.status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-slate-300">
                                            {log.latency}ms
                                        </td>
                                        <td className="py-3 px-4 text-sm text-slate-400 font-mono">
                                            {log.ip_address}
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {!loading && !error && filteredLogs.length > 0 && (
                    <div className="mt-4 text-sm text-slate-400 text-center">
                        Showing {filteredLogs.length} of {formattedLogs.length} logs
                    </div>
                )}
            </Card>
        </motion.div>
    );
}
