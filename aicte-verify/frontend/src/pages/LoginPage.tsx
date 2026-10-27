import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi } from '../api/auth';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      setError('Please provide a valid username or email.');
      return;
    }
    setError('');
    setIsLoading(true);

    let cleanUsername = username.trim();
    const compact = cleanUsername.toLowerCase().replace(/\s+/g, '').replace(/_/g, '');
    if (['clg1', 'clg2', 'clg3', 'clg4', 'clg5', 'clg6'].includes(compact)) {
      cleanUsername = compact.replace('clg', 'college');
    }

    try {
      await authApi.login({ username: cleanUsername, password });
      let target = (location.state as any)?.from?.pathname;
      if (!target || target === '/login') {
        target = '/dashboard';
      }
      navigate(target, { replace: true });
    } catch (err: any) {
      setError(err?.message || 'Login authentication failed. Check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const setDemoRole = (demoUsername: string, demoPassword: string) => {
    setUsername(demoUsername);
    setPassword(demoPassword);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Top Advisory Strip */}
      <div className="fixed top-0 inset-x-0 bg-amber-500 text-white text-xs font-semibold py-1.5 text-center shadow">
        ⚠️ AICTE-Verify Platform: Decision-support only. Final decisions rest with authorised AICTE officials.
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white text-3xl font-black mx-auto shadow-xl">
          A
        </div>
        <h2 className="mt-4 text-center text-2xl font-extrabold text-white tracking-tight">
          AICTE-Verify Portal
        </h2>
        <p className="mt-1 text-center text-xs text-slate-300">
          Smart Document Forensic Scrutiny & Regulatory Verification Gateway
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-200">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleLogin}>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Username or Official Email
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-aicte-500 focus:border-aicte-500 outline-none"
                placeholder="officer_kumar"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-aicte-500 focus:border-aicte-500 outline-none"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 rounded-lg bg-aicte-600 hover:bg-aicte-700 text-white font-bold text-sm shadow-md hover:shadow transition flex items-center justify-center gap-2"
            >
              {isLoading && (
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {isLoading ? 'Verifying Credentials...' : 'Sign In to Portal'}
            </button>
          </form>

          {/* Demo Roles Quick Pick */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 text-center">
              Quick Demo Personas (1-Click Fill)
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
              <button
                type="button"
                onClick={() => setDemoRole('admin', 'admin123')}
                className="p-2 border border-rose-200 bg-rose-50 hover:bg-rose-100 rounded text-rose-900 font-semibold text-left transition"
              >
                ⚙️ Central Admin
                <span className="block text-[10px] text-rose-600 font-normal">admin / admin123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('officer1', 'officer123')}
                className="p-2 border border-blue-200 bg-blue-50 hover:bg-blue-100 rounded text-blue-900 font-semibold text-left transition"
              >
                👮 RO South
                <span className="block text-[10px] text-blue-600 font-normal">officer1 / officer123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('officer2', 'officer123')}
                className="p-2 border border-purple-200 bg-purple-50 hover:bg-purple-100 rounded text-purple-900 font-semibold text-left transition"
              >
                👮 RO North
                <span className="block text-[10px] text-purple-600 font-normal">officer2 / officer123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('officer3', 'officer123')}
                className="p-2 border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 rounded text-indigo-900 font-semibold text-left transition"
              >
                👮 RO West (Zenith)
                <span className="block text-[10px] text-indigo-600 font-normal">officer3 / officer123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('college1', 'college123')}
                className="p-2 border border-emerald-200 bg-emerald-50 hover:bg-emerald-100 rounded text-emerald-900 font-semibold text-left transition"
              >
                🏛️ College 1 (Apex)
                <span className="block text-[10px] text-emerald-600 font-normal">college1 / college123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('college2', 'college123')}
                className="p-2 border border-teal-200 bg-teal-50 hover:bg-teal-100 rounded text-teal-900 font-semibold text-left transition"
              >
                🏛️ College 2 (Zenith)
                <span className="block text-[10px] text-teal-600 font-normal">college2 / college123</span>
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('college3', 'college123')}
                className="p-2 border border-amber-200 bg-amber-50 hover:bg-amber-100 rounded text-amber-900 font-semibold text-left transition"
              >
                🏛️ College 3 (Northern)
                <span className="block text-[10px] text-amber-600 font-normal">college3 / college123</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
