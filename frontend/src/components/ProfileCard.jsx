

import { useState } from 'react';

const MAX_VISIBLE_SKILLS = 10;

export default function ProfileCard({ profile }) {
  const [showAllSkills, setShowAllSkills] = useState(false);

  if (!profile) return null;

  const { skills = [], experience_years = 0, job_titles = [], summary = '' } = profile;
  const visibleSkills = showAllSkills ? skills : skills.slice(0, MAX_VISIBLE_SKILLS);
  const hiddenCount = skills.length - MAX_VISIBLE_SKILLS;

  return (
    <div className="glass-panel rounded-2xl p-8 mb-8 relative overflow-hidden shadow-sm">
      {/* Background glow */}
      <div className="absolute top-[-50px] right-[-50px] w-[150px] h-[150px] bg-[#FF416C]/10 blur-[60px] rounded-full pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between mb-6 relative z-10">
        <h2 className="text-slate-800 font-bold text-xl font-['Outfit'] tracking-wide">Extracted Profile</h2>
        <div className="flex items-center gap-1.5 bg-[#FF416C]/10 border border-[#FF416C]/20
                        px-4 py-1.5 rounded-full shadow-sm">
          <span className="font-mono text-[#FF416C] text-sm font-extrabold">{experience_years}</span>
          <span className="text-[#FF416C]/80 text-xs font-semibold uppercase tracking-wider">yrs exp</span>
        </div>
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-slate-600 text-sm leading-relaxed mb-6 relative z-10 bg-slate-50/80 p-4 rounded-xl border border-slate-200">{summary}</p>
      )}

      {/* Job titles */}
      {job_titles.length > 0 && (
        <div className="mb-6 relative z-10">
          <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mb-3">
            Roles
          </p>
          <div className="flex flex-wrap gap-2.5">
            {job_titles.map((title) => (
              <span
                key={title}
                className="text-xs font-semibold px-3 py-1.5 bg-white border border-slate-200
                           text-slate-600 rounded-lg shadow-sm"
              >
                {title}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <div className="relative z-10">
          <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mb-3">
            Top Skills
          </p>
          <div className="flex flex-wrap gap-2.5">
            {visibleSkills.map((skill) => (
              <span
                key={skill}
                className="text-xs font-semibold px-3 py-1.5 bg-emerald-50 border border-emerald-200
                           text-emerald-600 rounded-lg font-mono shadow-sm"
              >
                {skill}
              </span>
            ))}
            {!showAllSkills && hiddenCount > 0 && (
              <button
                onClick={() => setShowAllSkills(true)}
                className="text-xs font-bold px-3 py-1.5 bg-slate-100 text-slate-500 border border-slate-200
                           rounded-lg hover:text-slate-800 hover:bg-slate-200 transition-all font-mono shadow-sm"
              >
                +{hiddenCount} more
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}