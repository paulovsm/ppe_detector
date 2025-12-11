import React from 'react';
import { X } from 'lucide-react';
import VideoUploader from './VideoUploader';
import StreamConfig from './StreamConfig';
import EPISelector from './EPISelector';

const SettingsModal = ({ 
    isOpen, 
    onClose, 
    inputType, 
    setInputType, 
    onUploadComplete, 
    onConnect, 
    onDisconnect, 
    isConnected,
    selectedEpis,
    onToggleEpi
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
                <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Configurações</h2>
                    <button 
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>
                
                <div className="p-6 space-y-8">
                    {/* EPI Selector Section */}
                    <section>
                        <EPISelector selectedEpis={selectedEpis} onToggle={onToggleEpi} />
                    </section>

                    {/* Input Source Section */}
                    <section className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4">
                        <h3 className="font-semibold text-gray-800 dark:text-white mb-4">Fonte de Vídeo</h3>
                        <div className="flex space-x-4 mb-6 border-b border-gray-200 dark:border-gray-600 pb-2">
                            <button
                                className={`pb-2 px-1 ${inputType === 'upload' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}
                                onClick={() => setInputType('upload')}
                            >
                                Upload de Arquivo
                            </button>
                            <button
                                className={`pb-2 px-1 ${inputType === 'stream' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}
                                onClick={() => setInputType('stream')}
                            >
                                Streaming (RTMP/SRT)
                            </button>
                        </div>
                        
                        {inputType === 'upload' ? (
                            <VideoUploader onUploadComplete={(result) => {
                                onUploadComplete(result);
                                onClose();
                            }} />
                        ) : (
                            <StreamConfig 
                                onConnect={(result) => {
                                    onConnect(result);
                                    onClose();
                                }}
                                onDisconnect={onDisconnect}
                                isConnected={isConnected}
                            />
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
