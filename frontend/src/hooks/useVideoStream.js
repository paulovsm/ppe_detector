import { useState, useCallback, useEffect, useRef } from 'react';

export function useVideoStream(canvasRef) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [fps, setFps] = useState(0);
    const frameCountRef = useRef(0);
    const lastTimeRef = useRef(Date.now());

    const renderFrame = useCallback((frameData) => {
        if (!canvasRef.current || !frameData) return;

        const ctx = canvasRef.current.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            // Resize canvas to match image dimensions if needed
            if (canvasRef.current.width !== img.width || canvasRef.current.height !== img.height) {
                canvasRef.current.width = img.width;
                canvasRef.current.height = img.height;
            }
            ctx.drawImage(img, 0, 0);
            
            // Calculate FPS
            frameCountRef.current++;
            const now = Date.now();
            if (now - lastTimeRef.current >= 1000) {
                setFps(frameCountRef.current);
                frameCountRef.current = 0;
                lastTimeRef.current = now;
            }
        };
        
        img.src = `data:image/jpeg;base64,${frameData}`;
    }, [canvasRef]);

    const togglePlay = useCallback(() => {
        setIsPlaying(prev => !prev);
    }, []);

    return { isPlaying, fps, renderFrame, togglePlay };
}
