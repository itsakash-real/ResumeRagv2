

import axios from 'axios';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 120s — AI pipeline with embeddings can be slow
});

// ── Request interceptor: inject Bearer token ──────────────────────────────────
api.interceptors.request.use(
  (config) => {
    // Read token directly from localStorage to avoid circular import with store
    const raw = localStorage.getItem('auth-storage');
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        const token = parsed?.state?.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch {
        // Corrupted storage — ignore and let request proceed unauthenticated
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle auth, rate limit, server errors ──────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      // Clear persisted auth state
      localStorage.removeItem('auth-storage');
      toast.error('Session expired — please log in again.');
      // Redirect without React Router (interceptor lives outside component tree)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (status === 429) {
      toast.error('Rate limit reached — try again in an hour.');
    } else if (status >= 500) {
      toast.error('Server error — please try again.');
    }

    return Promise.reject(error);
  }
);

export default api;