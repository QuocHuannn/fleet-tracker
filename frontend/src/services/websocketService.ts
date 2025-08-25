// WebSocket Service for Real-time Communications
// Handles WebSocket connections for live updates

import config from '../config/environment.ts';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface VehicleLocation {
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed: number;
  heading: number;
  timestamp: string;
}

export interface Alert {
  id: string;
  vehicle_id: string;
  type: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor() {
    this.connect();
  }

  private connect() {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        console.warn('No auth token found, WebSocket connection delayed');
        return;
      }

      const wsUrl = `${config.WS_URL}?token=${token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('🔗 WebSocket connected');
        this.reconnectAttempts = 0;
        this.subscribeToUpdates();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  private subscribeToUpdates() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Subscribe to vehicle location updates
      this.sendMessage({
        type: 'subscribe',
        data: { subscription_type: 'all_vehicles' }
      });

      // Subscribe to alerts
      this.sendMessage({
        type: 'subscribe',
        data: { subscription_type: 'alerts' }
      });
    }
  }

  private sendMessage(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('📨 Received WebSocket message:', message.type);

    switch (message.type) {
      case 'location_update':
        this.notifyListeners('location_update', message.data);
        break;
      case 'alert':
        this.notifyListeners('alert', message.data);
        break;
      case 'vehicle_status':
        this.notifyListeners('vehicle_status', message.data);
        break;
      case 'connection_established':
        console.log('✅ WebSocket connection established');
        break;
      case 'error':
        console.error('WebSocket error:', message.data);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private notifyListeners(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => listener(data));
    }
  }

  // Public API
  public on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  public off(event: string, callback: (data: any) => void) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  public subscribeToVehicle(vehicleId: string) {
    this.sendMessage({
      type: 'subscribe',
      data: { subscription_type: `vehicle_${vehicleId}` }
    });
  }

  public unsubscribeFromVehicle(vehicleId: string) {
    this.sendMessage({
      type: 'unsubscribe',
      data: { subscription_type: `vehicle_${vehicleId}` }
    });
  }

  public ping() {
    this.sendMessage({
      type: 'ping',
      data: { timestamp: new Date().toISOString() }
    });
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
