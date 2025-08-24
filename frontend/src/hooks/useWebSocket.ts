// React Hook for WebSocket integration

import { useEffect, useState, useCallback } from 'react';
import { websocketService } from '../services/websocketService';

interface WebSocketState {
  connected: boolean;
  connectionState: string;
  error: string | null;
  subscriptions: string[];
}

export function useWebSocket() {
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    connectionState: 'disconnected',
    error: null,
    subscriptions: []
  });

  const [alerts, setAlerts] = useState<any[]>([]);
  const [locationUpdates, setLocationUpdates] = useState<any[]>([]);

  useEffect(() => {
    const updateState = () => {
      setState({
        connected: websocketService.isConnected(),
        connectionState: websocketService.getConnectionState(),
        error: null,
        subscriptions: websocketService.getStats().subscriptions
      });
    };

    // Connection handler
    const unsubscribeConnection = websocketService.onConnection((data) => {
      if (data.status === 'connected') {
        setState(prev => ({ ...prev, connected: true, connectionState: 'connected', error: null }));
      } else if (data.status === 'disconnected') {
        setState(prev => ({ ...prev, connected: false, connectionState: 'disconnected' }));
      } else if (data.status === 'error') {
        setState(prev => ({ ...prev, error: 'Connection error', connected: false }));
      }
    });

    // Alert handler
    const unsubscribeAlerts = websocketService.onAlert((alertData) => {
      setAlerts(prev => [alertData, ...prev.slice(0, 49)]); // Keep last 50 alerts
    });

    // Location update handler
    const unsubscribeLocation = websocketService.onLocationUpdate((locationData) => {
      setLocationUpdates(prev => [locationData, ...prev.slice(0, 99)]); // Keep last 100 updates
    });

    // Error handler
    const unsubscribeError = websocketService.onError((errorData) => {
      setState(prev => ({ ...prev, error: errorData.message || 'Unknown error' }));
    });

    // Initial state update
    updateState();

    // Cleanup function
    return () => {
      unsubscribeConnection();
      unsubscribeAlerts();
      unsubscribeLocation();
      unsubscribeError();
    };
  }, []);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));
      await websocketService.connect();
    } catch (error: any) {
      setState(prev => ({ ...prev, error: error.message, connected: false }));
    }
  }, []);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    websocketService.disconnect();
  }, []);

  // Subscribe to topics
  const subscribe = useCallback((subscriptionType: string) => {
    websocketService.subscribe(subscriptionType);
    setState(prev => ({ 
      ...prev, 
      subscriptions: [...new Set([...prev.subscriptions, subscriptionType])]
    }));
  }, []);

  // Unsubscribe from topics
  const unsubscribe = useCallback((subscriptionType: string) => {
    websocketService.unsubscribe(subscriptionType);
    setState(prev => ({ 
      ...prev, 
      subscriptions: prev.subscriptions.filter(s => s !== subscriptionType)
    }));
  }, []);

  // Send ping
  const ping = useCallback(() => {
    websocketService.ping();
  }, []);

  // Get recent alerts
  const getAlerts = useCallback(() => {
    websocketService.getAlerts();
  }, []);

  // Clear alerts
  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  // Clear location updates
  const clearLocationUpdates = useCallback(() => {
    setLocationUpdates([]);
  }, []);

  return {
    // State
    ...state,
    alerts,
    locationUpdates,
    
    // Actions
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    ping,
    getAlerts,
    clearAlerts,
    clearLocationUpdates
  };
}

// Hook for subscribing to specific vehicle updates
export function useVehicleTracking(vehicleId: string | null) {
  const { connected, subscribe, unsubscribe, locationUpdates } = useWebSocket();
  const [vehicleLocation, setVehicleLocation] = useState<any>(null);

  useEffect(() => {
    if (!vehicleId || !connected) return;

    const subscriptionType = `vehicle_${vehicleId}`;
    subscribe(subscriptionType);

    return () => {
      unsubscribe(subscriptionType);
    };
  }, [vehicleId, connected, subscribe, unsubscribe]);

  useEffect(() => {
    // Filter location updates for this specific vehicle
    const latestLocation = locationUpdates.find(update => update.vehicle_id === vehicleId);
    if (latestLocation) {
      setVehicleLocation(latestLocation);
    }
  }, [locationUpdates, vehicleId]);

  return {
    connected,
    vehicleLocation,
    allUpdates: locationUpdates.filter(update => update.vehicle_id === vehicleId)
  };
}

// Hook for fleet-wide alerts
export function useFleetAlerts() {
  const { connected, subscribe, unsubscribe, alerts, getAlerts, clearAlerts } = useWebSocket();
  
  useEffect(() => {
    if (!connected) return;

    subscribe('alerts');
    getAlerts(); // Get recent alerts on connect

    return () => {
      unsubscribe('alerts');
    };
  }, [connected, subscribe, unsubscribe, getAlerts]);

  const criticalAlerts = alerts.filter(alert => alert.severity === 'critical');
  const highAlerts = alerts.filter(alert => alert.severity === 'high');
  const mediumAlerts = alerts.filter(alert => alert.severity === 'medium');

  return {
    connected,
    alerts,
    criticalAlerts,
    highAlerts,
    mediumAlerts,
    clearAlerts,
    totalCount: alerts.length
  };
}
