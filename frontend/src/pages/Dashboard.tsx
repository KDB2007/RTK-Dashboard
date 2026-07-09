import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Layout } from '../components/Layout';
import { TrendChart } from '../components/TrendChart';
import { useDashboard } from '../hooks/useDashboard';
import { formatPct } from '../utils/format';

function pctColor(pct: number): string {
  if (pct === 0) return '#6b7280';
  const p = Math.min(pct, 100);
  if (p > 80) return '#22c55e';
  if (p > 50) return '#eab308';
  if (p > 20) return '#f97316';
  return '#ef4444';
}

function ImpactBar({ pct }: { pct: number }) {
  const p = Math.min(pct, 100);
  return (
    <div className="w-24 h-2.5 bg-gray-700 rounded-full overflow-hidden">
      <div className="h-full rounded-full" style={{ width: `${p}%`, backgroundColor: pctColor(pct) }} />
    </div>
  );
}

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
      <div className="text-xs text-gray-500 mb-1 uppercase tracking-wider">{label}</div>
      <div className="text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function toIST(utcStr: string): string {
  const d = new Date(utcStr);
  const ist = new Date(d.getTime() + 5.5 * 60 * 60 * 1000);
  return ist.toLocaleString('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

export function Dashboard() {
  const { summary, commands, trends, loading } = useDashboard();
  const [history, setHistory] = useState<Awaited<ReturnType<typeof api.dashboard.history>>>([]);

  useEffect(() => {
    const fetch = () => api.dashboard.history(50).then(setHistory).catch(() => {});
    fetch();
    const interval = setInterval(fetch, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !summary) {
    return (
      <Layout>
        <div className="text-gray-500 text-sm mt-10">Loading...</div>
      </Layout>
    );
  }

  const execSec = Math.floor(summary.total_exec_time / 1000);
  const execMin = Math.floor(execSec / 60);
  const execHr = Math.floor(execMin / 60);
  const execStr = execHr > 0
    ? `${execHr}h ${execMin % 60}m ${execSec % 60}s`
    : execMin > 0
      ? `${execMin}m ${execSec % 60}s`
      : `${execSec}s`;

  return (
    <Layout>
      <h2 className="text-lg font-semibold text-white mb-4">Overview</h2>
      <div className="grid grid-cols-5 gap-3 mb-6">
        <Card label="Commands tracked" value={summary.total_commands.toLocaleString()} />
        <Card label="Input tokens" value={summary.total_input_tokens.toLocaleString()} />
        <Card label="Output tokens" value={summary.total_output_tokens.toLocaleString()} />
        <Card label="Tokens saved" value={`${summary.total_saved_tokens.toLocaleString()} (${formatPct(summary.savings_pct)})`} />
        <Card label="Total execution time" value={execStr} />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="col-span-2">
          <TrendChart data={trends} />
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Token Comparison by Command</h3>
          <div className="space-y-3">
            {commands.slice(0, 6).map((c) => {
              const maxVal = Math.max(c.input_tokens, c.output_tokens, 1);
              return (
                <div key={c.cmd_type}>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>{c.cmd_type}</span>
                    <span className="text-sky-400">{c.saved_tokens.toLocaleString()} saved</span>
                  </div>
                  <div className="relative h-4 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="absolute inset-y-0 left-0 bg-cyan-600 rounded-full"
                      style={{ width: `${(c.output_tokens / maxVal) * 100}%` }}
                    />
                    <div
                      className="absolute inset-y-0 left-0 bg-sky-400 rounded-full opacity-50"
                      style={{ width: `${(c.input_tokens / maxVal) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-500 mt-0.5">
                    <span>RTK: {c.output_tokens.toLocaleString()}</span>
                    <span>Original: {c.input_tokens.toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-medium text-gray-400">All Commands</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs whitespace-nowrap">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-left">
                <th className="p-3 font-medium">#</th>
                <th className="p-3 font-medium">Timestamp (IST)</th>
                <th className="p-3 font-medium">Original command</th>
                <th className="p-3 font-medium">RTK command</th>
                <th className="p-3 font-medium text-right">Input</th>
                <th className="p-3 font-medium text-right">Output</th>
                <th className="p-3 font-medium text-right">Saved</th>
                <th className="p-3 font-medium text-right">%</th>
                <th className="p-3 font-medium">Bar</th>
              </tr>
            </thead>
            <tbody>
              {history.map((c, i) => (
                <tr key={c.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-3 text-gray-500">{i + 1}</td>
                  <td className="p-3 text-gray-400 text-xs">{toIST(c.ran_at)}</td>
                  <td className="p-3 text-gray-300 max-w-60 truncate" title={c.original_cmd}>
                    {c.original_cmd}
                  </td>
                  <td className="p-3 text-gray-300 max-w-60 truncate" title={c.rtk_cmd}>
                    {c.rtk_cmd}
                  </td>
                  <td className="p-3 text-gray-400 text-right">{c.input_tokens.toLocaleString()}</td>
                  <td className="p-3 text-gray-400 text-right">{c.output_tokens.toLocaleString()}</td>
                  <td className="p-3 text-sky-400 text-right">{c.saved_tokens.toLocaleString()}</td>
                  <td className="p-3 text-right" style={{ color: pctColor(c.savings_pct) }}>{formatPct(c.savings_pct)}</td>
                  <td className="p-3"><ImpactBar pct={c.savings_pct} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
