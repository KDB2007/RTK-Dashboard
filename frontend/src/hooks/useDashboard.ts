import { useEffect, useState } from 'react';
import { api } from '../api/client';

export function useDashboard() {
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof api.dashboard.summary>> | null>(null);
  const [commands, setCommands] = useState<Awaited<ReturnType<typeof api.dashboard.commands>>>([]);
  const [trends, setTrends] = useState<Awaited<ReturnType<typeof api.dashboard.trends>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    try {
      const [s, c, t] = await Promise.all([
        api.dashboard.summary(),
        api.dashboard.commands(),
        api.dashboard.trends(),
      ]);
      setSummary(s);
      setCommands(c);
      setTrends(t);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    const interval = setInterval(fetch, 10000);
    return () => clearInterval(interval);
  }, []);

  return { summary, commands, trends, loading, error, refresh: fetch };
}
