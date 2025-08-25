import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  DirectionsCar as CarIcon,
  Speed as SpeedIcon,
  LocationOn as LocationIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Vehicle } from '../../services/vehicleService';

interface VehicleStatusMonitoringProps {
  vehicles: Vehicle[];
  loading?: boolean;
  onRefresh?: () => void;
}

interface StatusSummary {
  total: number;
  active: number;
  inactive: number;
  maintenance: number;
  moving: number;
  stopped: number;
  offline: number;
}

const VehicleStatusMonitoring: React.FC<VehicleStatusMonitoringProps> = ({
  vehicles,
  loading = false,
  onRefresh
}) => {
  const [statusSummary, setStatusSummary] = useState<StatusSummary>({
    total: 0,
    active: 0,
    inactive: 0,
    maintenance: 0,
    moving: 0,
    stopped: 0,
    offline: 0
  });

  useEffect(() => {
    if (vehicles.length > 0) {
      const summary: StatusSummary = {
        total: vehicles.length,
        active: vehicles.filter(v => v.status === 'active').length,
        inactive: vehicles.filter(v => v.status === 'inactive').length,
        maintenance: vehicles.filter(v => v.status === 'maintenance').length,
        moving: vehicles.filter(v => v.current_speed && v.current_speed > 0).length,
        stopped: vehicles.filter(v => v.current_speed === 0).length,
        offline: vehicles.filter(v => !v.last_location || 
          new Date().getTime() - new Date(v.last_location.timestamp).getTime() > 300000).length // 5 minutes
      };
      setStatusSummary(summary);
    }
  }, [vehicles]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  const getSpeedColor = (speed: number) => {
    if (speed === 0) return 'default';
    if (speed > 80) return 'error';
    if (speed > 60) return 'warning';
    return 'success';
  };

  const getUptimePercentage = () => {
    if (statusSummary.total === 0) return 0;
    return Math.round((statusSummary.active / statusSummary.total) * 100);
  };

  const getOnlinePercentage = () => {
    if (statusSummary.total === 0) return 0;
    const online = statusSummary.total - statusSummary.offline;
    return Math.round((online / statusSummary.total) * 100);
  };

  const formatLastSeen = (timestamp: string) => {
    const now = new Date().getTime();
    const lastSeen = new Date(timestamp).getTime();
    const diff = now - lastSeen;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  const getCriticalAlerts = () => {
    return vehicles.filter(v => {
      // Speed alerts
      if (v.current_speed && v.current_speed > 100) return true;
      
      // Offline alerts
      if (!v.last_location) return true;
      const lastSeen = new Date(v.last_location.timestamp).getTime();
      const now = new Date().getTime();
      if (now - lastSeen > 900000) return true; // 15 minutes
      
      return false;
    });
  };

  const criticalAlerts = getCriticalAlerts();

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          Vehicle Status Monitoring
        </Typography>
        <Box display="flex" gap={1}>
          {criticalAlerts.length > 0 && (
            <Chip
              icon={<WarningIcon />}
              label={`${criticalAlerts.length} Critical Alerts`}
              color="error"
              size="small"
            />
          )}
          <Tooltip title="Refresh Status">
            <IconButton onClick={onRefresh} disabled={loading} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>{criticalAlerts.length} vehicles</strong> require attention:
            {criticalAlerts.slice(0, 3).map(v => ` ${v.license_plate}`).join(',')}
            {criticalAlerts.length > 3 && ` and ${criticalAlerts.length - 3} more`}
          </Typography>
        </Alert>
      )}

      {/* Status Overview */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <CarIcon color="primary" />
                <Typography variant="h6">{statusSummary.total}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Vehicles
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <CheckCircleIcon color="success" />
                <Typography variant="h6">{statusSummary.active}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <SpeedIcon color="primary" />
                <Typography variant="h6">{statusSummary.moving}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Moving
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <ErrorIcon color="error" />
                <Typography variant="h6">{statusSummary.offline}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Offline
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Progress Indicators */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                System Uptime
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Box flex={1}>
                  <LinearProgress
                    variant="determinate"
                    value={getUptimePercentage()}
                    color={getUptimePercentage() > 80 ? 'success' : 'warning'}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Typography variant="body2" fontWeight="medium">
                  {getUptimePercentage()}%
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {statusSummary.active} of {statusSummary.total} vehicles active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Online Status
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Box flex={1}>
                  <LinearProgress
                    variant="determinate"
                    value={getOnlinePercentage()}
                    color={getOnlinePercentage() > 90 ? 'success' : 'error'}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Typography variant="body2" fontWeight="medium">
                  {getOnlinePercentage()}%
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {statusSummary.total - statusSummary.offline} of {statusSummary.total} vehicles online
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Vehicle Status List */}
      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle1" gutterBottom>
            Vehicle Status Details
          </Typography>
          
          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : vehicles.length === 0 ? (
            <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
              No vehicles found
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {vehicles.map((vehicle) => (
                <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                        <Typography variant="subtitle2" fontWeight="medium">
                          {vehicle.license_plate}
                        </Typography>
                        <Chip
                          label={vehicle.status}
                          color={getStatusColor(vehicle.status) as any}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" mb={1}>
                        {vehicle.make} {vehicle.model} ({vehicle.year})
                      </Typography>

                      <Box display="flex" flexDirection="column" gap={0.5}>
                        {vehicle.current_speed !== null && (
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="caption" color="text.secondary">
                              Speed:
                            </Typography>
                            <Chip
                              label={`${vehicle.current_speed} km/h`}
                              color={getSpeedColor(vehicle.current_speed) as any}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        )}

                        {vehicle.last_location && (
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="caption" color="text.secondary">
                              Last Seen:
                            </Typography>
                            <Typography variant="caption">
                              {formatLastSeen(vehicle.last_location.timestamp)}
                            </Typography>
                          </Box>
                        )}

                        {vehicle.device_id && (
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="caption" color="text.secondary">
                              Device:
                            </Typography>
                            <Typography variant="caption">
                              {vehicle.device_id}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default VehicleStatusMonitoring;
