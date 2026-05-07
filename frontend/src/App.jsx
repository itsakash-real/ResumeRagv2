// src/App.jsx
// Route definitions — public routes and protected app routes.

import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Home from './pages/Home';

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Protected — AppLayout handles auth check internally */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/history" element={<History />} />

      {/* Default redirect to Home */}
      <Route path="/" element={<Home />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}