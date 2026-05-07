

import { useState, useCallback } from 'react';
import AppLayout from '../layouts/AppLayout';
import UploadZone from '../components/UploadZone';
import ProgressBar from '../components/ProgressBar';
import ProfileCard from '../components/ProfileCard';
import JobCard from '../components/JobCard';
import SkeletonCard from '../components/SkeletonCard';
import { useResume } from '../hooks/useResume';
import { useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { useEffect, useRef } from 'react';

// State machine states
const STATE = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  MATCHING: 'matching',
  COMPLETE: 'complete',
};

export default function Dashboard() {
  const [stage, setStage] = useState(STATE.IDLE);
  const { upload, match, reset, uploading, matching, resumeId, profile, matches, error } = useResume();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuthStore();
  const hasUploadedRef = useRef(false);

  const handleUpload = useCallback(async (file) => {
    if (!token) {
      navigate('/signup');
      return;
    }

    setStage(STATE.UPLOADING);
    try {
      const id = await upload(file);
      setStage(STATE.MATCHING);
      await match(id);
      setStage(STATE.COMPLETE);
    } catch {
      setStage(STATE.IDLE);
    }
  }, [upload, match, token, navigate]);

  useEffect(() => {
    if (location.state?.file && !hasUploadedRef.current) {
      hasUploadedRef.current = true;
      handleUpload(location.state.file);
      // Clear the state so it doesn't upload again on refresh
      navigate('/dashboard', { replace: true, state: {} });
    }
  }, [location.state, handleUpload, navigate]);

  const handleReset = () => {
    reset();
    setStage(STATE.IDLE);
  };

  const handleProgressComplete = useCallback(() => {
    // Progress bar completed — matching result will arrive via the match() promise
  }, []);

  return (
    <AppLayout>
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold text-slate-800 tracking-tight font-['Outfit']">
          AI Job <span className="text-transparent bg-clip-text bg-gradient-primary">Matcher</span>
        </h1>
        <p className="text-slate-500 text-sm mt-3 font-medium">
          Upload your resume to find semantically matched job listings instantly.
        </p>
      </div>

      {/* ── IDLE ────────────────────────────────────────────────────────────── */}
      {stage === STATE.IDLE && (
        <div className="max-w-xl mx-auto">
          <UploadZone onUpload={handleUpload} loading={false} />
        </div>
      )}

      {/* ── UPLOADING ───────────────────────────────────────────────────────── */}
      {stage === STATE.UPLOADING && (
        <div className="max-w-xl mx-auto">
          <UploadZone onUpload={handleUpload} loading={true} />
          <div className="mt-4">
            <ProgressBar resumeId={null} onComplete={handleProgressComplete} />
          </div>
        </div>
      )}

      {/* ── MATCHING ────────────────────────────────────────────────────────── */}
      {stage === STATE.MATCHING && (
        <div className="max-w-xl mx-auto">
          <div className="glass-panel rounded-2xl p-8 mb-6">
            <p className="text-sm text-blue-400 font-bold mb-3 tracking-wide uppercase flex items-center gap-2">
               <Spinner /> Running AI pipeline…
            </p>
            <ProgressBar resumeId={resumeId} onComplete={handleProgressComplete} />
          </div>

          {/* Skeletons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            {[1, 2, 3].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      )}

      {/* ── ERROR (inline, any stage) ─────────────────────────────────────── */}
      {error && stage === STATE.IDLE && (
        <div className="max-w-xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-5 mb-8
                          flex items-start gap-4 backdrop-blur-sm shadow-sm">
            <svg className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-red-700 text-sm font-bold">Pipeline failed</p>
              <p className="text-red-600 text-xs mt-1 font-mono bg-red-100/50 p-2 rounded-lg mt-2 border border-red-200/50">{error}</p>
            </div>
            <button
              onClick={handleReset}
              className="text-xs font-bold text-red-600 hover:text-red-700 transition-all
                         border border-red-200 hover:border-red-300 hover:bg-red-100 px-4 py-2 rounded-xl bg-white/50"
            >
              Retry
            </button>
          </div>
          <UploadZone onUpload={handleUpload} loading={false} />
        </div>
      )}

      {/* ── COMPLETE ────────────────────────────────────────────────────────── */}
      {stage === STATE.COMPLETE && profile && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Profile + reset button */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-800 font-['Outfit']">
              <span className="text-transparent bg-clip-text bg-gradient-primary">{matches.length}</span> matches found
            </h2>
            <button
              onClick={handleReset}
              className="text-sm font-bold text-slate-600 hover:text-slate-900 transition-all
                         border border-slate-200 hover:border-slate-300 hover:bg-slate-50 hover:shadow-sm px-4 py-2 rounded-xl flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
              Upload New
            </button>
          </div>

          <ProfileCard profile={profile} />

          {/* Job grid */}
          {matches.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-gray-500 text-sm">No job matches returned — try a different resume.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {matches.map((job, idx) => (
                <JobCard key={`${job.url}-${idx}`} job={job} />
              ))}
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}