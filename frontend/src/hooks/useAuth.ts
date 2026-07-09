import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';

function loadUser() {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<{ id: string; email: string; name: string; role: string } | null>(loadUser);

  const isAuthenticated = !!localStorage.getItem('access_token');
  const isAdmin = user?.role === 'admin';

  const fetchUser = useCallback(async () => {
    try {
      const u = await api.auth.me();
      localStorage.setItem('user', JSON.stringify(u));
      setUser(u);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchUser();
    }
  }, [isAuthenticated, user, fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.login({ email, password });
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);
      await fetchUser();
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchUser]);

  const register = useCallback(async (email: string, password: string, name: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.register({ email, password, name });
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);
      await fetchUser();
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchUser]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }, []);

  return { login, register, logout, isAuthenticated, isAdmin, user, loading, error };
}
