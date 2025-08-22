import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Location {
  id: string;
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  altitude?: number;
  accuracy?: number;
  recorded_at: string;
  created_at: string;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface Geofence {
  id: string;
  name: string;
  type: string;
  boundary: GeoJSON.Polygon;
  description?: string;
  created_at: string;
  updated_at: string;
}

class LocationService {
  /**
   * Lấy vị trí hiện tại của xe
   */
  async getCurrentLocation(vehicleId: string): Promise<Location> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/locations/current/${vehicleId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Get current location for vehicle ${vehicleId} error:`, error);
      throw error;
    }
  }

  /**
   * Lấy lịch sử vị trí của xe
   */
  async getLocationHistory(vehicleId: string, timeRange: TimeRange): Promise<Location[]> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/locations/history/${vehicleId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params: {
          start: timeRange.start,
          end: timeRange.end
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Get location history for vehicle ${vehicleId} error:`, error);
      throw error;
    }
  }

  /**
   * Lấy danh sách geofences
   */
  async getGeofences(): Promise<Geofence[]> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/geofences`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Get geofences error:', error);
      throw error;
    }
  }

  /**
   * Tạo geofence mới
   */
  async createGeofence(geofence: Omit<Geofence, 'id' | 'created_at' | 'updated_at'>): Promise<Geofence> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.post(`${API_URL}/api/v1/geofences`, geofence, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Create geofence error:', error);
      throw error;
    }
  }

  /**
   * Kiểm tra xe có trong geofence không
   */
  async checkGeofence(vehicleId: string, geofenceId: string): Promise<boolean> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/geofences/check`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params: {
          vehicle_id: vehicleId,
          geofence_id: geofenceId
        }
      });
      
      return response.data.inside;
    } catch (error) {
      console.error(`Check geofence for vehicle ${vehicleId} error:`, error);
      throw error;
    }
  }
}

export default new LocationService();
