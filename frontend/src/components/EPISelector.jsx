import React from 'react';
import { Check } from 'lucide-react';

const EPISelector = ({ selectedEpis, onToggle }) => {
    const availableEpis = [
        { id: 'Hardhat', label: 'Capacete' },
        { id: 'Mask', label: 'Máscara' },
        { id: 'Safety Vest', label: 'Colete' },
        { id: 'Person', label: 'Pessoas' }
    ];

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h3 className="font-semibold text-gray-800 dark:text-white mb-3">Filtros de Detecção</h3>
            <div className="space-y-2">
                {availableEpis.map((epi) => (
                    <button
                        key={epi.id}
                        onClick={() => onToggle(epi.id)}
                        className={`w-full flex items-center justify-between p-2 rounded-md text-sm transition-colors ${
                            selectedEpis.includes(epi.id)
                                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                    >
                        <span>{epi.label}</span>
                        {selectedEpis.includes(epi.id) && (
                            <Check className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default EPISelector;
