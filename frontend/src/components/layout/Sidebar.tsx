import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, FileText, Activity, ShieldAlert, Settings, LogOut, TrendingUp, Sparkles, BarChart3 } from 'lucide-react';
import { cn } from '@/utils';
import { useAuth } from '@/components/providers/AuthContext';

const NAV_ITEMS = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: TrendingUp, label: 'Traffic', path: '/traffic' },
    { icon: Users, label: 'Users', path: '/users' },
    { icon: FileText, label: 'Logs', path: '/logs' },
    { icon: Activity, label: 'Rate Limits', path: '/rate-limits' },
    { icon: ShieldAlert, label: 'Anomalies', path: '/anomalies' },
    { icon: Sparkles, label: 'ML Models', path: '/ml-models' },
    { icon: BarChart3, label: 'Performance', path: '/performance' },
];

export function Sidebar() {
    const { logout } = useAuth();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-glassSlate/80 backdrop-blur-xl border-r border-white/5 flex flex-col z-40">
            <div className="h-16 flex items-center px-6 border-b border-white/5">
                <div className="text-2xl font-bold font-mono tracking-tighter">
                    <span className="text-neon-cyan">INTELLI</span>
                    <span className="text-white">RATE</span>
                </div>
            </div>

            <nav className="flex-1 py-6 px-3 space-y-1">
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => cn(
                            "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                            isActive
                                ? "bg-neon-cyan/10 text-neon-cyan shadow-[0_0_15px_rgba(6,182,212,0.2)]"
                                : "text-slate-400 hover:text-white hover:bg-white/5"
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                        <div className={cn(
                            "ml-auto w-1.5 h-1.5 rounded-full bg-neon-cyan shadow-[0_0_8px_rgba(6,182,212,0.8)] opacity-0 transition-opacity",
                            "group-[.active]:opacity-100" // Tailwind needs explicit active class or logic here, using isActive check is enough
                        )} />
                    </NavLink>
                ))}
            </nav>

            <div className="p-3 border-t border-white/5">
                <NavLink
                    to="/settings"
                    className={({ isActive }) => cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 mb-1",
                        isActive
                            ? "bg-neon-cyan/10 text-neon-cyan"
                            : "text-slate-400 hover:text-white hover:bg-white/5"
                    )}
                >
                    <Settings className="w-5 h-5" />
                    <span className="font-medium">Settings</span>
                </NavLink>
                <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-status-danger hover:bg-status-danger/10 transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">Logout</span>
                </button>
            </div>
        </aside>
    );
}
