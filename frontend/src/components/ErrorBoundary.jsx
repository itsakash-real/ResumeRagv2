

import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    const isDev = import.meta.env.DEV;

    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-[#111118] border border-red-500/20 rounded-2xl p-8 text-center">
          <div className="w-14 h-14 bg-red-500/10 rounded-2xl flex items-center
                          justify-center mx-auto mb-5">
            <svg className="w-7 h-7 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <h2 className="text-white text-xl font-bold mb-2">Something went wrong</h2>
          <p className="text-gray-500 text-sm mb-6">
            An unexpected error occurred. The error has been logged.
          </p>

          {isDev && this.state.error && (
            <pre className="text-left text-xs text-red-300/70 bg-[#0a0a0f] border
                            border-red-500/10 rounded-lg p-4 mb-6 overflow-auto max-h-40 font-mono">
              {this.state.error.message}
            </pre>
          )}

          <button
            onClick={() => window.location.reload()}
            className="w-full bg-blue-500 hover:bg-blue-400 text-white font-semibold
                       text-sm px-4 py-2.5 rounded-lg transition-colors"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }
}