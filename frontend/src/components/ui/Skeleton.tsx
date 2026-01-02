import { Card } from '@/components/ui/Card';

interface SkeletonProps {
    className?: string;
}

export function Skeleton({ className = '' }: SkeletonProps) {
    return (
        <div className={`animate-pulse bg-white/10 rounded ${className}`} />
    );
}

export function DashboardSkeleton() {
    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map((i) => (
                    <Card key={i}>
                        <Skeleton className="h-20 w-full" />
                    </Card>
                ))}
            </div>
            <Card>
                <Skeleton className="h-[400px] w-full" />
            </Card>
        </div>
    );
}
