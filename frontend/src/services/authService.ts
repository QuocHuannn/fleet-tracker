import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

class AuthService {
  /**
   * Đăng nhập người dùng
   */
  async login(credentials: LoginCredentials): Promise<User> {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, credentials);
      
      // Lưu token vào localStorage
      localStorage.setItem('token', response.data.access_token);
      
      // Lấy thông tin người dùng
      return this.getCurrentUser();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Lấy thông tin người dùng hiện tại
   */
  async getCurrentUser(): Promise<User> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<TokenResponse> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Cập nhật token trong localStorage
      localStorage.setItem('token', response.data.access_token);
      
      return response.data;
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  }

  /**
   * Đăng xuất người dùng
   */
  logout(): void {
    localStorage.removeItem('token');
  }

  /**
   * Kiểm tra người dùng đã đăng nhập chưa
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

export default new AuthService();
