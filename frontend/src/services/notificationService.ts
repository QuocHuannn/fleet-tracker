import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8004/ws';

export interface Alert {
  id: string;
  vehicle_id?: string;
  type: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
}

export interface NotificationRule {
  id: string;
  name: string;
  description?: string;
  condition: Record<string, any>;
  action: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WebSocketMessage {
  type: string;
  vehicle_id?: string;
  data: any;
}

export type MessageHandler = (message: WebSocketMessage) => void;

class NotificationService {
  private socket: WebSocket | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectTimeout: number = 1000;

  /**
   * Kết nối WebSocket
   */
  connect(token: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    this.socket = new WebSocket(`${WS_URL}?token=${token}`);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  /**
   * Ngắt kết nối WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * Kết nối lại WebSocket
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const timeout = this.reconnectTimeout * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${timeout}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      const token = localStorage.getItem('token');
      if (token) {
        this.connect(token);
      }
    }, timeout);
  }

  /**
   * Xử lý message từ WebSocket
   */
  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => handler(message));
  }

  /**
   * Đăng ký handler cho loại message
   */
  onMessage(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);
  }

  /**
   * Subscribe vào updates của các xe
   */
  subscribeToVehicleUpdates(vehicleIds: string[]): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    this.socket.send(JSON.stringify({
      type: 'subscribe',
      vehicle_ids: vehicleIds
    }));
  }

  /**
   * Subscribe vào tất cả alerts
   */
  subscribeToAlerts(): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    this.socket.send(JSON.stringify({
      type: 'subscribe',
      subscribe_to_alerts: true
    }));
  }

  /**
   * Lấy danh sách alerts
   */
  async getAlerts(acknowledged?: boolean, vehicleId?: string): Promise<Alert[]> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // Xây dựng query params
      const params = new URLSearchParams();
      if (acknowledged !== undefined) params.append('acknowledged', acknowledged.toString());
      if (vehicleId) params.append('vehicle_id', vehicleId);
      
      const response = await axios.get(`${API_URL}/api/v1/alerts`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params
      });
      
      return response.data;
    } catch (error) {
      console.error('Get alerts error:', error);
      throw error;
    }
  }

  /**
   * Xác nhận alert
   */
  async acknowledgeAlert(alertId: string): Promise<Alert> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.post(`${API_URL}/api/v1/alerts/${alertId}/acknowledge`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Acknowledge alert ${alertId} error:`, error);
      throw error;
    }
  }

  /**
   * Lấy danh sách notification rules
   */
  async getNotificationRules(): Promise<NotificationRule[]> {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${API_URL}/api/v1/notification-rules`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Get notification rules error:', error);
      throw error;
    }
  }
}

export default new NotificationService();
