export function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export function formatPct(n: number): string {
  return `${n.toFixed(1)}%`;
}

export function timeAgo(dateStr: string | null): string {
  if (!dateStr) return 'never';
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const sec = Math.floor((now - then) / 1000);
  if (sec < 60) return `${sec}s ago`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const days = Math.floor(hr / 24);
  return `${days}d ago`;
}

export function statusColor(dateStr: string | null): string {
  if (!dateStr) return 'text-gray-400';
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const min = (now - then) / 60000;
  if (min < 5) return 'text-green-400';
  if (min < 60) return 'text-yellow-400';
  return 'text-red-400';
}
