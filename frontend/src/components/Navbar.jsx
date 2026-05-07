

import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="border-b border-white/50 bg-white/70 backdrop-blur-md sticky top-0 z-50 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Brand */}
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="text-2xl font-extrabold text-slate-800 tracking-tight font-['Outfit']">
              Resume<span className="text-transparent bg-clip-text bg-gradient-primary">RAG</span>
            </Link>
            <div className="hidden sm:flex items-center gap-8">
              <Link
                to="/dashboard"
                className="text-sm font-bold text-slate-500 hover:text-slate-900 transition-all"
              >
                Dashboard
              </Link>
              {user?.email && (
                <Link
                  to="/history"
                  className="text-sm font-bold text-slate-500 hover:text-slate-900 transition-all"
                >
                  History
                </Link>
              )}
            </div>
          </div>

          {/* User controls */}
          <div className="flex items-center gap-6">
            {user?.email ? (
              <>
                <span className="hidden sm:block text-xs text-slate-600 font-mono bg-white/80 border border-slate-200 px-3 py-1.5 rounded-full truncate max-w-[200px] shadow-sm">
                  {user.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm font-bold text-slate-600 hover:text-slate-900 transition-all px-4 py-2 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50/50 hover:shadow-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm font-bold text-slate-600 hover:text-slate-900 transition-colors hidden sm:block">
                  Sign In
                </Link>
                <Link to="/signup" className="bg-gradient-primary text-white text-sm font-bold px-5 py-2 rounded-xl shadow-sm hover:opacity-90 transition-all neon-glow neon-glow-hover">
                  Get Started
                </Link>
              </>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}