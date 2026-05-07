

import ScoreBadge from './ScoreBadge';

export default function JobCard({ job, compact = false }) {
  const {
    title,
    company,
    location,
    url,
    description,
    salary_min,
    salary_max,
    score,
  } = job;

  const salaryLabel =
    salary_min && salary_max
      ? `$${(salary_min / 1000).toFixed(0)}k – $${(salary_max / 1000).toFixed(0)}k`
      : salary_min
      ? `From $${(salary_min / 1000).toFixed(0)}k`
      : null;

  return (
    <div
      className="group glass-panel rounded-2xl p-6 relative overflow-hidden
                 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(255,65,108,0.15)]
                 hover:border-[#FF416C]/30 transition-all duration-300"
    >
      {/* Background glow on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#FF416C]/0 to-[#FF4B2B]/0 group-hover:from-[#FF416C]/5 group-hover:to-[#FF4B2B]/5 transition-colors duration-300 pointer-events-none" />

      {/* Header row */}
      <div className="flex items-start justify-between gap-4 mb-4 relative z-10">
        <div className="flex-1 min-w-0">
          <h3 className="text-slate-800 font-bold text-lg truncate leading-snug font-['Outfit'] tracking-wide group-hover:text-[#FF416C] transition-colors">
            {title}
          </h3>
          <p className="text-slate-500 font-medium text-sm mt-1 truncate">{company}</p>
        </div>
        <div className="flex-shrink-0">
          <ScoreBadge score={score} />
        </div>
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-4 mb-4 flex-wrap relative z-10">
        {location && (
          <span className="flex items-center gap-1.5 text-xs text-slate-600 font-medium bg-slate-100/80 px-2 py-1 rounded-md border border-slate-200">
            <svg className="w-3.5 h-3.5 text-[#FF4B2B]/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {location}
          </span>
        )}
        {salaryLabel && (
          <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-mono font-semibold bg-emerald-50 px-2 py-1 rounded-md border border-emerald-200">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {salaryLabel}
          </span>
        )}
      </div>

      {/* Description — hidden in compact mode */}
      {!compact && description && (
        <p className="text-slate-500 text-sm leading-relaxed line-clamp-3 mb-5 relative z-10">
          {description}
        </p>
      )}

      {/* CTA */}
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider
                     text-white hover:text-white transition-all
                     bg-gradient-primary neon-glow-hover
                     px-4 py-2 rounded-xl relative z-10 shadow-lg shadow-[#FF416C]/20"
        >
          View Job
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}
    </div>
  );
}