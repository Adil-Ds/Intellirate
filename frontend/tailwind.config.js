/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                deepSpace: {
                    DEFAULT: '#030014',
                    light: '#F8FAFC', // For light mode background
                },
                glassSlate: {
                    DEFAULT: '#0F172A',
                    light: '#FFFFFF', // For light mode surface
                },
                neon: {
                    cyan: '#06B6D4',
                    cyanBright: '#00F2FF',
                    purple: '#7C3AED',
                    purpleBright: '#7000FF',
                    pink: '#EC4899',
                    pinkBright: '#F472B6',
                },
                status: {
                    success: '#00ff9d',
                    warning: '#ffbb00',
                    danger: '#ff0055',
                }
            },
            boxShadow: {
                'neon-cyan': '0 0 10px rgba(6, 182, 212, 0.5), 0 0 20px rgba(6, 182, 212, 0.3)',
                'neon-purple': '0 0 10px rgba(124, 58, 237, 0.5), 0 0 20px rgba(124, 58, 237, 0.3)',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'spin-slow': 'spin 3s linear infinite',
            }
        },
    },
    plugins: [],
}
