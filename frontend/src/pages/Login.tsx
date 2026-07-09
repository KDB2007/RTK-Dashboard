import type { FormEvent } from 'react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const ok = await login(email, password);
    if (ok) navigate('/');
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-950">
      <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-800 rounded-lg p-8 w-96">
        <h1 className="text-xl font-semibold text-white mb-6">RTK Dashboard</h1>
        {error && <div className="text-red-400 text-sm mb-4">{error}</div>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded mb-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded mb-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 bg-sky-600 text-white rounded text-sm font-medium hover:bg-sky-700 disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Login'}
        </button>
        <p className="text-sm text-gray-500 mt-4 text-center">
          No account?{' '}
          <Link to="/register" className="text-sky-400 hover:text-sky-300">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}
