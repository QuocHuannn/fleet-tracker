import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { firebaseAuthService, User, LoginCredentials } from '../services/firebaseAuthService';

// Auth context để quản lý trạng thái xác thực người dùng với Firebase

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Actions
type AuthAction = 
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; user: User }
  | { type: 'AUTH_ERROR'; error: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'INITIALIZE'; user: User | null };

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true, error: null };
    case 'AUTH_SUCCESS':
      return { ...state, loading: false, user: action.user, error: null, initialized: true };
    case 'AUTH_ERROR':
      return { ...state, loading: false, error: action.error };
    case 'LOGOUT':
      return { ...state, user: null, loading: false, error: null };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'INITIALIZE':
      return { ...state, user: action.user, initialized: true, loading: false };
    default:
      return state;
  }
}

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    loading: false,
    error: null,
    initialized: false
  });

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const user = await firebaseAuthService.getCurrentUser();
        dispatch({ type: 'INITIALIZE', user });
      } catch (error) {
        console.error('Error initializing auth:', error);
        dispatch({ type: 'INITIALIZE', user: null });
      }
    };

    initializeAuth();

    // Listen for auth state changes
    const unsubscribe = firebaseAuthService.onAuthStateChanged((user) => {
      if (state.initialized) {
        if (user) {
          dispatch({ type: 'AUTH_SUCCESS', user });
        } else {
          dispatch({ type: 'LOGOUT' });
        }
      }
    });

    return unsubscribe;
  }, [state.initialized]);

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const user = await firebaseAuthService.login(credentials);
      dispatch({ type: 'AUTH_SUCCESS', user });
    } catch (error: any) {
      dispatch({ type: 'AUTH_ERROR', error: error.message });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await firebaseAuthService.logout();
      dispatch({ type: 'LOGOUT' });
    } catch (error: any) {
      dispatch({ type: 'AUTH_ERROR', error: error.message });
      throw error;
    }
  };

  const refreshToken = async () => {
    try {
      await firebaseAuthService.refreshToken();
    } catch (error: any) {
      dispatch({ type: 'AUTH_ERROR', error: error.message });
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  return (
    <AuthContext.Provider value={{
      ...state,
      login,
      logout,
      clearError,
      refreshToken,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}