import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Vehicle {
  id: string;
  license_plate: string;
  make: string;
  model: string;
  year: number;
  status: 'active' | 'inactive' | 'maintenance';
  device_id?: string;
  last_location?: {
    latitude: number;
    longitude: number;
    timestamp: string;
  };
  current_speed?: number;
  total_distance?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateVehicleRequest {
  license_plate: string;
  make: string;
  model: string;
  year: number;
  device_id?: string | undefined;
}

export interface UpdateVehicleRequest {
  license_plate?: string;
  make?: string;
  model?: string;
  year?: number;
  status?: 'active' | 'inactive' | 'maintenance';
  device_id?: string;
}

class VehicleService {
  private getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Lấy danh sách tất cả vehicles
   */
  async getVehicles(): Promise<Vehicle[]> {
    try {
      const response = await axios.get(`${API_URL}/vehicles/`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      throw error;
    }
  }

  /**
   * Lấy thông tin vehicle theo ID
   */
  async getVehicle(id: string): Promise<Vehicle> {
    try {
      const response = await axios.get(`${API_URL}/vehicles/${id}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle:', error);
      throw error;
    }
  }

  /**
   * Tạo vehicle mới
   */
  async createVehicle(vehicleData: CreateVehicleRequest): Promise<Vehicle> {
    try {
      const response = await axios.post(`${API_URL}/vehicles/`, vehicleData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error creating vehicle:', error);
      throw error;
    }
  }

  /**
   * Cập nhật vehicle
   */
  async updateVehicle(id: string, vehicleData: UpdateVehicleRequest): Promise<Vehicle> {
    try {
      const response = await axios.put(`${API_URL}/vehicles/${id}`, vehicleData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error updating vehicle:', error);
      throw error;
    }
  }

  /**
   * Xóa vehicle
   */
  async deleteVehicle(id: string): Promise<void> {
    try {
      await axios.delete(`${API_URL}/vehicles/${id}`, {
        headers: this.getAuthHeaders()
      });
    } catch (error) {
      console.error('Error deleting vehicle:', error);
      throw error;
    }
  }

  /**
   * Lấy vị trí hiện tại của vehicle
   */
  async getVehicleLocation(id: string): Promise<{
    latitude: number;
    longitude: number;
    timestamp: string;
    speed?: number;
  }> {
    try {
      const response = await axios.get(`${API_URL}/vehicles/${id}/location`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle location:', error);
      throw error;
    }
  }

  /**
   * Lấy lịch sử vị trí của vehicle
   */
  async getVehicleLocationHistory(
    id: string,
    startDate?: string,
    endDate?: string
  ): Promise<Array<{
    latitude: number;
    longitude: number;
    timestamp: string;
    speed?: number;
  }>> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await axios.get(`${API_URL}/vehicles/${id}/location/history?${params}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle location history:', error);
      throw error;
    }
  }
}

export const vehicleService = new VehicleService();
export default vehicleService;
