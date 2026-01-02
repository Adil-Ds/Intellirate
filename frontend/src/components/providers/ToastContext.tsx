import React, { createContext, useContext, useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle, AlertCircle, X, Info } from 'lucide-react';
import { cn } from '@/utils';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
    id: string;
    type: ToastType;
    message: string;
}

interface ToastContextType {
    toast: (message: string, type?: ToastType) => void;
    showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const toast = useCallback((message: string, type: ToastType = 'info') => {
        const id = Math.random().toString(36).substring(7);
        setToasts((prev) => [...prev, { id, type, message }]);
        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id));
        }, 5000);
    }, []);

    const removeToast = (id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    };

    return (
        <ToastContext.Provider value={{ toast, showToast: toast }}>
            {children}
            <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
                <AnimatePresence>
                    {toasts.map((t) => (
                        <motion.div
                            key={t.id}
                            initial={{ opacity: 0, y: 20, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                            className={cn(
                                "min-w-[300px] p-4 rounded-lg shadow-lg border backdrop-blur-md flex items-center gap-3",
                                t.type === 'success' && "bg-status-success/10 border-status-success/20 text-status-success",
                                t.type === 'error' && "bg-status-danger/10 border-status-danger/20 text-status-danger",
                                t.type === 'warning' && "bg-status-warning/10 border-status-warning/20 text-status-warning",
                                t.type === 'info' && "bg-neon-cyan/10 border-neon-cyan/20 text-neon-cyan"
                            )}
                        >
                            {t.type === 'success' && <CheckCircle size={20} />}
                            {t.type === 'error' && <AlertCircle size={20} />}
                            {t.type === 'warning' && <AlertCircle size={20} />}
                            {t.type === 'info' && <Info size={20} />}

                            <p className="text-sm font-medium flex-1">{t.message}</p>

                            <button
                                onClick={() => removeToast(t.id)}
                                className="opacity-70 hover:opacity-100 transition-opacity"
                            >
                                <X size={16} />
                            </button>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </ToastContext.Provider>
    );
}

export const useToast = () => {
    const context = useContext(ToastContext);
    if (context === undefined) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};
