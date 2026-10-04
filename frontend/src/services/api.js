import axios from 'axios';

// Base URL strictly from environment variable as mandated
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to attach bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ff_token') || sessionStorage.getItem('ff_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors gracefully
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let userFriendlyMessage = 'An unexpected error occurred. Please try again.';

    if (error.response) {
      const { status, data } = error.response;

      if (status === 401) {
        // Clear invalid auth state
        localStorage.removeItem('ff_token');
        localStorage.removeItem('ff_user');
        sessionStorage.removeItem('ff_token');
        sessionStorage.removeItem('ff_user');

        // Only redirect if not already on login/register to avoid infinite loop
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
          window.location.href = '/login?session_expired=true';
        }
        userFriendlyMessage = 'Your session has expired. Please sign in again.';
      } else if (status === 400) {
        userFriendlyMessage = data?.detail || data?.message || 'Invalid request. Please check your input.';
      } else if (status === 403) {
        userFriendlyMessage = 'You do not have permission to perform this action.';
      } else if (status === 404) {
        userFriendlyMessage = data?.detail || 'The requested resource was not found.';
      } else if (status === 422) {
        // FastAPI validation error formatting
        if (Array.isArray(data?.detail)) {
          userFriendlyMessage = data.detail.map((err) => `${err.loc?.slice(-1)[0] || 'Field'}: ${err.msg}`).join(', ');
        } else {
          userFriendlyMessage = data?.detail || 'Validation failed for submitted data.';
        }
      } else if (status >= 500) {
        userFriendlyMessage = 'Server error encountered. Our team has been alerted.';
      }
    } else if (error.request) {
      userFriendlyMessage = 'Unable to connect to the backend server. Please verify the service is running.';
    }

    const customError = new Error(userFriendlyMessage);
    customError.status = error.response?.status;
    customError.originalError = error;
    return Promise.reject(customError);
  }
);

export default api;
