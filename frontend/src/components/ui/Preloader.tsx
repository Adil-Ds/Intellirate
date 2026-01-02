import { motion } from 'framer-motion';

export function Preloader() {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-deepSpace text-white">
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 1, 0.5],
                    filter: ["drop-shadow(0 0 0px #06B6D4)", "drop-shadow(0 0 20px #06B6D4)", "drop-shadow(0 0 0px #06B6D4)"]
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="relative"
            >
                <div className="text-4xl font-bold font-mono tracking-tighter">
                    <span className="text-neon-cyan">INTELLI</span>
                    <span className="text-white">RATE</span>
                </div>
                <div className="absolute -bottom-4 left-0 right-0 h-1 bg-neon-cyan/20 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-neon-cyan"
                        animate={{ x: [-100, 100] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                    />
                </div>
            </motion.div>
        </div>
    );
}
