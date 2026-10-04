import api from './api';

export const authService = {
  /**
   * Register a new user account with FastAPI backend
   * @param {Object} userData 
   * @returns {Promise<Object>}
   */
  async register({ fullName, email, password, confirmPassword, termsAccepted }) {
    const payload = {
      full_name: fullName,
      email: email.trim().toLowerCase(),
      password,
      confirm_password: confirmPassword,
      terms_accepted: termsAccepted,
    };
    const response = await api.post('/auth/register', payload);
    return response.data;
  },

  /**
   * Login user with FastAPI backend
   * @param {Object} credentials
   * @returns {Promise<Object>}
   */
  async login({ email, password, rememberMe }) {
    const payload = {
      email: email.trim().toLowerCase(),
      password,
      remember_me: Boolean(rememberMe),
    };
    const response = await api.post('/auth/login', payload);
    return response.data;
  },

  /**
   * Get current authenticated user details from FastAPI backend
   * @returns {Promise<Object>}
   */
  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Sign out and clear stored session tokens
   */
  logout() {
    localStorage.removeItem('ff_token');
    localStorage.removeItem('ff_user');
    sessionStorage.removeItem('ff_token');
    sessionStorage.removeItem('ff_user');
  },
};
