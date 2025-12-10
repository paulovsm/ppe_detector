import React, { useState, useRef } from 'react';
import { Upload, FileVideo, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadVideo } from '../services/api';

const VideoUploader = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        validateAndSetFile(droppedFile);
    };

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        validateAndSetFile(selectedFile);
    };

    const validateAndSetFile = (file) => {
        if (!file) return;
        
        const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm'];
        if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv|webm)$/i)) {
            setError('Formato de arquivo não suportado. Use MP4, AVI, MOV, MKV ou WEBM.');
            return;
        }

        if (file.size > 100 * 1024 * 1024) { // 100MB limit
            setError('Arquivo muito grande. O limite é 100MB.');
            return;
        }

        setFile(file);
        setError(null);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        try {
            const result = await uploadVideo(file, []); // Empty selected_epis for now
            onUploadComplete(result);
        } catch (err) {
            console.error(err);
            setError('Erro ao fazer upload do vídeo. Tente novamente.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Upload de Vídeo</h2>
            
            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragging 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="video/*"
                    onChange={handleFileSelect}
                />
                
                {!file ? (
                    <div className="flex flex-col items-center text-gray-500 dark:text-gray-400">
                        <Upload className="w-12 h-12 mb-2" />
                        <p className="font-medium">Arraste e solte ou clique para selecionar</p>
                        <p className="text-sm mt-1">MP4, AVI, MOV (Max 100MB)</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-blue-600 dark:text-blue-400">
                        <FileVideo className="w-12 h-12 mb-2" />
                        <p className="font-medium truncate max-w-xs">{file.name}</p>
                        <p className="text-sm mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                )}
            </div>

            {error && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md flex items-center text-sm">
                    <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                    {error}
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`mt-4 w-full py-2 px-4 rounded-md font-medium text-white transition-colors ${
                    !file || uploading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700'
                }`}
            >
                {uploading ? 'Enviando...' : 'Processar Vídeo'}
            </button>
        </div>
    );
};

export default VideoUploader;
