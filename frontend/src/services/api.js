import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        Cookies.set('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
};

// Properties API
export const propertiesAPI = {
  list: (params) => api.get('/properties/', { params }),
  get: (id) => api.get(`/properties/${id}/`),
  create: (data) => api.post('/properties/', data),
  myProperties: () => api.get('/properties/my-properties/'),
};

// Applications API
export const applicationsAPI = {
  submit: (data) => api.post('/applications/submit/', data),
  myApplications: () => api.get('/applications/my-applications/'),
  received: () => api.get('/applications/received/'),
  respond: (id, data) => api.put(`/applications/${id}/respond/`, data),
};

export default api;