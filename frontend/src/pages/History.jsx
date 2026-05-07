

import { useEffect, useState, useRef, useCallback } from 'react';
import AppLayout from '../layouts/AppLayout';
import JobCard from '../components/JobCard';
import SkeletonCard from '../components/SkeletonCard';
import { useMatches } from '../hooks/useMatches';

const SORT_OPTIONS = [
  { label: 'Best Match', value: 'score_desc' },
  { label: 'Worst Match', value: 'score_asc' },
  { label: 'Newest', value: 'date_desc' },
];

import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const LIMIT = 10;

export default function History() {
  const { token } = useAuthStore();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  const { results, total, page, loading, error, fetch, remove } = useMatches();
  const [search, setSearch] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [sort, setSort] = useState('score_desc');
  const [currentPage, setCurrentPage] = useState(1);
  const debounceRef = useRef(null);

  // Fetch whenever filters or page change
  const loadResults = useCallback((opts = {}) => {
    fetch({
      page: opts.page ?? currentPage,
      limit: LIMIT,
      min_score: opts.minScore ?? minScore,
      sort: opts.sort ?? sort,
    });
  }, [fetch, currentPage, minScore, sort]);

  useEffect(() => {
    loadResults({ page: 1 });
    setCurrentPage(1);
  }, [sort]); // eslint-disable-line

  useEffect(() => {
    loadResults({ page: currentPage });
  }, [currentPage]); // eslint-disable-line

  const handleMinScoreChange = (value) => {
    setMinScore(value);
    setCurrentPage(1);
    loadResults({ minScore: value, page: 1 });
  };

  // Client-side search filter (debounced 300ms)
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearch(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      // Search filters already-fetched results client-side
    }, 300);
  };

  const filteredResults = results.filter((r) =>
    search.trim() === '' || r.job_title.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <AppLayout>
      {/* Header */}
      <div className="mb-8 text-center sm:text-left">
        <h1 className="text-3xl font-extrabold text-slate-800 font-['Outfit'] tracking-tight">Match <span className="text-transparent bg-clip-text bg-gradient-primary">History</span></h1>
        <p className="text-slate-500 text-sm mt-2 font-medium">
          All job matches from your previous resume uploads.
        </p>
      </div>

      {/* Filters bar */}
      <div className="glass-panel-heavy border border-slate-200 rounded-2xl p-5 mb-8
                      flex flex-col sm:flex-row gap-5 items-center relative z-10 shadow-sm">
        {/* Search */}
        <div className="flex-1 w-full">
          <input
            type="text"
            value={search}
            onChange={handleSearchChange}
            placeholder="Search job titles…"
            className="w-full bg-white/80 border border-slate-300 rounded-xl px-4 py-3
                       text-slate-800 placeholder-slate-400 text-sm font-medium
                       focus:outline-none focus:border-[#FF416C] focus:ring-1 focus:ring-[#FF416C]/50
                       transition-all shadow-sm"
          />
        </div>

        {/* Min score slider */}
        <div className="flex items-center gap-3 min-w-[200px] w-full sm:w-auto bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 whitespace-nowrap font-bold uppercase tracking-widest">
            Min Score
          </span>
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={minScore}
            onChange={(e) => handleMinScoreChange(Number(e.target.value))}
            className="flex-1 accent-[#FF416C] cursor-pointer"
          />
          <span className="text-xs text-[#FF416C] font-mono w-8 text-right font-bold">{minScore}%</span>
        </div>

        {/* Sort dropdown */}
        <div className="w-full sm:w-auto">
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="w-full sm:w-auto bg-white/80 border border-slate-300 rounded-xl px-4 py-3
                       text-slate-800 text-sm font-medium focus:outline-none focus:border-[#FF416C] focus:ring-1 focus:ring-[#FF416C]/50
                       cursor-pointer transition-all shadow-sm"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-white text-slate-800">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-center shadow-sm">
          <p className="text-red-700 text-sm font-bold mb-1">Failed to load history</p>
          <p className="text-red-500 text-xs font-mono">{error}</p>
          <button
            onClick={() => loadResults()}
            className="mt-3 text-xs font-bold text-red-600 hover:text-red-700 border border-red-200
                       px-4 py-2 rounded-lg transition-all hover:bg-red-100 bg-white"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredResults.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-panel rounded-2xl shadow-sm">
          <div className="w-16 h-16 bg-slate-50 border border-slate-200 rounded-2xl
                          flex items-center justify-center mb-4 shadow-sm">
            <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-slate-800 font-bold text-lg">No matches yet</p>
          <p className="text-slate-500 text-sm mt-1 font-medium">
            Upload a resume to get started.
          </p>
        </div>
      )}

      {/* Results grid */}
      {!loading && !error && filteredResults.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs text-slate-500 font-mono font-bold">
              {total} total result{total !== 1 ? 's' : ''}
              {search && ` · filtered to ${filteredResults.length}`}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredResults.map((match) => (
              <div key={match.id} className="relative group">
                <JobCard
                  job={{
                    title: match.job_title,
                    company: match.company,
                    url: match.url,
                    score: match.score,
                    location: '',
                    description: '',
                    salary_min: null,
                    salary_max: null,
                  }}
                  compact
                />
                {/* Delete button — appears on hover */}
                <button
                  onClick={() => remove(match.id)}
                  className="absolute top-3 right-3 opacity-0 group-hover:opacity-100
                             transition-opacity text-slate-400 hover:text-red-500
                             bg-white border border-slate-200 p-1.5 rounded-lg shadow-sm hover:border-red-200 hover:bg-red-50 z-20"
                  title="Delete match"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-10">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-900
                           disabled:opacity-40 disabled:cursor-not-allowed transition-all
                           border border-slate-200 bg-white px-5 py-2.5 rounded-xl hover:border-slate-300 hover:bg-slate-50 shadow-sm"
              >
                ← Previous
              </button>

              <span className="text-sm text-slate-500 font-mono font-bold px-4 py-2 bg-slate-50 rounded-lg border border-slate-200 shadow-sm">
                Page <span className="text-slate-800">{currentPage}</span> of{' '}
                <span className="text-slate-800">{totalPages}</span>
              </span>

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-900
                           disabled:opacity-40 disabled:cursor-not-allowed transition-all
                           border border-slate-200 bg-white px-5 py-2.5 rounded-xl hover:border-slate-300 hover:bg-slate-50 shadow-sm"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </AppLayout>
  );
}