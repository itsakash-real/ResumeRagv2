

export default function ScoreBadge({ score }) {
  const config =
    score >= 80
      ? { bg: 'bg-emerald-50 border-emerald-200', text: 'text-emerald-700', label: 'Strong Match' }
      : score >= 60
      ? { bg: 'bg-amber-50 border-amber-200', text: 'text-amber-700', label: 'Good Match' }
      : { bg: 'bg-slate-100 border-slate-200', text: 'text-slate-700', label: 'Partial Match' };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${config.bg} shadow-inner`}>
      <span className={`font-mono text-xs font-black tracking-wide ${config.text}`}>
        {score.toFixed(1)}%
      </span>
      <span className={`text-[10px] font-bold uppercase tracking-wider ${config.text} opacity-90`}>{config.label}</span>
    </div>
  );
}