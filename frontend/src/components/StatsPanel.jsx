import React from 'react';
import { BarChart, Activity, Users, ShieldCheck } from 'lucide-react';

const StatsPanel = ({ stats }) => {
    // Default stats if none provided
    const data = stats || {
        total_detections: 0,
        violations_count: 0,
        processing_time_ms: 0
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 flex items-center">
                <div className="p-3 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 mr-4">
                    <Users className="w-6 h-6" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Total Detecções</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">{data.total_detections}</p>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 flex items-center">
                <div className="p-3 rounded-full bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 mr-4">
                    <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Violações Ativas</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">{data.violations_count}</p>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 flex items-center">
                <div className="p-3 rounded-full bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 mr-4">
                    <Activity className="w-6 h-6" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Latência (ms)</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">
                        {data.processing_time_ms ? data.processing_time_ms.toFixed(1) : '0.0'}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default StatsPanel;
