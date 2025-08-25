import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  DirectionsCar,
  LocationOn,
  Warning,
  Speed,
  Timeline
} from '@mui/icons-material';
import VehicleStatusMonitoring from '../Vehicles/VehicleStatusMonitoring';

import { Vehicle } from '../../services/vehicleService';

interface Alert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  vehicle_id: string;
}

const Dashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    // TODO: Fetch data from API
    const fetchDashboardData = async () => {
      try {
        // Mock data for now
        setVehicles([
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
        ]);

        setAlerts([
          {
            id: '1',
            type: 'speed_violation',
            severity: 'medium',
            message: 'Vehicle ABC-123 exceeded speed limit',
            timestamp: new Date().toISOString(),
            vehicle_id: '1'
          }
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const activeVehicles = vehicles.filter(v => v.status === 'active').length;
  const criticalAlerts = alerts.filter(a => a.severity === 'critical').length;

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Vehicle Status" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <>
          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <DirectionsCar sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{vehicles.length}</Typography>
                      <Typography color="textSecondary">Total Vehicles</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <LocationOn sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{activeVehicles}</Typography>
                      <Typography color="textSecondary">Active Vehicles</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Warning sx={{ fontSize: 40, color: 'error.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{alerts.length}</Typography>
                      <Typography color="textSecondary">Active Alerts</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Speed sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{criticalAlerts}</Typography>
                      <Typography color="textSecondary">Critical Alerts</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Content Grid */}
          <Grid container spacing={3}>
            {/* Recent Alerts */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Alerts
                </Typography>
                <List>
                  {alerts.slice(0, 5).map((alert) => (
                    <ListItem key={alert.id} divider>
                      <ListItemIcon>
                        <Warning color={alert.severity === 'critical' ? 'error' : 'warning'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.message}
                        secondary={new Date(alert.timestamp).toLocaleString()}
                      />
                      <Chip
                        label={alert.severity}
                        color={alert.severity === 'critical' ? 'error' : 'warning'}
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>

            {/* Active Vehicles */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Active Vehicles
                </Typography>
                <List>
                  {vehicles.filter(v => v.status === 'active').map((vehicle) => (
                    <ListItem key={vehicle.id} divider>
                      <ListItemIcon>
                        <DirectionsCar color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={vehicle.license_plate}
                        secondary={`Speed: ${vehicle.current_speed || 0} km/h`}
                      />
                      <Chip label="Active" color="success" size="small" />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </>
      )}

      {activeTab === 1 && (
        <VehicleStatusMonitoring
          vehicles={vehicles}
          loading={loading}
          onRefresh={() => {
            setLoading(true);
            // TODO: Implement refresh logic
            setTimeout(() => setLoading(false), 1000);
          }}
        />
      )}
    </Box>
  );
};

export default Dashboard;
