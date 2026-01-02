import { useState, useEffect } from 'react';
import { getTrafficData } from '@/services/api';

export interface TrafficDataPoint {
    time: string;
    value: number;
}

export const useLiveTraffic = (hours = 24) => {
    const [data, setData] = useState<TrafficDataPoint[]>([]);

    const fetchTrafficData = async () => {
        try {
            const response = await getTrafficData();

            // Transform backend data to chart format
            if (response.data && Array.isArray(response.data)) {
                const formattedData = response.data.map((item: any) => ({
                    time: item.time ? new Date(item.time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    }) : 'N/A',
                    value: item.value || 0
                })).reverse(); // Reverse to show oldest to newest

                setData(formattedData);
            } else {
                // If no data, show empty array
                setData([]);
            }
        } catch (error) {
            console.error('Error fetching traffic data:', error);
            // On error, keep existing data or set empty
            setData([]);
        }
    };

    useEffect(() => {
        // Fetch immediately
        fetchTrafficData();

        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchTrafficData, 30000);

        return () => clearInterval(interval);
    }, [hours]);

    return data;
};
