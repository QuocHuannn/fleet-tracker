// Firebase Authentication Service
// Handles Firebase integration with Fleet Tracker backend

import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, signOut, onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';

interface LoginCredentials {
  email: string;
  password: string;
}

interface User {
  id: string;
  email: string;
  display_name?: string;
  role: string;
  firebase_uid: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
  email: string;
  role: string;
  display_name?: string;
  expires_at: string;
}

class FirebaseAuthService {
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  private auth;
  private currentUser: User | null = null;
  private accessToken: string | null = null;
  private authStateListeners: ((user: User | null) => void)[] = [];

  constructor() {
    // Initialize Firebase (configuration would be loaded from environment)
    const firebaseConfig = {
      apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
      authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
      storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.REACT_APP_FIREBASE_APP_ID
    };

    // Initialize Firebase if configuration is available
    if (firebaseConfig.apiKey) {
      const app = initializeApp(firebaseConfig);
      this.auth = getAuth(app);
      
      // Listen for auth state changes
      onAuthStateChanged(this.auth, this.handleAuthStateChange.bind(this));
    } else {
      console.warn('Firebase configuration not found. Using development mode.');
    }

    // Load stored token
    this.accessToken = localStorage.getItem('access_token');
    this.loadStoredUser();
  }

  private async handleAuthStateChange(firebaseUser: FirebaseUser | null) {
    if (firebaseUser) {
      try {
        // Get Firebase ID token
        const idToken = await firebaseUser.getIdToken();
        
        // Login to our backend with Firebase token
        await this.loginWithFirebaseToken(idToken);
      } catch (error) {
        console.error('Error handling auth state change:', error);
      }
    } else {
      // User signed out
      this.clearStoredAuth();
    }
  }

  async login(credentials: LoginCredentials): Promise<User> {
    if (this.auth) {
      // Firebase authentication
      try {
        const userCredential = await signInWithEmailAndPassword(
          this.auth,
          credentials.email,
          credentials.password
        );
        
        const idToken = await userCredential.user.getIdToken();
        return await this.loginWithFirebaseToken(idToken);
      } catch (error: any) {
        console.error('Firebase login error:', error);
        throw new Error(error.message || 'Login failed');
      }
    } else {
      // Development mode - direct backend call
      return await this.loginDevelopmentMode(credentials);
    }
  }

  private async loginWithFirebaseToken(firebaseToken: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          firebase_token: firebaseToken,
          device_info: {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            timestamp: new Date().toISOString()
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Login failed');
      }

      const loginData: LoginResponse = await response.json();
      
      // Store tokens
      localStorage.setItem('access_token', loginData.access_token);
      localStorage.setItem('refresh_token', loginData.refresh_token);
      
      // Create user object
      const user: User = {
        id: loginData.user_id,
        email: loginData.email,
        display_name: loginData.display_name,
        role: loginData.role,
        firebase_uid: loginData.user_id 
      };
      
      this.currentUser = user;
      this.accessToken = loginData.access_token;
      
      // Store user data
      localStorage.setItem('current_user', JSON.stringify(user));
      
      // Notify listeners
      this.notifyAuthStateListeners(user);
      
      return user;
    } catch (error: any) {
      console.error('Backend login error:', error);
      throw new Error(error.message || 'Login failed');
    }
  }

  private async loginDevelopmentMode(credentials: LoginCredentials): Promise<User> {
    // Development mode - simulate login
    const user: User = {
      id: 'dev_user_001',
      email: credentials.email,
      display_name: 'Development User',
      role: 'admin',
      firebase_uid: 'dev_firebase_uid'
    };
    
    this.currentUser = user;
    this.accessToken = 'dev_access_token_' + Date.now();
    
    localStorage.setItem('current_user', JSON.stringify(user));
    localStorage.setItem('access_token', this.accessToken);
    
    // Notify listeners
    this.notifyAuthStateListeners(user);
    
    return user;
  }

  async logout(): Promise<void> {
    if (this.auth) {
      await signOut(this.auth);
    }
    this.clearStoredAuth();
    this.notifyAuthStateListeners(null);
  }

  private clearStoredAuth() {
    this.currentUser = null;
    this.accessToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
  }

  private loadStoredUser() {
    const storedUser = localStorage.getItem('current_user');
    if (storedUser) {
      try {
        this.currentUser = JSON.parse(storedUser);
      } catch (error) {
        console.error('Error loading stored user:', error);
      }
    }
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.currentUser) {
      return this.currentUser;
    }
    
    // Try to load from storage
    this.loadStoredUser();
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    return !!(this.accessToken && this.currentUser);
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  async refreshToken(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const loginData: LoginResponse = await response.json();
      
      localStorage.setItem('access_token', loginData.access_token);
      this.accessToken = loginData.access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout user
      await this.logout();
      throw error;
    }
  }

  // Auth state listener methods
  onAuthStateChanged(listener: (user: User | null) => void) {
    this.authStateListeners.push(listener);
    
    // Call immediately with current user
    listener(this.currentUser);
    
    // Return unsubscribe function
    return () => {
      const index = this.authStateListeners.indexOf(listener);
      if (index > -1) {
        this.authStateListeners.splice(index, 1);
      }
    };
  }

  private notifyAuthStateListeners(user: User | null) {
    this.authStateListeners.forEach(listener => {
      try {
        listener(user);
      } catch (error) {
        console.error('Error in auth state listener:', error);
      }
    });
  }

  // HTTP client with automatic token handling
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getAccessToken();
    
    if (!token) {
      throw new Error('No authentication token available');
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    // Handle token expiry
    if (response.status === 401) {
      try {
        await this.refreshToken();
        
        // Retry with new token
        const newToken = this.getAccessToken();
        const retryResponse = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${newToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        return retryResponse;
      } catch (refreshError) {
        // Refresh failed, logout user
        await this.logout();
        throw new Error('Session expired. Please login again.');
      }
    }

    return response;
  }
}

export const firebaseAuthService = new FirebaseAuthService();
export type { User, LoginCredentials };
