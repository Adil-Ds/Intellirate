import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/components/providers/ThemeContext';
import { AuthProvider, useAuth } from '@/components/providers/AuthContext';
import { ToastProvider } from '@/components/providers/ToastContext';
import { MainLayout } from '@/components/layout/MainLayout';
import { Preloader } from '@/components/ui/Preloader';
import Dashboard from '@/pages/Dashboard';
import Users from '@/pages/Users';
import Logs from '@/pages/Logs';
import Anomalies from '@/pages/Anomalies';
import RateLimits from '@/pages/RateLimits';
import Traffic from '@/pages/Traffic';
import MLModels from '@/pages/MLModels';
import Performance from '@/pages/Performance';
import Settings from '@/pages/Settings';
import Login from '@/pages/Login';

function ProtectedRoutes() {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return <Preloader />;
    }

    if (!isAuthenticated) {
        return <Login />;
    }

    return (
        <Routes>
            <Route path="/" element={<MainLayout />}>
                <Route index element={<Dashboard />} />
                <Route path="traffic" element={<Traffic />} />
                <Route path="users" element={<Users />} />
                <Route path="logs" element={<Logs />} />
                <Route path="rate-limits" element={<RateLimits />} />
                <Route path="anomalies" element={<Anomalies />} />
                <Route path="ml-models" element={<MLModels />} />
                <Route path="performance" element={<Performance />} />
                <Route path="settings" element={<Settings />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

function App() {
    return (
        <BrowserRouter>
            <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
                <AuthProvider>
                    <ToastProvider>
                        <ProtectedRoutes />
                    </ToastProvider>
                </AuthProvider>
            </ThemeProvider>
        </BrowserRouter>
    );
}

export default App;
