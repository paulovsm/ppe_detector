import React, { useState, useCallback, useEffect } from 'react';
import VideoUploader from './VideoUploader';
import StreamConfig from './StreamConfig';
import StreamViewer from './StreamViewer';
import AlertPanel from './AlertPanel';
import StatsPanel from './StatsPanel';
import EPISelector from './EPISelector';
import Toast from './Toast';
import { LayoutDashboard, Video, Settings, Moon, Sun } from 'lucide-react';

const Dashboard = () => {
    const [activeVideoId, setActiveVideoId] = useState(null);
    const [activeStreamUrl, setActiveStreamUrl] = useState(null);
    const [inputType, setInputType] = useState('upload');
    const [currentStats, setCurrentStats] = useState(null);
    const [recentAlerts, setRecentAlerts] = useState([]);
    const [selectedEpis, setSelectedEpis] = useState(['Hardhat', 'Mask', 'Safety Vest', 'Person']);
    const [toast, setToast] = useState(null);
    const [isDarkMode, setIsDarkMode] = useState(false);

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [isDarkMode]);

    const handleUploadComplete = (result) => {
        console.log('Upload complete:', result);
        setActiveVideoId(result.video_id);
        setActiveStreamUrl(null);
        // Reset alerts when starting new video
        setRecentAlerts([]);
    };

    const handleStreamConnect = (result) => {
        console.log('Stream connected:', result);
        setActiveStreamUrl(result.stream_url);
        setActiveVideoId(null);
        setRecentAlerts([]);
    };

    const handleStatsUpdate = useCallback((stats) => {
        setCurrentStats(stats);
    }, []);

    const handleAlert = useCallback((alert) => {
        setRecentAlerts(prev => [alert, ...prev].slice(0, 50));
        setToast({
            message: `Violação detectada: ${alert.class}`,
            type: 'error'
        });
    }, []);

    const toggleEpi = (epiId) => {
        setSelectedEpis(prev => 
            prev.includes(epiId) 
                ? prev.filter(id => id !== epiId)
                : [...prev, epiId]
        );
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
            {toast && (
                <Toast 
                    message={toast.message} 
                    type={toast.type} 
                    onClose={() => setToast(null)} 
                />
            )}
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-20 transition-colors duration-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center">
                        <LayoutDashboard className="w-6 h-6 text-blue-600 mr-2" />
                        <h1 className="text-xl font-bold text-gray-900 dark:text-white">PPE Monitor</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <button 
                            onClick={() => setIsDarkMode(!isDarkMode)}
                            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                        </button>
                        <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                            <Settings className="w-5 h-5" />
                        </button>
                        <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold">
                            A
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                
                {/* Stats Row */}
                <StatsPanel stats={currentStats} />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Left Column: Video Area */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-1 transition-colors duration-200">
                            {activeVideoId || activeStreamUrl ? (
                                <StreamViewer 
                                    videoId={activeVideoId}
                                    streamUrl={activeStreamUrl}
                                    onStatsUpdate={handleStatsUpdate}
                                    onAlert={handleAlert}
                                />
                            ) : (
                                <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-400 dark:text-gray-500">
                                    <div className="text-center">
                                        <Video className="w-12 h-12 mx-auto mb-2" />
                                        <p>Nenhum vídeo selecionado</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Section */}
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
                            <div className="flex space-x-4 mb-6 border-b border-gray-200 dark:border-gray-700 pb-2">
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
                                <VideoUploader onUploadComplete={handleUploadComplete} />
                            ) : (
                                <StreamConfig onConnect={handleStreamConnect} />
                            )}
                        </div>
                    </div>

                    {/* Right Column: Alerts & Controls */}
                    <div className="space-y-6">
                        <EPISelector selectedEpis={selectedEpis} onToggle={toggleEpi} />
                        <div className="h-[600px]">
                            <AlertPanel alerts={recentAlerts} />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
