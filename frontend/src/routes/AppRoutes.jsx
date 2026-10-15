
import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MainLayout from '../components/layout/MainLayout';
import Dashboard from '../pages/Dashboard';
import CustomerFeedback from '../pages/CustomerFeedback';
import Insights from '../pages/Insights';
import Planning from '../pages/Planning';
import Requirements from '../pages/Requirements';
import Assistant from '../pages/Assistant';
import Login from '../pages/Login';
import Register from '../pages/Register';
import NotFound from '../pages/NotFound';
import { ContentSkeleton } from '../components/common/LoadingState';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-canvas flex flex-col items-center justify-center p-6 space-y-4 max-w-xl mx-auto">
        <div className="w-8 h-8 rounded-full border-2 border-emerald-600 border-t-transparent animate-spin mb-2" />
        <p className="text-xs text-slate-500 font-medium">
          Verifying workspace session...
        </p>
        <div className="w-full">
          <ContentSkeleton lines={3} />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <Login />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/register"
        element={
          <PublicOnlyRoute>
            <Register />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="feedback" element={<CustomerFeedback />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="insights" element={<Insights />} />
        <Route path="planning" element={<Planning />} />
        <Route path="requirements" element={<Requirements />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
