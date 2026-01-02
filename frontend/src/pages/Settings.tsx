import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { useTheme } from '@/components/providers/ThemeContext';
import { useAuth } from '@/components/providers/AuthContext';
import { useToast } from '@/components/providers/ToastContext';
import { Sun, Moon, User, Shield, Globe, Save, AlertCircle, CheckCircle, Key, Wifi, WifiOff } from 'lucide-react';

export default function Settings() {
    const { theme, setTheme } = useTheme();
    const { user, changePassword } = useAuth();
    const { showToast } = useToast();

    // Profile state
    const [displayName, setDisplayName] = useState(user?.name || '');
    const [email, setEmail] = useState(user?.email || '');
    const [profileChanged, setProfileChanged] = useState(false);
    const [isSavingProfile, setIsSavingProfile] = useState(false);

    // API configuration state
    const [backendUrl, setBackendUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:8000');
    const [apiKey, setApiKey] = useState('sk_live_••••••••••••••••');
    const [isTestingConnection, setIsTestingConnection] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [isRegeneratingKey, setIsRegeneratingKey] = useState(false);

    // Security state
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [show2FAModal, setShow2FAModal] = useState(false);
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    // Track profile changes
    const handleProfileChange = (field: 'name' | 'email', value: string) => {
        if (field === 'name') setDisplayName(value);
        if (field === 'email') setEmail(value);
        setProfileChanged(true);
    };

    // Save profile changes
    const handleSaveProfile = async () => {
        setIsSavingProfile(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            showToast('Profile updated successfully', 'success');
            setProfileChanged(false);
        } catch (error) {
            showToast('Failed to update profile', 'error');
        } finally {
            setIsSavingProfile(false);
        }
    };

    // Test API connection
    const handleTestConnection = async () => {
        setIsTestingConnection(true);
        setConnectionStatus('idle');
        try {
            // Simulate API health check
            const response = await fetch(`${backendUrl}/health`);
            if (response.ok) {
                setConnectionStatus('success');
                showToast('Connection successful', 'success');
            } else {
                setConnectionStatus('error');
                showToast('Connection failed', 'error');
            }
        } catch (error) {
            setConnectionStatus('error');
            showToast('Unable to reach backend', 'error');
        } finally {
            setIsTestingConnection(false);
        }
    };

    // Regenerate API key
    const handleRegenerateKey = async () => {
        setIsRegeneratingKey(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1500));
            const newKey = `sk_live_${Math.random().toString(36).substring(2, 18)}`;
            setApiKey(newKey);
            showToast('API key regenerated successfully', 'success');
        } catch (error) {
            showToast('Failed to regenerate API key', 'error');
        } finally {
            setIsRegeneratingKey(false);
        }
    };

    // Change password
    const handleChangePassword = async () => {
        // Validate password match
        if (newPassword !== confirmPassword) {
            showToast('Passwords do not match', 'error');
            return;
        }

        // Validate password length
        if (newPassword.length < 8) {
            showToast('Password must be at least 8 characters', 'error');
            return;
        }

        // Validate current password is provided
        if (!currentPassword) {
            showToast('Please enter your current password', 'error');
            return;
        }

        try {
            // Call the changePassword method from AuthContext
            const success = await changePassword(currentPassword, newPassword);

            if (success) {
                showToast('Password changed successfully', 'success');
                setShowPasswordModal(false);
                setCurrentPassword('');
                setNewPassword('');
                setConfirmPassword('');
            } else {
                showToast('Current password is incorrect', 'error');
            }
        } catch (error) {
            showToast('Failed to change password', 'error');
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Settings
                </h1>
                <p className="text-slate-400 mt-1">Manage your preferences and account settings</p>
            </div>

            {/* Profile Section */}
            <Card>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <User size={20} className="text-neon-cyan" />
                    Profile Information
                </h3>
                <div className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple p-[2px]">
                            <div className="w-full h-full rounded-full overflow-hidden bg-slate-900">
                                <img src={user?.avatar} alt="Profile" className="w-full h-full object-cover" />
                            </div>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white">{displayName}</h4>
                            <p className="text-sm text-slate-400">{email}</p>
                            <span className="inline-block mt-1 px-2 py-0.5 bg-neon-cyan/20 text-neon-cyan text-xs rounded-full">
                                {user?.role}
                            </span>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/10">
                        <div>
                            <label className="text-sm text-slate-400 mb-1 block">Display Name</label>
                            <input
                                type="text"
                                value={displayName}
                                onChange={(e) => handleProfileChange('name', e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-cyan/50 transition-colors"
                            />
                        </div>
                        <div>
                            <label className="text-sm text-slate-400 mb-1 block">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => handleProfileChange('email', e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-cyan/50 transition-colors"
                            />
                        </div>
                    </div>

                    {profileChanged && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-center justify-between p-3 bg-neon-cyan/10 border border-neon-cyan/20 rounded-lg"
                        >
                            <div className="flex items-center gap-2 text-neon-cyan text-sm">
                                <AlertCircle size={16} />
                                <span>You have unsaved changes</span>
                            </div>
                            <button
                                onClick={handleSaveProfile}
                                disabled={isSavingProfile}
                                className="flex items-center gap-2 px-4 py-2 bg-neon-cyan text-slate-900 rounded-lg hover:bg-neon-cyan/90 transition-colors font-medium disabled:opacity-50"
                            >
                                {isSavingProfile ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-slate-900/30 border-t-slate-900 rounded-full animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save size={16} />
                                        Save Changes
                                    </>
                                )}
                            </button>
                        </motion.div>
                    )}
                </div>
            </Card>

            {/* Appearance Section */}
            <Card>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Sun size={20} className="text-neon-purple" />
                    Appearance
                </h3>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="font-medium text-white">Theme</p>
                        <p className="text-sm text-slate-400">Choose your preferred color scheme</p>
                    </div>
                    <button
                        onClick={() => {
                            setTheme(theme === 'dark' ? 'light' : 'dark');
                            showToast(`Switched to ${theme === 'dark' ? 'light' : 'dark'} mode`, 'success');
                        }}
                        className="p-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                    >
                        {theme === 'dark' ? <Moon size={20} className="text-neon-cyan" /> : <Sun size={20} className="text-neon-purple" />}
                    </button>
                </div>
            </Card>

            {/* API Configuration */}
            <Card>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Globe size={20} className="text-neon-pink" />
                    API Configuration
                </h3>
                <div className="space-y-3">
                    <div>
                        <label className="text-sm text-slate-400 mb-1 block">Backend URL</label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={backendUrl}
                                onChange={(e) => setBackendUrl(e.target.value)}
                                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-slate-300 font-mono text-sm focus:outline-none focus:border-neon-cyan/50"
                            />
                            <button
                                onClick={handleTestConnection}
                                disabled={isTestingConnection}
                                className="px-4 py-2 bg-neon-cyan/10 text-neon-cyan rounded-lg hover:bg-neon-cyan/20 transition-colors text-sm font-medium disabled:opacity-50 flex items-center gap-2"
                            >
                                {isTestingConnection ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-neon-cyan/30 border-t-neon-cyan rounded-full animate-spin" />
                                        Testing...
                                    </>
                                ) : (
                                    <>
                                        {connectionStatus === 'success' && <Wifi size={16} />}
                                        {connectionStatus === 'error' && <WifiOff size={16} />}
                                        Test
                                    </>
                                )}
                            </button>
                        </div>
                        {connectionStatus !== 'idle' && (
                            <motion.p
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className={`text-xs mt-1 flex items-center gap-1 ${connectionStatus === 'success' ? 'text-green-400' : 'text-red-400'}`}
                            >
                                {connectionStatus === 'success' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                                {connectionStatus === 'success' ? 'Connected successfully' : 'Connection failed'}
                            </motion.p>
                        )}
                    </div>

                    <div>
                        <label className="text-sm text-slate-400 mb-1 block">API Key</label>
                        <div className="flex gap-2">
                            <input
                                type="password"
                                value={apiKey}
                                readOnly
                                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm"
                            />
                            <button
                                onClick={handleRegenerateKey}
                                disabled={isRegeneratingKey}
                                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium disabled:opacity-50 flex items-center gap-2"
                            >
                                {isRegeneratingKey ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <Key size={16} />
                                        Regenerate
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Security */}
            <Card>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Shield size={20} className="text-status-success" />
                    Security
                </h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div>
                            <p className="font-medium text-white">Two-Factor Authentication</p>
                            <p className="text-sm text-slate-400">Add an extra layer of security</p>
                        </div>
                        <button
                            onClick={() => setShow2FAModal(true)}
                            className="px-4 py-2 bg-neon-cyan/10 text-neon-cyan rounded-lg hover:bg-neon-cyan/20 transition-colors text-sm font-medium"
                        >
                            Enable
                        </button>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div>
                            <p className="font-medium text-white">Password</p>
                            <p className="text-sm text-slate-400">Last changed 30 days ago</p>
                        </div>
                        <button
                            onClick={() => setShowPasswordModal(true)}
                            className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium"
                        >
                            Change
                        </button>
                    </div>
                </div>
            </Card>

            {/* Password Change Modal */}
            <AnimatePresence>
                {showPasswordModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl"
                        >
                            <h3 className="text-xl font-semibold text-white mb-4">Change Password</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-slate-400 mb-1 block">Current Password</label>
                                    <input
                                        type="password"
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-cyan/50"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm text-slate-400 mb-1 block">New Password</label>
                                    <input
                                        type="password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-cyan/50"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm text-slate-400 mb-1 block">Confirm New Password</label>
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-cyan/50"
                                    />
                                </div>
                            </div>
                            <div className="flex gap-3 mt-6">
                                <button
                                    onClick={() => {
                                        setShowPasswordModal(false);
                                        setCurrentPassword('');
                                        setNewPassword('');
                                        setConfirmPassword('');
                                    }}
                                    className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleChangePassword}
                                    className="flex-1 px-4 py-2 bg-neon-cyan/20 hover:bg-neon-cyan/30 text-neon-cyan rounded-lg transition-colors"
                                >
                                    Change Password
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* 2FA Modal */}
            <AnimatePresence>
                {show2FAModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl"
                        >
                            <h3 className="text-xl font-semibold text-white mb-4">Enable Two-Factor Authentication</h3>
                            <p className="text-slate-400 text-sm mb-6">
                                Two-factor authentication adds an extra layer of security to your account. Scan the QR code below with your authenticator app.
                            </p>
                            <div className="bg-white p-4 rounded-lg mb-6 flex justify-center">
                                <div className="w-48 h-48 bg-slate-200 rounded flex items-center justify-center">
                                    <p className="text-slate-500 text-sm text-center">QR Code<br />Placeholder</p>
                                </div>
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShow2FAModal(false)}
                                    className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => {
                                        showToast('2FA will be enabled in production', 'success');
                                        setShow2FAModal(false);
                                    }}
                                    className="flex-1 px-4 py-2 bg-neon-cyan/20 hover:bg-neon-cyan/30 text-neon-cyan rounded-lg transition-colors"
                                >
                                    Enable 2FA
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
