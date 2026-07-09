import { useDashboard } from '../hooks/useDashboard';
import { Layout } from '../components/Layout';
import { formatTokens, formatPct } from '../utils/format';

export function Commands() {
  const { commands, loading } = useDashboard();

  return (
    <Layout>
      <h2 className="text-lg font-semibold text-white mb-4">Command Breakdown</h2>
      {loading ? (
        <div className="text-gray-500 text-sm">Loading...</div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-left">
                <th className="p-3 font-medium">Command</th>
                <th className="p-3 font-medium">Count</th>
                <th className="p-3 font-medium">Tokens Saved</th>
                <th className="p-3 font-medium">Avg Savings</th>
              </tr>
            </thead>
            <tbody>
              {commands.map((c) => (
                <tr key={c.cmd_type} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-3 text-white">{c.cmd_type}</td>
                  <td className="p-3 text-gray-400">{c.count}</td>
                  <td className="p-3 text-sky-400">{formatTokens(c.saved_tokens)}</td>
                  <td className="p-3 text-green-400">{formatPct(c.savings_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
