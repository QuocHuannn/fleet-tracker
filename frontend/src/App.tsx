/**
 * Main App Component
 * Root component with routing and providers setup
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';

// Components
import Header from './components/Layout/Header.tsx';
import LoginForm from './components/Auth/LoginForm.tsx';
import Dashboard from './components/Dashboard/Dashboard.tsx';
import VehicleList from './components/Vehicles/VehicleList.tsx';
import LiveMap from './components/Map/LiveMap.tsx';
import AlertManagement from './components/Alerts/AlertManagement.tsx';

// Contexts
import { AuthProvider, useAuth } from './contexts/AuthContext.tsx';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <div>Loading...</div>
      </Box>
    );
  }

  return (
    <Router>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        
        <Box component="main" sx={{ flexGrow: 1 }}>
          <Routes>
            <Route 
              path="/login" 
              element={
                !user ? (
                  <LoginForm />
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                user ? (
                  <Dashboard />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/vehicles" 
              element={
                user ? (
                  <Box sx={{ p: 3 }}>
                    <VehicleList />
                  </Box>
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/map" 
              element={
                user ? (
                  <Box sx={{ p: 3 }}>
                    <LiveMap />
                  </Box>
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/alerts" 
              element={
                user ? (
                  <Box sx={{ p: 3 }}>
                    <AlertManagement />
                  </Box>
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/" 
              element={
                user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
