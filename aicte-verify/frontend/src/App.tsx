import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ApplicationsListPage from './pages/ApplicationsListPage';
import ApplicationDetailPage from './pages/ApplicationDetailPage';
import ReviewQueuePage from './pages/ReviewQueuePage';
import AlertsPage from './pages/AlertsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AuditLogPage from './pages/AuditLogPage';
import GraphPage from './pages/GraphPage';
import EvaluationPage from './pages/EvaluationPage';
import LettersPage from './pages/LettersPage';
import UsersPage from './pages/UsersPage';
import NewApplicationPage from './pages/NewApplicationPage';

export const App: React.FC = () => {
  return (
    <Routes>
      {/* Public Login Route */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected Layout Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="applications" element={<ApplicationsListPage />} />
        <Route path="applications/:id" element={<ApplicationDetailPage />} />
        <Route
          path="apply"
          element={
            <ProtectedRoute allowedRoles={['college_user']}>
              <NewApplicationPage />
            </ProtectedRoute>
          }
        />
        <Route path="review-queue" element={<ReviewQueuePage />} />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="graph" element={<GraphPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="audit" element={<AuditLogPage />} />
        <Route path="evaluation" element={<EvaluationPage />} />
        <Route path="letters" element={<LettersPage />} />
        <Route
          path="users"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UsersPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
