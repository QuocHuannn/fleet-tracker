import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Vehicle {
  id: string;
  name: string;
  license_plate: string;
  type: string;
  status: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface VehicleCreate {
  name: string;
  license_plate: string;
  type: string;
  status?: string;
  description?: string;
}

export interface VehicleUpdate {
  name?: string;
  license_plate?: string;
  type?: string;
  status?: string;
  description?: string;
}

export interface VehicleFilters {
  status?: string;
  type?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

class VehicleService {
  /**
   * Lấy danh sách xe
   */
  async getVehicles(filters?: VehicleFilters): Promise<Vehicle[]> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // Xây dựng query params
      const params = new URLSearchParams();
      if (filters) {
        if (filters.status) params.append('status', filters.status);
        if (filters.type) params.append('type', filters.type);
        if (filters.search) params.append('search', filters.search);
        if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
        if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
      }
      
      const response = await axios.get(`${API_URL}/api/v1/vehicles`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params
      });
      
      return response.data;
    } catch (error) {
      console.error('Get vehicles error:', error);
      throw error;
    }
  }

  /**
   * Lấy thông tin chi tiết của một xe
   */
  async getVehicle(id: string): Promise<Vehicle> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/vehicles/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Get vehicle ${id} error:`, error);
      throw error;
    }
  }

  /**
   * Tạo xe mới
   */
  async createVehicle(data: VehicleCreate): Promise<Vehicle> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.post(`${API_URL}/api/v1/vehicles`, data, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Create vehicle error:', error);
      throw error;
    }
  }

  /**
   * Cập nhật thông tin xe
   */
  async updateVehicle(id: string, data: VehicleUpdate): Promise<Vehicle> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.put(`${API_URL}/api/v1/vehicles/${id}`, data, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Update vehicle ${id} error:`, error);
      throw error;
    }
  }

  /**
   * Xóa xe
   */
  async deleteVehicle(id: string): Promise<void> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      await axios.delete(`${API_URL}/api/v1/vehicles/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error(`Delete vehicle ${id} error:`, error);
      throw error;
    }
  }
}

export default new VehicleService();
