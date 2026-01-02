import { Search, Bell, Sun, Moon, LogOut, Settings as SettingsIcon, ChevronDown } from 'lucide-react';
import { useTheme } from '@/components/providers/ThemeContext';
import { useAuth } from '@/components/providers/AuthContext';
import { cn } from '@/utils';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function Navbar() {
    const { theme, setTheme } = useTheme();
    const { user, logout } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        setShowLogoutConfirm(false);
        setShowUserMenu(false);
    };

    return (
        <header className="sticky top-0 z-30 h-16 w-full glass-panel border-b border-white/5 flex items-center justify-between px-6 bg-glassSlate/50">
            {/* Search */}
            <div className="flex-1 max-w-xl">
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-neon-cyan transition-colors" />
                    <input
                        type="text"
                        placeholder="Search users, logs, or endpoints... (CMD+K)"
                        className="w-full bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/50 transition-all"
                    />
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                    className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                >
                    {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>

                <button className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-neon-pink rounded-full shadow-[0_0_8px_#EC4899]" />
                </button>

                <div className="h-8 w-[1px] bg-white/10 mx-2" />

                {/* User Menu */}
                <div className="relative">
                    <button
                        onClick={() => setShowUserMenu(!showUserMenu)}
                        className="flex items-center gap-3 hover:bg-white/5 rounded-lg p-2 transition-colors"
                    >
                        <div className="text-right hidden md:block">
                            <p className="text-sm font-medium text-white">{user?.name}</p>
                            <p className="text-xs text-slate-400">{user?.role}</p>
                        </div>
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-neon-cyan to-neon-purple p-[1px]">
                            <div className="w-full h-full rounded-full overflow-hidden bg-slate-900">
                                <img src={user?.avatar} alt="Profile" className="w-full h-full object-cover" />
                            </div>
                        </div>
                        <ChevronDown className={cn("w-4 h-4 text-slate-400 transition-transform", showUserMenu && "rotate-180")} />
                    </button>

                    {/* Dropdown Menu */}
                    {showUserMenu && (
                        <>
                            <div
                                className="fixed inset-0 z-40"
                                onClick={() => setShowUserMenu(false)}
                            />
                            <div className="absolute right-0 mt-2 w-56 bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
                                <div className="p-3 border-b border-white/10">
                                    <p className="text-sm font-medium text-white">{user?.name}</p>
                                    <p className="text-xs text-slate-400">{user?.email}</p>
                                </div>
                                <div className="p-1">
                                    <button
                                        onClick={() => {
                                            navigate('/settings');
                                            setShowUserMenu(false);
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                                    >
                                        <SettingsIcon className="w-4 h-4" />
                                        Settings
                                    </button>
                                    <button
                                        onClick={() => {
                                            setShowLogoutConfirm(true);
                                            setShowUserMenu(false);
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        Logout
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Logout Confirmation Dialog */}
            {showLogoutConfirm && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-xl p-6 max-w-sm w-full mx-4 shadow-2xl">
                        <h3 className="text-xl font-semibold text-white mb-2">Confirm Logout</h3>
                        <p className="text-slate-400 text-sm mb-6">Are you sure you want to logout? You'll need to login again to access IntelliRate.</p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowLogoutConfirm(false)}
                                className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleLogout}
                                className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
}
