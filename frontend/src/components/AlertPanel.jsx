import React from 'react';
import { AlertTriangle, Clock, ShieldAlert } from 'lucide-react';

const AlertPanel = ({ alerts = [] }) => {
    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md h-full flex flex-col">
            <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                <h3 className="font-semibold text-gray-800 dark:text-white flex items-center">
                    <ShieldAlert className="w-5 h-5 mr-2 text-red-500" />
                    Alertas Recentes
                </h3>
                <span className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    {alerts.length}
                </span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {alerts.length === 0 ? (
                    <div className="text-center text-gray-400 dark:text-gray-500 py-8">
                        <p>Nenhuma violação detectada</p>
                    </div>
                ) : (
                    alerts.map((alert, index) => (
                        <div 
                            key={index} 
                            className={`flex items-start p-3 border rounded-md animate-in fade-in slide-in-from-right-4 ${
                                alert.severity === 'high' 
                                    ? 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/30' 
                                    : 'bg-orange-50 dark:bg-orange-900/20 border-orange-100 dark:border-orange-900/30'
                            }`}
                        >
                            <AlertTriangle className={`w-5 h-5 mt-0.5 mr-3 flex-shrink-0 ${
                                alert.severity === 'high' ? 'text-red-500' : 'text-orange-500'
                            }`} />
                            <div className="flex-1">
                                <p className={`text-sm font-medium ${
                                    alert.severity === 'high' ? 'text-red-800 dark:text-red-200' : 'text-orange-800 dark:text-orange-200'
                                }`}>
                                    Violação de EPI Detectada
                                </p>
                                <div className={`mt-1 text-xs space-y-1 ${
                                    alert.severity === 'high' ? 'text-red-600 dark:text-red-300' : 'text-orange-600 dark:text-orange-300'
                                }`}>
                                    <div className="flex items-center">
                                        <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                                            alert.severity === 'high' ? 'bg-red-400' : 'bg-orange-400'
                                        }`}></span>
                                        {alert.class} ({(alert.confidence * 100).toFixed(0)}%)
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 ml-2">
                                <Clock className="w-3 h-3 mr-1" />
                                {formatTime(alert.timestamp)}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AlertPanel;
