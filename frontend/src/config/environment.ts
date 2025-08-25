// Environment Configuration
export const config = {
  // API Configuration
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8004/ws',
  
  // Mapbox Configuration
  MAPBOX_TOKEN: process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example',
  
  // Application Configuration
  APP_NAME: process.env.REACT_APP_APP_NAME || 'Fleet Tracker',
  APP_VERSION: process.env.REACT_APP_APP_VERSION || '1.0.0',
  ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
  
  // Feature Flags
  ENABLE_REAL_TIME: process.env.REACT_APP_ENABLE_REAL_TIME === 'true',
  ENABLE_NOTIFICATIONS: process.env.REACT_APP_ENABLE_NOTIFICATIONS === 'true',
  ENABLE_ANALYTICS: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
  
  // Default Map Center (Ho Chi Minh City)
  DEFAULT_MAP_CENTER: {
    latitude: 10.762622,
    longitude: 106.660172,
    zoom: 12
  }
};

export default config;
