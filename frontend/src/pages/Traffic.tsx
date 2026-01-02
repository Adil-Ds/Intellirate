import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';
import { LiveTrafficChart } from '@/components/charts/LiveTrafficChart';
import { ForecastChart } from '@/components/charts/ForecastChart';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

export default function Traffic() {
    console.log('🚦 TRAFFIC PAGE IS RENDERING');

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-6"
        >
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Traffic & Forecasting
                    </h1>
                    <p className="text-slate-400 mt-1">Real-time traffic monitoring and AI-powered predictions</p>
                </div>
                <div className="flex items-center gap-2">
                    <TrendingUp className="text-neon-cyan" size={24} />
                </div>
            </div>

            <div className="space-y-6">
                <LiveTrafficChart />
                <ForecastChart />
            </div>
        </motion.div>
    );
}
