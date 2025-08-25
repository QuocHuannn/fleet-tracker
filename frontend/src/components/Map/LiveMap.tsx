import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  MyLocation as LocationIcon,
  Speed as SpeedIcon,
  DirectionsCar as CarIcon
} from '@mui/icons-material';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import config from '../../config/environment';
import { websocketService, VehicleLocation, Alert } from '../../services/websocketService';

import { Vehicle } from '../../services/vehicleService';

interface LiveMapProps {
  vehicles?: Vehicle[];
  loading?: boolean;
}

const LiveMap: React.FC<LiveMapProps> = ({ vehicles = [], loading = false }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<{ [key: string]: mapboxgl.Marker }>({});
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  // Mock data for development
  const mockVehicles: Vehicle[] = [
    {
      id: '1',
      license_plate: 'ABC-123',
      make: 'Toyota',
      model: 'Hilux',
      year: 2022,
      status: 'active',
      device_id: 'GPS001',
      last_location: {
        latitude: 10.762622,
        longitude: 106.660172,
        timestamp: new Date().toISOString()
      },
      current_speed: 45,
      total_distance: 15000,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      license_plate: 'XYZ-789',
      make: 'Ford',
      model: 'Ranger',
      year: 2021,
      status: 'active',
      device_id: 'GPS002',
      last_location: {
        latitude: 10.782622,
        longitude: 106.680172,
        timestamp: new Date().toISOString()
      },
      current_speed: 30,
      total_distance: 12000,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  const displayVehicles = vehicles.length > 0 ? vehicles : mockVehicles;

  // WebSocket event handlers
  useEffect(() => {
    const handleLocationUpdate = (data: VehicleLocation) => {
      setVehicles(prev => {
        const updated = prev.map(v => 
          v.id === data.vehicle_id 
            ? { ...v, last_location: { latitude: data.latitude, longitude: data.longitude, timestamp: data.timestamp }, current_speed: data.speed }
            : v
        );
        return updated;
      });
      
      // Update marker on map
      updateVehicleMarker(data);
    };

    const handleAlert = (data: Alert) => {
      setAlerts(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 alerts
    };

    const handleConnection = () => {
      setWsConnected(true);
    };

    // Subscribe to WebSocket events
    websocketService.on('location_update', handleLocationUpdate);
    websocketService.on('alert', handleAlert);
    websocketService.on('connection_established', handleConnection);

    // Check connection status
    setWsConnected(websocketService.isConnected());

    return () => {
      websocketService.off('location_update', handleLocationUpdate);
      websocketService.off('alert', handleAlert);
      websocketService.off('connection_established', handleConnection);
    };
  }, []);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Initialize map
    mapboxgl.accessToken = config.MAPBOX_TOKEN;
    
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [config.DEFAULT_MAP_CENTER.longitude, config.DEFAULT_MAP_CENTER.latitude],
      zoom: config.DEFAULT_MAP_CENTER.zoom
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add geolocate control
    map.current.addControl(
      new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true,
        showUserHeading: true
      }),
      'top-right'
    );

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, []);

  useEffect(() => {
    if (!map.current) return;

    // Wait for map to load
    map.current.on('load', () => {
      addVehicleMarkers();
    });

    if (map.current.isStyleLoaded()) {
      addVehicleMarkers();
    }
  }, [displayVehicles]);

  const updateVehicleMarker = (locationData: VehicleLocation) => {
    if (!map.current) return;

    const vehicleId = locationData.vehicle_id;
    const { latitude, longitude } = locationData;

    // Update existing marker or create new one
    if (markers.current[vehicleId]) {
      markers.current[vehicleId].setLngLat([longitude, latitude]);
    } else {
      // Create new marker
      const markerEl = document.createElement('div');
      markerEl.className = 'vehicle-marker';
      markerEl.innerHTML = `
        <div style="
          background: #4caf50;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          cursor: pointer;
        "></div>
      `;

      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0;">Vehicle ${vehicleId}</h4>
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            Speed: <strong>${locationData.speed} km/h</strong>
          </p>
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            Last Update: ${new Date(locationData.timestamp).toLocaleTimeString()}
          </p>
        </div>
      `);

      const marker = new mapboxgl.Marker(markerEl)
        .setLngLat([longitude, latitude])
        .setPopup(popup)
        .addTo(map.current);

      markers.current[vehicleId] = marker;
    }
  };

  const addVehicleMarkers = () => {
    if (!map.current) return;

    // Clear existing markers
    Object.values(markers.current).forEach(marker => marker.remove());
    markers.current = {};

    // Add new markers
    displayVehicles.forEach(vehicle => {
      if (!vehicle.last_location) return;

      const { latitude, longitude } = vehicle.last_location;

      // Create custom marker element
      const markerEl = document.createElement('div');
      markerEl.className = 'vehicle-marker';
      markerEl.innerHTML = `
        <div style="
          background: ${vehicle.status === 'active' ? '#4caf50' : '#ff9800'};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          cursor: pointer;
        "></div>
      `;

      // Create popup
      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0;">${vehicle.license_plate}</h4>
          <p style="margin: 4px 0; font-size: 14px;">
            <strong>${vehicle.make} ${vehicle.model}</strong>
          </p>
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            Status: <span style="color: ${vehicle.status === 'active' ? '#4caf50' : '#ff9800'}">${vehicle.status}</span>
          </p>
          ${vehicle.current_speed ? `
            <p style="margin: 4px 0; font-size: 12px; color: #666;">
              Speed: <strong>${vehicle.current_speed} km/h</strong>
            </p>
          ` : ''}
          <p style="margin: 4px 0; font-size: 12px; color: #666;">
            Last Update: ${new Date(vehicle.last_location.timestamp).toLocaleTimeString()}
          </p>
        </div>
      `);

      // Create marker
      const marker = new mapboxgl.Marker(markerEl)
        .setLngLat([longitude, latitude])
        .setPopup(popup)
        .addTo(map.current);

      markers.current[vehicle.id] = marker;
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'default';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" component="h2">
          Live Map
        </Typography>
        <Box display="flex" gap={1}>
          <Chip
            icon={<CarIcon />}
            label={`${displayVehicles.filter(v => v.status === 'active').length} Active`}
            color="success"
            size="small"
          />
          <Chip
            icon={<SpeedIcon />}
            label={`${displayVehicles.filter(v => v.current_speed && v.current_speed > 0).length} Moving`}
            color="primary"
            size="small"
          />
          <Chip
            icon={<LocationIcon />}
            label={wsConnected ? "Live" : "Offline"}
            color={wsConnected ? "success" : "error"}
            size="small"
          />
        </Box>
      </Box>

      <Paper sx={{ position: 'relative', height: '600px' }}>
        {loading && (
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            display="flex"
            alignItems="center"
            justifyContent="center"
            bgcolor="rgba(255,255,255,0.8)"
            zIndex={1000}
          >
            <CircularProgress />
          </Box>
        )}

        <div
          ref={mapContainer}
          style={{
            width: '100%',
            height: '100%',
            borderRadius: '4px'
          }}
        />

        {/* Vehicle List Overlay */}
        <Box
          position="absolute"
          top={16}
          left={16}
          maxWidth={300}
          maxHeight={400}
          overflow="auto"
          bgcolor="rgba(255,255,255,0.95)"
          borderRadius={1}
          p={1}
        >
          <Typography variant="subtitle2" gutterBottom>
            Vehicles
          </Typography>
          {displayVehicles.map(vehicle => (
            <Card key={vehicle.id} sx={{ mb: 1, cursor: 'pointer' }} onClick={() => {
              if (vehicle.last_location && map.current) {
                map.current.flyTo({
                  center: [vehicle.last_location.longitude, vehicle.last_location.latitude],
                  zoom: 15
                });
              }
            }}>
              <CardContent sx={{ py: 1, px: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="body2" fontWeight="bold">
                      {vehicle.license_plate}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {vehicle.make} {vehicle.model}
                    </Typography>
                  </Box>
                  <Chip
                    label={vehicle.status}
                    color={getStatusColor(vehicle.status) as any}
                    size="small"
                  />
                </Box>
                {vehicle.current_speed && (
                  <Typography variant="caption" color="textSecondary">
                    Speed: {vehicle.current_speed} km/h
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default LiveMap;
