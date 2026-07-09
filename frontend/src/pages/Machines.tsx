import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Layout } from '../components/Layout';
import { statusColor, timeAgo } from '../utils/format';

interface Agent {
  id: string;
  name: string;
  os: string;
  rtk_version: string;
  last_sync_at: string | null;
  created_at: string;
}

export function Machines() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.agents
      .list()
      .then(setAgents)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <h2 className="text-lg font-semibold text-white mb-4">Machines</h2>
      {loading ? (
        <div className="text-gray-500 text-sm">Loading...</div>
      ) : agents.length === 0 ? (
        <div className="text-gray-500 text-sm">No machines registered yet.</div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-left">
                <th className="p-3 font-medium">Name</th>
                <th className="p-3 font-medium">OS</th>
                <th className="p-3 font-medium">RTK Version</th>
                <th className="p-3 font-medium">Status</th>
                <th className="p-3 font-medium">Last Sync</th>
              </tr>
            </thead>
            <tbody>
              {agents.map((a) => (
                <tr key={a.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-3 text-white">{a.name}</td>
                  <td className="p-3 text-gray-400">{a.os || '-'}</td>
                  <td className="p-3 text-gray-400">{a.rtk_version || '-'}</td>
                  <td className="p-3">
                    <span className={`inline-flex items-center gap-1.5 ${statusColor(a.last_sync_at)}`}>
                      <span className="w-2 h-2 rounded-full bg-current" />
                      {a.last_sync_at ? 'Online' : 'Offline'}
                    </span>
                  </td>
                  <td className="p-3 text-gray-400">{timeAgo(a.last_sync_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
