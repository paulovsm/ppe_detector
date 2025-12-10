import React, { useState } from 'react';
import { Radio, Link, AlertCircle } from 'lucide-react';
import { connectStream } from '../services/api';

const StreamConfig = ({ onConnect }) => {
    const [url, setUrl] = useState('');
    const [protocol, setProtocol] = useState('rtmp');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!url) return;

        setLoading(true);
        setError(null);

        try {
            const result = await connectStream(url, protocol);
            onConnect(result);
        } catch (err) {
            console.error(err);
            setError('Erro ao conectar à stream. Verifique a URL e tente novamente.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white flex items-center">
                <Radio className="w-6 h-6 mr-2 text-blue-600" />
                Configuração de Stream
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Protocolo
                    </label>
                    <div className="flex space-x-4">
                        {['rtmp', 'srt'].map((p) => (
                            <label key={p} className="flex items-center cursor-pointer">
                                <input
                                    type="radio"
                                    name="protocol"
                                    value={p}
                                    checked={protocol === p}
                                    onChange={(e) => setProtocol(e.target.value)}
                                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                                />
                                <span className="ml-2 text-gray-700 dark:text-gray-300 uppercase">{p}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        URL da Stream
                    </label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Link className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder={protocol === 'rtmp' ? 'rtmp://localhost/live/stream' : 'srt://localhost:8890'}
                            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {protocol === 'rtmp' 
                            ? 'Ex: rtmp://192.168.1.100/live/cam1' 
                            : 'Ex: srt://192.168.1.100:8890?mode=caller'}
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <AlertCircle className="h-5 w-5 text-red-400" />
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-700 dark:text-red-200">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={loading || !url}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                        (loading || !url) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {loading ? 'Conectando...' : 'Conectar Stream'}
                </button>
            </form>
        </div>
    );
};

export default StreamConfig;
