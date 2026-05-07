

import { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from '../layouts/AuthLayout';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, fieldError } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;
    login(email.trim(), password);
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="w-full">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 tracking-tight">Sign in</h2>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-sm text-slate-600 font-bold mb-1.5">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            className="w-full bg-white/50 border border-slate-300 rounded-xl px-4 py-3
                       text-slate-800 placeholder-slate-400 text-sm font-medium
                       focus:outline-none focus:border-[#FF416C] focus:ring-1 focus:ring-[#FF416C]/50
                       transition-all shadow-sm"
          />
        </div>

        {/* Password */}
        <div className="mb-2">
          <label className="block text-sm text-slate-600 font-bold mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            className="w-full bg-white/50 border border-slate-300 rounded-xl px-4 py-3
                       text-slate-800 placeholder-slate-400 text-sm font-medium
                       focus:outline-none focus:border-[#FF416C] focus:ring-1 focus:ring-[#FF416C]/50
                       transition-all shadow-sm"
          />
        </div>

        {/* Field-level error */}
        {fieldError && (
          <p className="text-red-500 text-xs mt-2 mb-1 font-mono font-bold">{fieldError}</p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !email || !password}
          className={`mt-6 w-full flex items-center justify-center gap-2 px-4 py-3
                      rounded-xl text-sm font-bold transition-all select-none tracking-wide shadow-sm
                      ${loading || !email || !password
                        ? 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
                        : 'bg-gradient-primary hover:opacity-90 text-white neon-glow neon-glow-hover border border-transparent'
                      }`}
        >
          {loading ? (
            <>
              <Spinner />
              Signing in…
            </>
          ) : (
            'Sign in'
          )}
        </button>

        {/* Switch to signup */}
        <p className="text-center text-sm text-slate-500 font-medium mt-6">
          Don't have an account?{' '}
          <Link to="/signup" className="text-[#FF416C] font-bold hover:text-[#FF4B2B] transition-colors">
            Sign up
          </Link>
        </p>
      </form>
    </AuthLayout>
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