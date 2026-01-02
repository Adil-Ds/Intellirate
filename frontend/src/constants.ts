export const MOCK_USERS = [
    { id: 1, name: "Alice Johnson", role: "Admin", status: "Active", lastActive: "2 mins ago" },
    { id: 2, name: "Bob Smith", role: "Developer", status: "Offline", lastActive: "4 hours ago" },
    { id: 3, name: "Charlie Brown", role: "Viewer", status: "Active", lastActive: "Just now" },
    { id: 4, name: "Diana Prince", role: "Admin", status: "Active", lastActive: "10 mins ago" },
    { id: 5, name: "Evan Wright", role: "Developer", status: "Inactive", lastActive: "2 days ago" },
];

export const MOCK_LOGS = [
    { id: "req_1", method: "POST", path: "/api/v1/predict", status: 200, latency: "45ms", time: "10:00:01" },
    { id: "req_2", method: "GET", path: "/api/v1/health", status: 200, latency: "12ms", time: "10:00:05" },
    { id: "req_3", method: "POST", path: "/api/auth/login", status: 401, latency: "89ms", time: "10:00:12" },
    { id: "req_4", method: "GET", path: "/api/v1/users", status: 200, latency: "150ms", time: "10:00:15" },
    { id: "req_5", method: "POST", path: "/api/v1/predict", status: 200, latency: "52ms", time: "10:00:22" },
];

export const DASHBOARD_METRICS = {
    totalRequests: { value: "2.4M", trend: "+12.5%", isPositive: true },
    avgLatency: { value: "48ms", trend: "-5.2%", isPositive: true }, // Lower latency is good (positive)
    anomalies: { value: "15", trend: "+2", isPositive: false },
    activeUsers: { value: "842", trend: "+8.1%", isPositive: true },
};
