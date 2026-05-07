

import { Link, useNavigate } from 'react-router-dom';
import UploadZone from '../components/UploadZone';
import useAuthStore from '../store/authStore';

export default function Home() {
  const navigate = useNavigate();
  const { token } = useAuthStore();

  const handleUpload = (file) => {
    if (!token) {
      navigate('/signup');
    } else {
      navigate('/dashboard', { state: { file } });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-x-hidden font-sans">
      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#FF416C]/20 blur-[120px] rounded-full pointer-events-none mix-blend-multiply animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-[#FF4B2B]/20 blur-[120px] rounded-full pointer-events-none mix-blend-multiply animate-pulse" style={{ animationDelay: '2s' }}></div>

      {/* Navbar */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-extrabold text-slate-800 tracking-tight font-['Outfit']">
            Resume<span className="text-transparent bg-clip-text bg-gradient-primary">RAG</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-slate-600 font-bold hover:text-slate-900 transition-colors px-4 py-2 hidden sm:block">
            Sign In
          </Link>
          <Link to="/signup" className="bg-gradient-primary text-white font-bold px-6 py-2.5 rounded-xl shadow-sm hover:opacity-90 transition-all neon-glow neon-glow-hover">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center text-center px-4 pt-24 pb-20 max-w-5xl mx-auto">
        <div className="inline-block mb-8 px-5 py-2 rounded-full border border-slate-200 bg-white/60 backdrop-blur-md shadow-sm">
          <span className="text-sm font-bold text-slate-600 flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FF416C] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#FF416C]"></span>
            </span>
            The future of AI-powered job matching
          </span>
        </div>
        
        <h1 className="text-5xl sm:text-7xl font-extrabold text-slate-800 tracking-tight font-['Outfit'] leading-tight mb-8">
          Land your dream job with <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-primary">intelligent matching.</span>
        </h1>
        
        <p className="text-lg sm:text-xl text-slate-500 font-medium max-w-2xl mx-auto mb-12 leading-relaxed">
          Upload your resume and let our advanced AI instantly analyze your skills, extract your profile, and match you with the best open roles across the web.
        </p>
        
        <div className="w-full max-w-xl mx-auto">
          <UploadZone onUpload={handleUpload} loading={false} />
        </div>
      </main>

      {/* Features Grid */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-12 mb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<svg className="w-6 h-6 text-[#FF416C]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            title="Instant Analysis"
            description="Our AI parses your PDF resume in seconds, extracting your core skills, experience, and career trajectory."
          />
          <FeatureCard 
            icon={<svg className="w-6 h-6 text-[#FF4B2B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
            title="Smart Matching"
            description="We build a semantic vector index of your profile to find jobs that truly fit, not just basic keyword matches."
          />
          <FeatureCard 
            icon={<svg className="w-6 h-6 text-[#FF416C]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
            title="Real-time Ranking"
            description="Get a precise compatibility score for every job, so you know exactly where to focus your applications."
          />
        </div>
      </section>
      
      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-200 bg-white/50 backdrop-blur-md py-8 text-center mt-auto">
        <p className="text-slate-500 font-medium text-sm">
          &copy; {new Date().getFullYear()} ResumeRAG. Built with advanced semantic search.
        </p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="glass-panel-heavy p-8 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-all hover:-translate-y-1">
      <div className="w-14 h-14 bg-gradient-to-br from-[#FF416C]/10 to-[#FF4B2B]/10 border border-[#FF416C]/20 rounded-2xl flex items-center justify-center mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-slate-800 mb-3 tracking-tight">{title}</h3>
      <p className="text-slate-500 font-medium leading-relaxed">
        {description}
      </p>
    </div>
  );
}
