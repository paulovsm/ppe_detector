import React, { useEffect, useRef, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useVideoStream } from '../hooks/useVideoStream';
import { Play, Pause, Activity } from 'lucide-react';

const StreamViewer = ({ videoId, streamUrl, onStatsUpdate, onAlert }) => {
    const canvasRef = useRef(null);
    const clientId = useRef(Math.random().toString(36).substring(7)).current;
    
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const WS_URL = API_URL.replace(/^http/, 'ws');
    
    const { isConnected, lastFrame, alerts, stats, sendMessage } = useWebSocket(`${WS_URL}/ws/video/${clientId}`);
    const { isPlaying, fps, renderFrame, togglePlay } = useVideoStream(canvasRef);
    
    const [processingStarted, setProcessingStarted] = useState(false);

    // Handle incoming frames
    useEffect(() => {
        if (lastFrame) {
            renderFrame(lastFrame);
        }
    }, [lastFrame, renderFrame]);

    // Handle alerts and stats
    useEffect(() => {
        if (alerts.length > 0 && onAlert) {
            onAlert(alerts[0]); // Send latest alert
        }
    }, [alerts, onAlert]);

    useEffect(() => {
        if (stats && onStatsUpdate) {
            onStatsUpdate(stats);
        }
    }, [stats, onStatsUpdate]);

    // Start processing when connected and videoId/streamUrl is available
    useEffect(() => {
        if (isConnected && !processingStarted && (videoId || streamUrl)) {
            sendMessage({
                action: 'start_processing',
                video_id: videoId,
                stream_url: streamUrl
            });
            setProcessingStarted(true);
        }
    }, [isConnected, videoId, streamUrl, processingStarted, sendMessage]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (isConnected) {
                sendMessage({ action: 'stop_processing' });
            }
        };
    }, [isConnected, sendMessage]);

    return (
        <div className="relative w-full bg-black rounded-lg overflow-hidden shadow-lg aspect-video">
            {!isConnected && (
                <div className="absolute inset-0 flex items-center justify-center text-white bg-gray-900 bg-opacity-80 z-10">
                    <div className="text-center">
                        <Activity className="w-10 h-10 mx-auto mb-2 animate-pulse" />
                        <p>Conectando ao servidor...</p>
                    </div>
                </div>
            )}
            
            <canvas 
                ref={canvasRef} 
                className="w-full h-full object-contain"
            />
            
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 flex justify-between items-center text-white">
                <div className="flex items-center space-x-4">
                    <button 
                        onClick={togglePlay}
                        className="p-2 hover:bg-white/20 rounded-full transition-colors"
                    >
                        {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                    </button>
                    <div className="text-sm font-mono">
                        <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        {isConnected ? 'AO VIVO' : 'OFFLINE'}
                    </div>
                </div>
                
                <div className="text-sm font-mono">
                    FPS: {fps}
                </div>
            </div>
        </div>
    );
};

export default StreamViewer;
