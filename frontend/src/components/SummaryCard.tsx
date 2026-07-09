interface Props {
  title: string;
  value: string;
  subtitle?: string;
  color?: string;
}

export function SummaryCard({ title, value, subtitle, color = 'text-sky-400' }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="text-sm text-gray-500 mb-1">{title}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      {subtitle && <div className="text-xs text-gray-600 mt-1">{subtitle}</div>}
    </div>
  );
}
