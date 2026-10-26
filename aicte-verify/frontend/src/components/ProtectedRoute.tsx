import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { UserRole, User } from '../types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const location = useLocation();
  const token = localStorage.getItem('aicte_token');
  const userJson = localStorage.getItem('aicte_user');

  let user: User | null = null;
  if (token && token !== 'undefined' && token !== 'null' && userJson && userJson !== 'undefined' && userJson !== 'null') {
    try {
      user = JSON.parse(userJson);
    } catch {
      user = null;
    }
  }

  if (!token || token === 'undefined' || !user) {
    localStorage.removeItem('aicte_token');
    localStorage.removeItem('aicte_user');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="max-w-md bg-white border border-rose-200 rounded-2xl p-8 shadow-xl text-center">
          <div className="w-16 h-16 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
            ⛔
          </div>
          <h2 className="text-xl font-bold text-slate-800">Restricted Access</h2>
          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            Your current role (<strong className="font-semibold text-slate-800">{user.role}</strong>) does
            not possess authorization to view this administrative resource.
          </p>
          <a
            href="/dashboard"
            className="inline-block mt-6 px-5 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white text-xs font-semibold rounded-lg shadow-sm"
          >
            Return to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
