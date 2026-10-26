import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { User } from '../types';
import { authApi } from '../api/auth';
import { getOfflineFallback, subscribeOfflineFallback } from '../api/client';

export const Layout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isOffline, setIsOffline] = useState(getOfflineFallback());
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    return subscribeOfflineFallback(setIsOffline);
  }, []);

  const userJson = localStorage.getItem('aicte_user');
  let user: User;
  try {
    if (userJson && userJson !== 'undefined' && userJson !== 'null') {
      user = JSON.parse(userJson);
    } else {
      user = {
        id: '1',
        username: 'admin',
        email: 'admin@aicte.gov.in',
        full_name: 'AICTE Administrator',
        role: 'admin',
        created_at: new Date().toISOString(),
      };
    }
  } catch {
    user = {
      id: '1',
      username: 'admin',
      email: 'admin@aicte.gov.in',
      full_name: 'AICTE Administrator',
      role: 'admin',
      created_at: new Date().toISOString(),
    };
  }

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  const isCollege = user.role === 'college_user';
  const isOfficer = user.role === 'officer';
  const isAdmin = user.role === 'admin';

  const icons = {
    dashboard: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
    applications: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    reviewQueue: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
    alerts: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    graph: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    ),
    analytics: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    audit: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.04 1-4.225 1-6.48 0-4.08-1.28-7.86-3.467-10.976M6.48 5.48A14.004 14.004 0 004 11.65" />
      </svg>
    ),
    eval: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
      </svg>
    ),
    letters: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    users: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
  };

  let navItems: { label: string; path: string; icon: JSX.Element }[] = [];

  if (isCollege) {
    // 🏛️ College User: Only institutional self-service functions
    navItems = [
      {
        label: 'My Institution Dashboard',
        path: '/dashboard',
        icon: icons.dashboard,
      },
      {
        label: 'Apply for Approval / EoA',
        path: '/apply',
        icon: (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        ),
      },
      {
        label: 'My EoA Applications',
        path: '/applications',
        icon: icons.applications,
      },
      {
        label: 'Deficiency Notices & Hearing',
        path: '/letters',
        icon: icons.letters,
      },
    ];
  } else if (isOfficer) {
    // 👮 Regional Officer: Jurisdictional scrutiny, review, and letter issuance
    navItems = [
      {
        label: `RO ${user.region || 'Regional'} Dashboard`,
        path: '/dashboard',
        icon: icons.dashboard,
      },
      {
        label: `Regional Applications (${user.region || 'Jurisdiction'})`,
        path: '/applications',
        icon: icons.applications,
      },
      {
        label: 'Officer Review Queue',
        path: '/review-queue',
        icon: icons.reviewQueue,
      },
      {
        label: 'Forensic & Fraud Alerts',
        path: '/alerts',
        icon: icons.alerts,
      },
      {
        label: 'Collusion & Faculty Graph',
        path: '/graph',
        icon: icons.graph,
      },
      {
        label: 'Regional Analytics',
        path: '/analytics',
        icon: icons.analytics,
      },
      {
        label: 'Issue Deficiency Notices',
        path: '/letters',
        icon: icons.letters,
      },
    ];
  } else {
    // ⚙️ Admin: National Central Scrutiny + Audit Ledger + ML Evaluation
    navItems = [
      {
        label: 'National Scrutiny Hub',
        path: '/dashboard',
        icon: icons.dashboard,
      },
      {
        label: 'All National Applications',
        path: '/applications',
        icon: icons.applications,
      },
      {
        label: 'Officer Review Queue',
        path: '/review-queue',
        icon: icons.reviewQueue,
      },
      {
        label: 'Fraud & Forensic Alerts',
        path: '/alerts',
        icon: icons.alerts,
      },
      {
        label: 'Collusion Network Graph',
        path: '/graph',
        icon: icons.graph,
      },
      {
        label: 'National Analytics',
        path: '/analytics',
        icon: icons.analytics,
      },
      {
        label: 'Audit Ledger (Hash Chain)',
        path: '/audit',
        icon: icons.audit,
      },
      {
        label: 'ML Model Evaluation',
        path: '/evaluation',
        icon: icons.eval,
      },
      {
        label: 'Deficiency Notices',
        path: '/letters',
        icon: icons.letters,
      },
      {
        label: 'User & Officer Management',
        path: '/users',
        icon: icons.users,
      },
    ];
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'officer':
        return 'bg-blue-600 text-white';
      case 'scrutiny_admin':
        return 'bg-purple-600 text-white';
      case 'admin':
        return 'bg-rose-600 text-white';
      case 'college_user':
        return 'bg-emerald-600 text-white';
      default:
        return 'bg-slate-600 text-white';
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100 font-sans">
      {/* 1. Mandatory AICTE Advisory Banner across EVERY page */}
      <div className="bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 text-white px-4 py-2 text-center text-xs md:text-sm font-semibold tracking-wide shadow-sm flex items-center justify-center gap-2 z-50">
        <svg className="w-4 h-4 flex-shrink-0 animate-bounce" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
        <span>⚠️ Decision-support only. Final decisions rest with authorised AICTE officials.</span>
      </div>

      {/* 2. Persistent Offline Demo Data Banner (Displayed whenever backend is unreachable) */}
      {isOffline && (
        <div id="offline-demo-banner" className="bg-rose-600 text-white px-4 py-2.5 text-center text-xs md:text-sm font-bold tracking-wide shadow-md flex items-center justify-center gap-2 z-50">
          <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
          <span>OFFLINE DEMO DATA - backend unreachable</span>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarCollapsed ? 'w-20' : 'w-64'
          } bg-slate-900 text-slate-300 flex flex-col transition-all duration-200 border-r border-slate-800 flex-shrink-0`}
        >
          {/* Logo / Brand Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            {!sidebarCollapsed ? (
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-extrabold text-lg shadow-md">
                  A
                </div>
                <div>
                  <h1 className="text-sm font-extrabold text-white tracking-wider">AICTE-VERIFY</h1>
                  <p className="text-[10px] text-slate-400">Smart Document Scrutiny</p>
                </div>
              </div>
            ) : (
              <div className="mx-auto w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
                A
              </div>
            )}
            <button
              type="button"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800"
              title="Toggle sidebar"
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
          </div>

          {/* Nav items */}
          <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition ${
                    isActive
                      ? 'bg-aicte-600 text-white font-semibold shadow'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <span className="flex-shrink-0">{item.icon}</span>
                  {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                </Link>
              );
            })}
          </nav>

          {/* Sidebar Footer User info */}
          <div className="p-3 border-t border-slate-800 bg-slate-950/40">
            {!sidebarCollapsed ? (
              <div className="flex items-center justify-between">
                <div className="truncate pr-2">
                  <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
                  <span
                    className={`inline-block mt-0.5 text-[9px] uppercase font-bold px-1.5 py-0.2 rounded ${getRoleBadge(
                      user.role
                    )}`}
                  >
                    {user.role.replace('_', ' ')}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded text-xs"
                  title="Logout"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleLogout}
                className="w-full flex justify-center text-slate-400 hover:text-rose-400 p-2"
                title="Logout"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
              </button>
            )}
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Top Bar */}
          <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between flex-shrink-0 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Approval Process Handbook (APH) 2025-26
              </span>
              <span className="text-slate-300">|</span>
              <span className="text-xs text-slate-600 font-medium">
                Regional Portal: {user.institution_name || 'All India Council for Technical Education'}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                <span className="text-xs font-medium text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Integrity Active
                </span>
              </div>

              <div className="text-right">
                <span className="text-xs font-bold text-slate-800 block">{user.full_name}</span>
                <span className="text-[10px] text-slate-400 capitalize">{user.role.replace('_', ' ')}</span>
              </div>
            </div>
          </header>

          {/* Page Outlet */}
          <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
