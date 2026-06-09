import axios from 'axios';

const TOKEN_KEY = 'token';
const USER_KEY = 'user';

export const saveAuthData = (token, username) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, username);
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const clearAuthData = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  delete axios.defaults.headers.common['Authorization'];
};

export const isAuthenticated = () => Boolean(localStorage.getItem(TOKEN_KEY));

export const getStoredUser = () => localStorage.getItem(USER_KEY) || '';

export const getAuthHeaders = () => {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
};
