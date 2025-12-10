import React, { useState, useEffect } from 'react';
import { Radio, AlertCircle, Play, Square } from 'lucide-react';
import { connectStream } from '../services/api';

const StreamConfig = ({ onConnect, onDisconnect, isConnected }) => {
    const [protocol, setProtocol] = useState('rtmp');
    const [streamKey, setStreamKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [hostname, setHostname] = useState('localhost');

    useEffect(() => {
        setHostname(window.location.hostname);
        // Gerar chave simples
        setStreamKey('ppe_stream_' + Math.floor(Math.random() * 1000));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const result = await connectStream(streamKey, protocol);
            onConnect(result);
        } catch (err) {
            console.error(err);
            setError('Erro ao iniciar processamento. Verifique se o OBS está transmitindo para o servidor.');
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnect = async () => {
        setLoading(true);
        try {
            await onDisconnect();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getServerUrl = () => {
        if (protocol === 'rtmp') return `rtmp://${hostname}:1935/live`;
        return `srt://${hostname}:8890`;
    };

    const getObsUrl = () => {
        if (protocol === 'rtmp') return `rtmp://${hostname}:1935/live`;
        return `srt://${hostname}:8890?streamid=publish:${streamKey}`;
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white flex items-center">
                <Radio className="w-6 h-6 mr-2 text-blue-600" />
                Servidor de Streaming
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                                    disabled={isConnected}
                                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 disabled:opacity-50"
                                />
                                <span className="ml-2 text-gray-700 dark:text-gray-300 uppercase">{p}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md space-y-3">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Configuração no OBS Studio
                    </h3>
                    
                    <div>
                        <label className="block text-xs text-gray-500 dark:text-gray-400 uppercase">Servidor</label>
                        <div className="flex items-center mt-1">
                            <code className="flex-1 block w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-mono text-gray-900 dark:text-white break-all">
                                {getServerUrl()}
                            </code>
                        </div>
                    </div>

                    {protocol === 'rtmp' && (
                        <div>
                            <label className="block text-xs text-gray-500 dark:text-gray-400 uppercase">Chave da Stream</label>
                            <div className="flex items-center mt-1">
                                <code className="flex-1 block w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-mono text-gray-900 dark:text-white">
                                    {streamKey}
                                </code>
                            </div>
                        </div>
                    )}

                    {protocol === 'srt' && (
                        <div>
                            <label className="block text-xs text-gray-500 dark:text-gray-400 uppercase">URL Completa (SRT)</label>
                            <div className="flex items-center mt-1">
                                <code className="flex-1 block w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-mono text-gray-900 dark:text-white break-all">
                                    {getObsUrl()}
                                </code>
                            </div>
                        </div>
                    )}
                </div>

                <div className="text-sm text-gray-600 dark:text-gray-400">
                    <p>1. Configure o OBS com os dados acima.</p>
                    <p>2. Inicie a transmissão no OBS.</p>
                    <p>3. Clique no botão abaixo para iniciar a detecção.</p>
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

                {!isConnected ? (
                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                            loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                    >
                        {loading ? 'Conectando...' : (
                            <>
                                <Play className="w-4 h-4 mr-2" />
                                Iniciar Detecção
                            </>
                        )}
                    </button>
                ) : (
                    <button
                        type="button"
                        onClick={handleDisconnect}
                        disabled={loading}
                        className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 ${
                            loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                    >
                        {loading ? 'Desconectando...' : (
                            <>
                                <Square className="w-4 h-4 mr-2 fill-current" />
                                Parar Detecção
                            </>
                        )}
                    </button>
                )}
            </form>
        </div>
    );
};

export default StreamConfig;
