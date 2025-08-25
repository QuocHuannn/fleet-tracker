import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Chip,
  Divider,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  LocationOn as LocationIcon,
  Speed as SpeedIcon,
  DirectionsCar as CarIcon,
  Schedule as ScheduleIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { Vehicle } from '../../services/vehicleService';

interface VehicleDetailsProps {
  open: boolean;
  onClose: () => void;
  vehicle: Vehicle | null;
  onEdit?: () => void;
}

const VehicleDetails: React.FC<VehicleDetailsProps> = ({
  open,
  onClose,
  vehicle,
  onEdit
}) => {
  if (!vehicle) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

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

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Vehicle Details
          </Typography>
          <Box>
            {onEdit && (
              <Tooltip title="Edit Vehicle">
                <IconButton onClick={onEdit} size="small" sx={{ mr: 1 }}>
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title="Close">
              <IconButton onClick={onClose} size="small">
                <CloseIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 0 }}>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Basic Information
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      License Plate:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {vehicle.license_plate}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Make:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {vehicle.make}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Model:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {vehicle.model}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Year:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {vehicle.year}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      Status:
                    </Typography>
                    <Chip
                      label={vehicle.status}
                      color={getStatusColor(vehicle.status) as any}
                      size="small"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Current Status */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Status
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {vehicle.current_speed !== null && (
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <SpeedIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          Current Speed:
                        </Typography>
                      </Box>
                      <Chip
                        label={`${vehicle.current_speed} km/h`}
                        color={getSpeedColor(vehicle.current_speed) as any}
                        size="small"
                      />
                    </Box>
                  )}
                  
                  {vehicle.last_location && (
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <LocationIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          Last Location:
                        </Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="medium">
                        {vehicle.last_location.latitude.toFixed(6)}, {vehicle.last_location.longitude.toFixed(6)}
                      </Typography>
                    </Box>
                  )}

                  {vehicle.last_location && (
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <ScheduleIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          Last Update:
                        </Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="medium">
                        {formatDate(vehicle.last_location.timestamp)}
                      </Typography>
                    </Box>
                  )}

                  {vehicle.device_id && (
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Device ID:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {vehicle.device_id}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* System Information */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Vehicle ID:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {vehicle.id}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Created:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {formatDate(vehicle.created_at)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Updated:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {formatDate(vehicle.updated_at)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Total Distance:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {vehicle.total_distance ? `${vehicle.total_distance} km` : 'N/A'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        {onEdit && (
          <Button onClick={onEdit} variant="contained">
            Edit Vehicle
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default VehicleDetails;
