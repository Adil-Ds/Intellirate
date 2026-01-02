import { useState } from 'react';
import { X, CheckSquare, Square, RefreshCw } from 'lucide-react';
import { Card } from '@/components/ui/Card';

interface RetrainModelsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onRetrain: (models: string[]) => Promise<void>;
    retraining: boolean;
}

export function RetrainModelsModal({
    isOpen,
    onClose,
    onRetrain,
    retraining
}: RetrainModelsModalProps) {
    const [selectedModels, setSelectedModels] = useState<string[]>([]);

    if (!isOpen) return null;

    const models = [
        { id: 'prophet', name: 'Prophet', description: 'Traffic Forecasting' },
        { id: 'xgboost', name: 'XGBoost', description: 'Rate Limit Optimization' },
        { id: 'isolation_forest', name: 'Isolation Forest', description: 'Abuse Detection' }
    ];

    const toggleModel = (modelId: string) => {
        setSelectedModels(prev =>
            prev.includes(modelId)
                ? prev.filter(id => id !== modelId)
                : [...prev, modelId]
        );
    };

    const selectAll = () => {
        setSelectedModels(models.map(m => m.id));
    };

    const deselectAll = () => {
        setSelectedModels([]);
    };

    const handleRetrain = async () => {
        if (selectedModels.length === 0) return;
        await onRetrain(selectedModels);
        setSelectedModels([]);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <Card className="w-full max-w-md slideUp">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-white">Retrain Models</h2>
                    <button
                        onClick={onClose}
                        disabled={retraining}
                        className="p-2 rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
                    >
                        <X className="text-slate-400" size={20} />
                    </button>
                </div>

                {/* Model Selection */}
                <div className="space-y-3 mb-6">
                    {models.map(model => (
                        <button
                            key={model.id}
                            onClick={() => toggleModel(model.id)}
                            disabled={retraining}
                            className="w-full flex items-center gap-3 p-4 rounded-lg border border-slate-700 hover:border-neon-cyan transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {selectedModels.includes(model.id) ? (
                                <CheckSquare className="text-neon-cyan" size={20} />
                            ) : (
                                <Square className="text-slate-500" size={20} />
                            )}
                            <div className="flex-1 text-left">
                                <p className="font-semibold text-white">{model.name}</p>
                                <p className="text-xs text-slate-400">{model.description}</p>
                            </div>
                        </button>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={selectAll}
                        disabled={retraining}
                        className="flex-1 px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors disabled:opacity-50"
                    >
                        Select All
                    </button>
                    <button
                        onClick={deselectAll}
                        disabled={retraining}
                        className="flex-1 px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors disabled:opacity-50"
                    >
                        Deselect All
                    </button>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        disabled={retraining}
                        className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors disabled:opacity-50"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleRetrain}
                        disabled={retraining || selectedModels.length === 0}
                        className="flex-1 px-4 py-3 bg-gradient-to-r from-neon-purple to-neon-cyan text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {retraining ? (
                            <>
                                <RefreshCw className="animate-spin" size={16} />
                                Retraining...
                            </>
                        ) : (
                            'Start Retraining'
                        )}
                    </button>
                </div>
            </Card>
        </div>
    );
}
