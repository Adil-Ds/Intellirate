import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
    id: string;
    name: string;
    email: string;
    avatar: string;
    role: 'admin' | 'user';
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
    isLoading: boolean;
    changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Default admin credentials
const DEFAULT_CREDENTIALS = {
    email: 'admin@intellirate.com',
    password: 'Admin@321',
};

const ADMIN_USER: User = {
    id: '1',
    name: 'Admin User',
    email: 'admin@intellirate.com',
    avatar: 'https://ui-avatars.com/api/?name=Admin+User&background=0D8ABC&color=fff',
    role: 'admin',
};

// LocalStorage keys
const STORAGE_KEYS = {
    USER: 'intellirate_user',
    CREDENTIALS: 'intellirate_credentials',
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [credentials, setCredentials] = useState(() => {
        // Load credentials from localStorage or use defaults
        const stored = localStorage.getItem(STORAGE_KEYS.CREDENTIALS);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (error) {
                console.error('Failed to parse stored credentials:', error);
            }
        }
        return { ...DEFAULT_CREDENTIALS };
    });

    useEffect(() => {
        // Check for existing session in localStorage
        const checkSession = () => {
            const savedUser = localStorage.getItem(STORAGE_KEYS.USER);
            if (savedUser) {
                try {
                    setUser(JSON.parse(savedUser));
                } catch (error) {
                    console.error('Failed to parse saved user:', error);
                    localStorage.removeItem(STORAGE_KEYS.USER);
                }
            }
            setIsLoading(false);
        };

        // Simulate initial auth check with slight delay
        setTimeout(checkSession, 500);
    }, []);

    const login = async (email: string, password: string): Promise<boolean> => {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 800));

        // Validate credentials against stored credentials
        if (email === credentials.email && password === credentials.password) {
            setUser(ADMIN_USER);
            localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(ADMIN_USER));
            return true;
        }

        return false;
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem(STORAGE_KEYS.USER);
    };

    const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 800));

        // Validate current password
        if (currentPassword !== credentials.password) {
            return false;
        }

        // Update credentials in state and localStorage
        const newCredentials = {
            ...credentials,
            password: newPassword,
        };
        setCredentials(newCredentials);
        localStorage.setItem(STORAGE_KEYS.CREDENTIALS, JSON.stringify(newCredentials));

        return true;
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, isLoading, changePassword }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
