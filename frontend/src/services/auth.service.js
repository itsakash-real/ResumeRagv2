
import api from './api';

export const signupRequest = (email, password) =>
  api.post('/auth/signup', { email, password });

export const loginRequest = (email, password) =>
  api.post('/auth/login', { email, password });