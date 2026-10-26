import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

let isOffline = false;
const listeners = new Set<(val: boolean) => void>();

export function setOfflineFallback(val: boolean) {
  if (isOffline !== val) {
    isOffline = val;
    listeners.forEach((fn) => fn(val));
    window.dispatchEvent(new CustomEvent('aicte:offline-fallback', { detail: { isOffline: val } }));
  }
}

export function getOfflineFallback(): boolean {
  return isOffline;
}

export function subscribeOfflineFallback(fn: (val: boolean) => void) {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('aicte_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token expiry handling & offline fallback telemetry
apiClient.interceptors.response.use(
  (response) => {
    // Successful backend request clears offline fallback
    setOfflineFallback(false);
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn('Unauthorized API response:', error.config?.url);
    }
    if (!error.response || error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
      setOfflineFallback(true);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
