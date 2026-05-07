// src/main.jsx
// React app entry point — wraps everything in ErrorBoundary and Toaster.

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <App />
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#111118',
              color: '#e5e7eb',
              border: '1px solid #1f2937',
              fontFamily: 'monospace',
              fontSize: '13px',
            },
            success: { iconTheme: { primary: '#4ade80', secondary: '#111118' } },
            error: { iconTheme: { primary: '#f87171', secondary: '#111118' } },
          }}
        />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);