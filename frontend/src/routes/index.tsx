import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import Navbar from '../components/Navbar';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import VocabularyPage from '../pages/VocabularyPage';
import GrammarPage from '../pages/GrammarPage';
import TestPage from '../pages/TestPage';
import TestHistoryPage from '../pages/TestHistoryPage';
import ProfilePage from '../pages/ProfilePage';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected routes */}
      <Route
        path="/vocabulary"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <VocabularyPage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/grammar"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <GrammarPage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tests"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <TestPage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tests/history"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <TestHistoryPage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <ProfilePage />
            </div>
          </ProtectedRoute>
        }
      />

      {/* Redirects */}
      <Route path="/" element={<Navigate to="/vocabulary" replace />} />
      <Route path="*" element={<Navigate to="/vocabulary" replace />} />
    </Routes>
  );
}