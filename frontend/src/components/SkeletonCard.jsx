

export default function SkeletonCard() {
  return (
    <div className="glass-panel rounded-2xl p-6 animate-pulse">
      {/* Header row: title + score badge placeholder */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 mr-4">
          <div className="h-6 bg-slate-200/80 rounded-lg w-3/4 mb-2" />
          <div className="h-4 bg-slate-200/60 rounded-md w-1/2" />
        </div>
        <div className="h-7 w-28 bg-slate-200/80 rounded-full flex-shrink-0" />
      </div>

      {/* Location + salary row */}
      <div className="flex items-center gap-4 mb-5">
        <div className="h-6 bg-slate-200/60 rounded-md w-24" />
        <div className="h-6 bg-slate-200/60 rounded-md w-32" />
      </div>

      {/* Description lines */}
      <div className="space-y-2.5 mb-5">
        <div className="h-3 bg-slate-200/50 rounded w-full" />
        <div className="h-3 bg-slate-200/50 rounded w-5/6" />
        <div className="h-3 bg-slate-200/50 rounded w-4/6" />
      </div>

      {/* CTA button placeholder */}
      <div className="h-9 bg-slate-200/80 rounded-xl w-32 mt-2" />
    </div>
  );
}