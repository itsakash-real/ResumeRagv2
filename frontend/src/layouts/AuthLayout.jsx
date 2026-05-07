

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 relative overflow-hidden font-sans">
      
      {/* Background Glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#FF416C]/20 blur-[120px] rounded-full pointer-events-none mix-blend-multiply animate-pulse"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#FF4B2B]/20 blur-[120px] rounded-full pointer-events-none mix-blend-multiply animate-pulse" style={{ animationDelay: '2s' }}></div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo / Brand */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-slate-800 tracking-tight font-['Outfit']">
            Resume<span className="text-transparent bg-clip-text bg-gradient-primary">RAG</span>
          </h1>
          <p className="text-slate-500 text-sm mt-3 font-medium">
            AI-powered job matching
          </p>
        </div>

        {/* Card */}
        <div className="glass-panel-heavy rounded-2xl p-8 shadow-sm">
          {children}
        </div>
      </div>
    </div>
  );
}