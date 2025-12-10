import React, { useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';

const Toast = ({ message, type = 'error', onClose, duration = 3000 }) => {
    useEffect(() => {
        if (duration) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const bgColor = type === 'error' ? 'bg-red-500' : 'bg-blue-500';

    return (
        <div className={`fixed top-4 right-4 z-50 flex items-center p-4 mb-4 text-white rounded-lg shadow-lg ${bgColor} animate-in slide-in-from-right`}>
            <div className="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-red-500 bg-white rounded-lg">
                <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="ml-3 text-sm font-normal">{message}</div>
            <button 
                onClick={onClose}
                className="ml-auto -mx-1.5 -my-1.5 bg-transparent text-white hover:text-gray-200 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 inline-flex h-8 w-8"
            >
                <X className="w-5 h-5" />
            </button>
        </div>
    );
};

export default Toast;
