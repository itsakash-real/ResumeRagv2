

import { useEffect, useState, useRef } from 'react';

const STEPS = [
  'Parsing PDF...',
  'Extracting profile with Groq...',
  'Fetching job listings...',
  'Building vector index...',
  'Ranking matches...',
];

export default function ProgressBar({ resumeId, onComplete }) {
  const [percent, setPercent] = useState(0);
  const [step, setStep] = useState(STEPS[0]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!resumeId) return;

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsUrl = apiUrl.replace(/^http/, 'ws') + `/ws/progress/${resumeId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const { step: newStep, percent: newPercent } = JSON.parse(event.data);
        if (newStep) setStep(newStep);
        if (typeof newPercent === 'number') setPercent(newPercent);
        if (newPercent >= 100) {
          ws.close();
          onComplete?.();
        }
      } catch {
        // Malformed message — ignore
      }
    };

    ws.onerror = () => {
      // WebSocket unavailable — simulate progress so UX doesn't freeze
      simulateProgress(setPercent, setStep, onComplete);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, [resumeId, onComplete]);

  return (
    <div className="w-full mt-6">
      {/* Track */}
      <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden border border-slate-300">
        <div
          className="h-full bg-gradient-primary rounded-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(255,65,108,0.6)]"
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Labels */}
      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-slate-500 font-mono tracking-wide font-bold">{step}</span>
        <span className="text-xs text-transparent bg-clip-text bg-gradient-primary font-mono font-bold tracking-wider">{percent}%</span>
      </div>

      {!connected && (
        <p className="text-xs text-slate-400 mt-2 font-mono">Connecting to pipeline…</p>
      )}
    </div>
  );
}

// Fallback: animate progress client-side if WebSocket is unavailable
function simulateProgress(setPercent, setStep, onComplete) {
  const timeline = [
    { delay: 0, percent: 10, step: STEPS[0] },
    { delay: 800, percent: 30, step: STEPS[1] },
    { delay: 2500, percent: 55, step: STEPS[2] },
    { delay: 3800, percent: 75, step: STEPS[3] },
    { delay: 4500, percent: 90, step: STEPS[4] },
    { delay: 5500, percent: 100, step: 'Complete!' },
  ];

  timeline.forEach(({ delay, percent, step }) => {
    setTimeout(() => {
      setPercent(percent);
      setStep(step);
      if (percent >= 100) onComplete?.();
    }, delay);
  });
}