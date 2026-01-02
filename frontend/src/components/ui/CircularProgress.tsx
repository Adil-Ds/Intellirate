import { motion } from 'framer-motion';

interface CircularProgressProps {
    percentage: number;
    size?: number;
    strokeWidth?: number;
    color?: string;
    backgroundColor?: string;
    label?: string;
    sublabel?: string;
    showPercentage?: boolean;
}

export function CircularProgress({
    percentage,
    size = 180,
    strokeWidth = 12,
    color = '#00d9ff',
    backgroundColor = 'rgba(255, 255, 255, 0.1)',
    label,
    sublabel,
    showPercentage = true
}: CircularProgressProps) {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    return (
        <div className="flex flex-col items-center gap-1">
            <div className="relative" style={{ width: size, height: size }}>
                {/* Background Circle */}
                <svg
                    width={size}
                    height={size}
                    className="transform -rotate-90"
                >
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        stroke={backgroundColor}
                        strokeWidth={strokeWidth}
                        fill="none"
                    />
                    {/* Animated Progress Circle */}
                    <motion.circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        stroke={color}
                        strokeWidth={strokeWidth}
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset: offset }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                    />
                </svg>

                {/* Center Text */}
                {showPercentage && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <motion.span
                            className="text-3xl font-bold text-white"
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.3, duration: 0.5 }}
                        >
                            {percentage.toFixed(1)}%
                        </motion.span>
                        {sublabel && (
                            <span className="text-xs text-slate-400 mt-1">{sublabel}</span>
                        )}
                    </div>
                )}
            </div>

            {/* Label */}
            {label && (
                <div className="text-center">
                    <p className="text-sm text-slate-300">{label}</p>
                </div>
            )}
        </div>
    );
}

interface CircularProgressCardProps {
    title: string;
    percentage: number;
    description: string;
    color?: string;
    icon?: React.ReactNode;
}

export function CircularProgressCard({
    title,
    percentage,
    description,
    color = '#00d9ff',
    icon
}: CircularProgressCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-slate-900/50 backdrop-blur-sm border border-white/10 rounded-2xl p-3 flex flex-col items-center"
        >
            <div className="flex items-center gap-2 mb-2">
                {icon && <div className="text-slate-400">{icon}</div>}
                <h3 className="text-lg font-semibold text-white">{title}</h3>
            </div>

            <CircularProgress
                percentage={percentage}
                color={color}
                sublabel="Utilization"
                size={150}
                strokeWidth={12}
            />

            <p className="text-sm text-slate-400 text-center mt-2">
                {description}
            </p>
        </motion.div>
    );
}
