

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';
import { loginRequest, signupRequest } from '../services/auth.service';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [fieldError, setFieldError] = useState('');
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const login = async (email, password) => {
    setLoading(true);
    setFieldError('');
    try {
      const { data } = await loginRequest(email, password);
      setAuth({ email }, data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Login failed.';
      setFieldError(detail);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password) => {
    setLoading(true);
    setFieldError('');
    try {
      const { data } = await signupRequest(email, password);
      setAuth({ email }, data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Signup failed.';
      setFieldError(detail);
    } finally {
      setLoading(false);
    }
  };

  return { login, signup, loading, fieldError };
}