import React, { Component, ErrorInfo, ReactNode } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

// Sanitize corrupt legacy localStorage data immediately
try {
  const token = localStorage.getItem('aicte_token');
  const user = localStorage.getItem('aicte_user');
  if (token === 'undefined' || token === 'null' || !token) {
    localStorage.removeItem('aicte_token');
  }
  if (user === 'undefined' || user === 'null' || !user) {
    localStorage.removeItem('aicte_user');
  } else {
    JSON.parse(user);
  }
} catch {
  localStorage.removeItem('aicte_token');
  localStorage.removeItem('aicte_user');
}

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught React Error:', error, errorInfo);
  }

  private handleReturnToDashboard = () => {
    this.setState({ hasError: false });
    window.location.href = '/dashboard';
  };

  private handleReset = () => {
    localStorage.removeItem('aicte_token');
    localStorage.removeItem('aicte_user');
    sessionStorage.clear();
    window.location.href = '/login';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-2xl text-center">
            <div className="text-4xl mb-3">⚠️</div>
            <h2 className="text-lg font-bold text-white mb-2">Interface Notice</h2>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              {this.state.error?.message || 'A display component encountered an unexpected error.'}
            </p>
            <div className="flex flex-col gap-2">
              <button
                onClick={this.handleReturnToDashboard}
                className="w-full py-2.5 px-4 bg-aicte-600 hover:bg-aicte-700 text-white text-xs font-bold rounded-lg shadow transition"
              >
                Return to Dashboard
              </button>
              <button
                onClick={this.handleReset}
                className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Sign In Again
              </button>
            </div>
          </div>
        </div>
      );
    }


    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);
