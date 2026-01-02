import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { Preloader } from '@/components/ui/Preloader';
import { useAuth } from '@/components/providers/AuthContext';
import { AnimatePresence } from 'framer-motion';

export function MainLayout() {
    const { isLoading } = useAuth();

    if (isLoading) {
        return <Preloader />;
    }

    return (
        <div className="min-h-screen bg-deepSpace text-slate-200 flex">
            <Sidebar />
            <main className="flex-1 ml-64 flex flex-col min-h-screen">
                <Navbar />
                <div className="flex-1 p-6 overflow-y-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
