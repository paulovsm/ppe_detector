import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

export const uploadVideo = async (file, selectedEpis) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('selected_epis', JSON.stringify(selectedEpis));

    const response = await api.post('/video/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getStatus = async () => {
    const response = await api.get('/status');
    return response.data;
};

export const getClasses = async () => {
    const response = await api.get('/classes');
    return response.data;
};

export const connectStream = async (streamUrl, protocol) => {
    const formData = new FormData();
    formData.append('stream_url', streamUrl);
    formData.append('protocol', protocol);

    const response = await api.post('/stream/connect', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const disconnectStream = async (streamId) => {
    const formData = new FormData();
    formData.append('stream_id', streamId);

    const response = await api.post('/stream/disconnect', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export default api;
