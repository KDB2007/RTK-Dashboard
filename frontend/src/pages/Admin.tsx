import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { Layout } from '../components/Layout';
import { formatPct } from '../utils/format';

interface UserSummary {
  user_id: string;
  email: string;
  name: string;
  total_commands: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_saved_tokens: number;
  total_exec_time: number;
  savings_pct: number;
}

export function Admin() {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.admin.users().then(setUsers).finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <h2 className="text-lg font-semibold text-white mb-4">Admin — All Users</h2>
      {loading ? (
        <div className="text-gray-500 text-sm">Loading...</div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-xs whitespace-nowrap">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-left">
                <th className="p-3 font-medium">Email</th>
                <th className="p-3 font-medium">Name</th>
                <th className="p-3 font-medium text-right">Commands</th>
                <th className="p-3 font-medium text-right">Input</th>
                <th className="p-3 font-medium text-right">Output</th>
                <th className="p-3 font-medium text-right">Saved</th>
                <th className="p-3 font-medium text-right">%</th>
                <th className="p-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.user_id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-3 text-gray-300">{u.email}</td>
                  <td className="p-3 text-white">{u.name}</td>
                  <td className="p-3 text-gray-400 text-right">{u.total_commands.toLocaleString()}</td>
                  <td className="p-3 text-gray-400 text-right">{u.total_input_tokens.toLocaleString()}</td>
                  <td className="p-3 text-gray-400 text-right">{u.total_output_tokens.toLocaleString()}</td>
                  <td className="p-3 text-sky-400 text-right">{u.total_saved_tokens.toLocaleString()}</td>
                  <td className="p-3 text-right" style={{ color: u.savings_pct > 0 ? (u.savings_pct > 80 ? '#22c55e' : u.savings_pct > 50 ? '#eab308' : u.savings_pct > 20 ? '#f97316' : '#ef4444') : '#6b7280' }}>{formatPct(u.savings_pct)}</td>
                  <td className="p-3">
                    <Link
                      to={`/admin/users/${u.user_id}`}
                      className="text-sky-400 hover:text-sky-300 text-xs"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
