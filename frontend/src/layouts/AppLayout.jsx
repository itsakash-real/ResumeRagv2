

import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Navbar from '../components/Navbar';

export default function AppLayout({ children }) {
  const { token } = useAuthStore();

  // AppLayout is now public. Individual pages can enforce auth if needed.
  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden font-sans">
      {/* Vibrant background glowing shapes */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#FF416C]/20 blur-[120px] rounded-full pointer-events-none mix-blend-multiply animate-pulse"></div>
      <div className="absolute top-[20%] right-[-10%] w-[40%] h-[60%] bg-[#FF4B2B]/20 blur-[140px] rounded-full pointer-events-none mix-blend-multiply animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute bottom-[-20%] left-[20%] w-[60%] h-[50%] bg-[#FEB47B]/20 blur-[130px] rounded-full pointer-events-none mix-blend-multiply animate-pulse" style={{ animationDelay: '4s' }}></div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
          {children}
        </main>
      </div>
    </div>
  );
}