import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    noHover?: boolean;
}

export function Card({ children, className, noHover = false, ...props }: CardProps) {
    return (
        <motion.div
            whileHover={!noHover ? { scale: 1.02, boxShadow: "0 0 20px rgba(6, 182, 212, 0.15)" } : {}}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className={cn(
                "glass-panel rounded-xl p-6 transition-all duration-300 relative overflow-hidden group",
                "border border-white/10 dark:border-white/5",
                "bg-white/50 dark:bg-slate-900/60", // base background
                className
            )}
            {...props}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-neon-cyan/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
                {children}
            </div>
        </motion.div>
    );
}
