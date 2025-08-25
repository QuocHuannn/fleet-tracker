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
  Tab,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  DirectionsCar,
  LocationOn,
  Warning,
  Speed,
  Timeline,
  Notifications,
  Analytics,
  ArrowForward
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import VehicleStatusMonitoring from '../Vehicles/VehicleStatusMonitoring.tsx';
import AnalyticsDashboard from '../Analytics/AnalyticsDashboard.tsx';

import { Vehicle } from '../../services/vehicleService.ts';
import { Alert, alertService } from '../../services/alertService.ts';

const Dashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch alerts
      const alertsResponse = await alertService.getAlerts(
        { acknowledged: false, resolved: false }, // Only show unresolved alerts
        1,
        5 // Limit to 5 recent alerts
      );
      setAlerts(alertsResponse.alerts);

      // Mock vehicles data - replace with actual API call
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
          current_speed: 38,
          total_distance: 12000,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

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

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Tổng quan" />
          <Tab label="Trạng thái xe" />
          <Tab label="Analytics" />
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
                      <Typography color="textSecondary">Tổng số xe</Typography>
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
                      <Typography color="textSecondary">Xe hoạt động</Typography>
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
                      <Typography color="textSecondary">Cảnh báo</Typography>
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
                      <Typography color="textSecondary">Cảnh báo nghiêm trọng</Typography>
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
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    <Notifications sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Cảnh báo gần đây
                  </Typography>
                  <Button
                    size="small"
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/alerts')}
                  >
                    Xem tất cả
                  </Button>
                </Box>
                <List>
                  {alerts.length === 0 ? (
                    <Typography color="textSecondary" textAlign="center" py={2}>
                      Không có cảnh báo nào
                    </Typography>
                  ) : (
                    alerts.slice(0, 5).map((alert) => (
                      <ListItem key={alert.id} divider>
                        <ListItemIcon>
                          <Warning color={getSeverityColor(alert.severity) as any} />
                        </ListItemIcon>
                        <ListItemText
                          primary={alert.title}
                          secondary={alert.message}
                        />
                        <Chip
                          label={alert.severity}
                          color={getSeverityColor(alert.severity) as any}
                          size="small"
                        />
                      </ListItem>
                    ))
                  )}
                </List>
              </Paper>
            </Grid>

            {/* Active Vehicles */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    <DirectionsCar sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Xe đang hoạt động
                  </Typography>
                  <Button
                    size="small"
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/vehicles')}
                  >
                    Quản lý xe
                  </Button>
                </Box>
                <List>
                  {vehicles.filter(v => v.status === 'active').map((vehicle) => (
                    <ListItem key={vehicle.id} divider>
                      <ListItemIcon>
                        <DirectionsCar color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={vehicle.license_plate}
                        secondary={`Tốc độ: ${vehicle.current_speed || 0} km/h | ${vehicle.make} ${vehicle.model}`}
                      />
                      <Chip label="Hoạt động" color="success" size="small" />
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
          onRefresh={fetchDashboardData}
        />
      )}

      {activeTab === 2 && (
        <AnalyticsDashboard />
      )}
    </Box>
  );
};

export default Dashboard;