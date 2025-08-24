// WebSocket Service for Real-time Communications
// Handles WebSocket connections for live updates

import { firebaseAuthService } from './firebaseAuthService';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
  message_id?: string;
}

interface WebSocketSubscription {
  subscription_type: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private baseURL: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000; // 5 seconds
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private subscriptions: Set<string> = new Set();
  private isConnecting = false;

  constructor() {
    // Convert HTTP URL to WebSocket URL
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.baseURL = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      const token = firebaseAuthService.getAccessToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const wsUrl = `${this.baseURL}:8004/ws?token=${encodeURIComponent(token)}`;
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
      // Wait for connection
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 10000);

        this.ws!.addEventListener('open', () => {
          clearTimeout(timeout);
          resolve(void 0);
        });

        this.ws!.addEventListener('error', () => {
          clearTimeout(timeout);
          reject(new Error('WebSocket connection failed'));
        });
      });

    } finally {
      this.isConnecting = false;
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.reconnectAttempts = 0;
  }

  private handleOpen(event: Event): void {
    console.log('🔗 WebSocket connected');
    this.reconnectAttempts = 0;
    
    // Resubscribe to previous subscriptions
    this.subscriptions.forEach(subscriptionType => {
      this.subscribe(subscriptionType);
    });
    
    // Notify connection listeners
    this.notifyHandlers('connection', { status: 'connected' });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('📨 WebSocket message:', message.type, message.data);
      
      // Handle different message types
      switch (message.type) {
        case 'connection_established':
          this.handleConnectionEstablished(message.data);
          break;
        case 'alert':
          this.notifyHandlers('alert', message.data);
          break;
        case 'location_update':
          this.notifyHandlers('location_update', message.data);
          break;
        case 'subscription_confirmed':
          this.handleSubscriptionConfirmed(message.data);
          break;
        case 'error':
          this.handleServerError(message.data);
          break;
        case 'pong':
          this.handlePong(message.data);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('❌ WebSocket disconnected:', event.code, event.reason);
    this.ws = null;
    
    // Notify disconnection listeners
    this.notifyHandlers('connection', { status: 'disconnected', code: event.code, reason: event.reason });
    
    // Attempt to reconnect if not intentionally closed
    if (event.code !== 1000) { // 1000 = normal closure
      this.attemptReconnect();
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.notifyHandlers('connection', { status: 'error', error: event });
  }

  private handleConnectionEstablished(data: any): void {
    console.log('✅ WebSocket connection established:', data);
  }

  private handleSubscriptionConfirmed(data: any): void {
    console.log('📋 Subscription confirmed:', data.subscription_type);
  }

  private handleServerError(data: any): void {
    console.error('Server error:', data.message);
    this.notifyHandlers('error', data);
  }

  private handlePong(data: any): void {
    console.log('🏓 Pong received:', data);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1), 30000);
    
    console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
        this.attemptReconnect();
      });
    }, delay);
  }

  subscribe(subscriptionType: string): void {
    this.subscriptions.add(subscriptionType);
    
    if (this.isConnected()) {
      this.sendMessage({
        type: 'subscribe',
        data: { subscription_type: subscriptionType }
      });
    }
  }

  unsubscribe(subscriptionType: string): void {
    this.subscriptions.delete(subscriptionType);
    
    if (this.isConnected()) {
      this.sendMessage({
        type: 'unsubscribe',
        data: { subscription_type: subscriptionType }
      });
    }
  }

  ping(): void {
    if (this.isConnected()) {
      this.sendMessage({
        type: 'ping',
        data: { timestamp: new Date().toISOString() }
      });
    }
  }

  getAlerts(): void {
    if (this.isConnected()) {
      this.sendMessage({
        type: 'get_alerts',
        data: {}
      });
    }
  }

  private sendMessage(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected. Cannot send message:', message);
      return;
    }

    message.timestamp = new Date().toISOString();
    message.message_id = this.generateMessageId();
    
    this.ws.send(JSON.stringify(message));
    console.log('📤 Sent WebSocket message:', message.type);
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }

  // Event handlers
  onAlert(handler: (data: any) => void): () => void {
    return this.addMessageHandler('alert', handler);
  }

  onLocationUpdate(handler: (data: any) => void): () => void {
    return this.addMessageHandler('location_update', handler);
  }

  onConnection(handler: (data: any) => void): () => void {
    return this.addMessageHandler('connection', handler);
  }

  onError(handler: (data: any) => void): () => void {
    return this.addMessageHandler('error', handler);
  }

  private addMessageHandler(type: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    
    this.messageHandlers.get(type)!.push(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  private notifyHandlers(type: string, data: any): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in ${type} handler:`, error);
        }
      });
    }
  }

  getStats(): any {
    return {
      connected: this.isConnected(),
      connectionState: this.getConnectionState(),
      subscriptions: Array.from(this.subscriptions),
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

export const websocketService = new WebSocketService();
export type { WebSocketMessage };
