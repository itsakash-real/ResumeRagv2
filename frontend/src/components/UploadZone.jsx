

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

const MAX_SIZE = 5 * 1024 * 1024; // 5 MB

export default function UploadZone({ onUpload, loading }) {
  const [file, setFile] = useState(null);

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length > 0) {
      const reason = rejected[0]?.errors?.[0]?.code;
      if (reason === 'file-too-large') {
        toast.error('File exceeds 5MB limit.');
      } else {
        toast.error('Only PDF files accepted.');
      }
      return;
    }
    if (accepted.length > 0) {
      setFile(accepted[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: MAX_SIZE,
    multiple: false,
    disabled: loading,
  });

  const handleUpload = () => {
    if (file && !loading) onUpload(file);
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    setFile(null);
  };

  const formatSize = (bytes) =>
    bytes < 1024 * 1024
      ? `${(bytes / 1024).toFixed(1)} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

  return (
    <div className="w-full">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`relative w-full rounded-2xl border-2 border-dashed p-10
                    flex flex-col items-center justify-center gap-4 cursor-pointer
                    transition-all duration-300 select-none glass-panel-heavy shadow-sm
                    ${isDragActive
                      ? 'border-[#FF416C] bg-[#FF416C]/5 shadow-[0_0_40px_rgba(255,65,108,0.2)] animate-pulse'
                      : file
                      ? 'border-slate-300 bg-slate-50/80 hover:bg-white'
                      : 'border-slate-300 bg-white/50 hover:border-slate-400 hover:bg-white/80'
                    }
                    ${loading ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`}
      >
        <input {...getInputProps()} />

        {file ? (
          /* File selected state */
          <div className="text-center animate-in zoom-in-95 duration-200">
            <div className="w-16 h-16 bg-gradient-to-br from-[#FF416C]/10 to-[#FF4B2B]/10 border border-[#FF416C]/20
                            rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
              <svg className="w-8 h-8 text-[#FF416C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-slate-800 font-bold text-base truncate max-w-[240px] tracking-wide">{file.name}</p>
            <p className="text-slate-500 text-xs font-mono mt-1 font-semibold tracking-wider">{formatSize(file.size)}</p>
            {!loading && (
              <button
                onClick={handleRemove}
                className="text-xs text-slate-500 hover:text-red-500 transition-colors mt-3 font-semibold uppercase tracking-wider
                           bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-red-300 hover:bg-red-50"
              >
                Remove
              </button>
            )}
          </div>
        ) : isDragActive ? (
          /* Drag active state */
          <div className="text-center">
            <div className="w-16 h-16 bg-[#FF416C]/10 rounded-2xl flex items-center
                            justify-center mx-auto mb-4 animate-bounce border border-[#FF416C]/20">
              <svg className="w-8 h-8 text-[#FF416C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-[#FF416C] font-bold text-base">Drop it like it's hot</p>
          </div>
        ) : (
          /* Idle state */
          <div className="text-center">
            <div className="w-16 h-16 bg-slate-50 border border-slate-200 rounded-2xl flex items-center
                            justify-center mx-auto mb-5 shadow-sm">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-slate-700 font-bold text-base tracking-wide">
              Drop your resume here
            </p>
            <p className="text-slate-500 text-xs mt-2 font-mono uppercase tracking-wider font-semibold">
              PDF only · max 5 MB
            </p>
            <div className="mt-5 px-5 py-2.5 bg-slate-100 border border-slate-200 rounded-xl inline-block hover:bg-slate-200/80 transition-colors shadow-sm">
              <span className="text-sm text-slate-600 font-bold">Browse files</span>
            </div>
          </div>
        )}
      </div>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`mt-6 w-full flex items-center justify-center gap-3 px-4 py-4
                    rounded-xl text-base font-bold transition-all tracking-wide shadow-sm
                    ${!file || loading
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
                      : 'bg-gradient-primary hover:opacity-90 text-white neon-glow neon-glow-hover border border-transparent'
                    }`}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Processing…
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Analyze & Match
          </>
        )}
      </button>
    </div>
  );
}