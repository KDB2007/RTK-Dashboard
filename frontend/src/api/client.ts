const rawBase = import.meta.env.VITE_API_URL || '';
const API_BASE = rawBase ? (rawBase.startsWith('http') ? rawBase : `https://${rawBase}`) : '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh && path !== '/auth/refresh') {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem('access_token', data.access_token);
        headers['Authorization'] = `Bearer ${data.access_token}`;
        const retryRes = await fetch(`${API_BASE}${path}`, { ...options, headers });
        if (!retryRes.ok) throw new Error(await retryRes.text());
        return retryRes.json();
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  return res.json();
}

export const api = {
  auth: {
    register: (body: { email: string; password: string; name: string }) =>
      request<{ access_token: string; refresh_token: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    login: (body: { email: string; password: string }) =>
      request<{ access_token: string; refresh_token: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    me: () =>
      request<{ id: string; email: string; name: string; role: string; created_at: string }>(
        '/auth/me'
      ),
  },
  dashboard: {
    summary: (userId?: string) => {
      const qs = userId ? `?user_id=${userId}` : '';
      return request<{
        total_commands: number;
        total_input_tokens: number;
        total_output_tokens: number;
        total_saved_tokens: number;
        total_exec_time: number;
        savings_pct: number;
        machine_count: number;
        active_machines: number;
      }>(`/dashboard/summary${qs}`);
    },
    commands: (userId?: string) => {
      const qs = userId ? `?user_id=${userId}` : '';
      return request<Array<{ cmd_type: string; count: number; input_tokens: number; output_tokens: number; saved_tokens: number; savings_pct: number }>>(
        `/dashboard/commands${qs}`
      );
    },
    trends: (days = 30, userId?: string) => {
      const qs = userId ? `?days=${days}&user_id=${userId}` : `?days=${days}`;
      return request<Array<{ date: string; commands: number; saved_tokens: number; savings_pct: number }>>(
        `/dashboard/trends${qs}`
      );
    },
    history: (limit = 50, offset = 0, userId?: string) => {
      const qs = userId ? `?limit=${limit}&offset=${offset}&user_id=${userId}` : `?limit=${limit}&offset=${offset}`;
      return request<
        Array<{
          id: number;
          original_cmd: string;
          rtk_cmd: string;
          input_tokens: number;
          output_tokens: number;
          saved_tokens: number;
          savings_pct: number;
          exec_time_ms: number;
          ran_at: string;
        }>
      >(`/dashboard/history${qs}`);
    },
  },
  agents: {
    list: () =>
      request<
        Array<{
          id: string;
          name: string;
          os: string;
          rtk_version: string;
          last_sync_at: string | null;
          created_at: string;
        }>
      >('/agents'),
  },
  admin: {
    users: () =>
      request<
        Array<{
          user_id: string;
          email: string;
          name: string;
          total_commands: number;
          total_input_tokens: number;
          total_output_tokens: number;
          total_saved_tokens: number;
          total_exec_time: number;
          savings_pct: number;
        }>
      >('/admin/users'),
  },
};
