import { useState, useEffect, useCallback, useRef } from 'react';

export function useWebSocket(url) {
    const [isConnected, setIsConnected] = useState(false);
    const [lastFrame, setLastFrame] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState({});
    const socketRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    const connect = useCallback(() => {
        if (socketRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(url);
        socketRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket Connected');
            setIsConnected(true);
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                
                switch (message.type) {
                    case 'frame':
                        setLastFrame(message.data);
                        break;
                    case 'alert':
                        setAlerts(prev => [message.data, ...prev].slice(0, 50)); // Keep last 50 alerts
                        break;
                    case 'stats':
                        setStats(message.data);
                        break;
                    case 'status':
                        console.log('Status:', message.message);
                        break;
                    case 'error':
                        console.error('Server Error:', message.message);
                        break;
                    default:
                        // console.log('Unknown message type:', message.type);
                        break;
                }
            } catch (e) {
                console.error('Error parsing message:', e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket Disconnected');
            setIsConnected(false);
            // Auto reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                console.log('Attempting to reconnect...');
                connect();
            }, 3000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            ws.close();
        };

    }, [url]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (socketRef.current) {
            socketRef.current.close();
            socketRef.current = null;
        }
    }, []);

    const sendMessage = useCallback((message) => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    useEffect(() => {
        connect();
        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return { isConnected, lastFrame, alerts, stats, sendMessage };
}
