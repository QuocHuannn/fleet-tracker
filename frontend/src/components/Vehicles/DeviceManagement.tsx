import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Bluetooth as BluetoothIcon,
  SignalCellular4Bar as SignalIcon,
  Battery90 as BatteryIcon
} from '@mui/icons-material';
import { Vehicle } from '../../services/vehicleService';

interface Device {
  id: string;
  device_id: string;
  vehicle_id: string;
  device_type: string;
  status: 'active' | 'inactive' | 'maintenance';
  last_seen: string;
  battery_level?: number;
  signal_strength?: number;
  firmware_version?: string;
  created_at: string;
  updated_at: string;
}

interface DeviceManagementProps {
  open: boolean;
  onClose: () => void;
  vehicle: Vehicle | null;
}

const DeviceManagement: React.FC<DeviceManagementProps> = ({
  open,
  onClose,
  vehicle
}) => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);

  // Mock devices for development
  const mockDevices: Device[] = [
    {
      id: '1',
      device_id: 'GPS_001',
      vehicle_id: vehicle?.id || '',
      device_type: 'GPS Tracker',
      status: 'active',
      last_seen: new Date().toISOString(),
      battery_level: 85,
      signal_strength: 90,
      firmware_version: 'v2.1.0',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      device_id: 'SENSOR_001',
      vehicle_id: vehicle?.id || '',
      device_type: 'Engine Sensor',
      status: 'active',
      last_seen: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
      battery_level: 92,
      signal_strength: 85,
      firmware_version: 'v1.5.2',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  useEffect(() => {
    if (open && vehicle) {
      setDevices(mockDevices);
    }
  }, [open, vehicle]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  const getBatteryColor = (level: number) => {
    if (level < 20) return 'error';
    if (level < 50) return 'warning';
    return 'success';
  };

  const getSignalColor = (strength: number) => {
    if (strength < 30) return 'error';
    if (strength < 70) return 'warning';
    return 'success';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  const handleAddDevice = () => {
    setShowAddForm(true);
    setEditingDevice(null);
  };

  const handleEditDevice = (device: Device) => {
    setEditingDevice(device);
    setShowAddForm(true);
  };

  const handleDeleteDevice = (deviceId: string) => {
    setDevices(prev => prev.filter(d => d.id !== deviceId));
  };

  const handleCloseForm = () => {
    setShowAddForm(false);
    setEditingDevice(null);
  };

  if (!vehicle) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Device Management - {vehicle.license_plate}
          </Typography>
          <Box>
            <Tooltip title="Add Device">
              <IconButton onClick={handleAddDevice} size="small" sx={{ mr: 1 }}>
                <AddIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Close">
              <IconButton onClick={onClose} size="small">
                <CloseIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 0 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Device Summary */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Device Summary
                </Typography>
                <Box display="flex" gap={2} flexWrap="wrap">
                  <Chip
                    icon={<BluetoothIcon />}
                    label={`${devices.length} Total Devices`}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={`${devices.filter(d => d.status === 'active').length} Active`}
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    label={`${devices.filter(d => d.status === 'inactive').length} Inactive`}
                    color="error"
                    variant="outlined"
                  />
                  <Chip
                    label={`${devices.filter(d => d.status === 'maintenance').length} Maintenance`}
                    color="warning"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Devices Table */}
          <Grid item xs={12}>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Device ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Battery</TableCell>
                    <TableCell>Signal</TableCell>
                    <TableCell>Last Seen</TableCell>
                    <TableCell>Firmware</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {devices.map((device) => (
                    <TableRow key={device.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {device.device_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {device.device_type}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={device.status}
                          color={getStatusColor(device.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {device.battery_level !== undefined ? (
                          <Box display="flex" alignItems="center" gap={1}>
                            <BatteryIcon 
                              fontSize="small" 
                              color={getBatteryColor(device.battery_level) as any}
                            />
                            <Typography variant="body2">
                              {device.battery_level}%
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {device.signal_strength !== undefined ? (
                          <Box display="flex" alignItems="center" gap={1}>
                            <SignalIcon 
                              fontSize="small" 
                              color={getSignalColor(device.signal_strength) as any}
                            />
                            <Typography variant="body2">
                              {device.signal_strength}%
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(device.last_seen)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {device.firmware_version || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box display="flex" gap={1} justifyContent="center">
                          <Tooltip title="Edit Device">
                            <IconButton
                              size="small"
                              onClick={() => handleEditDevice(device)}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Device">
                            <IconButton
                              size="small"
                              onClick={() => handleDeleteDevice(device.id)}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>

        {/* Add/Edit Device Form */}
        {showAddForm && (
          <Dialog 
            open={showAddForm} 
            onClose={handleCloseForm}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle>
              {editingDevice ? 'Edit Device' : 'Add New Device'}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
                <TextField
                  label="Device ID"
                  defaultValue={editingDevice?.device_id || ''}
                  fullWidth
                />
                <TextField
                  label="Device Type"
                  defaultValue={editingDevice?.device_type || ''}
                  fullWidth
                />
                <TextField
                  label="Firmware Version"
                  defaultValue={editingDevice?.firmware_version || ''}
                  fullWidth
                />
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseForm}>
                Cancel
              </Button>
              <Button variant="contained">
                {editingDevice ? 'Update Device' : 'Add Device'}
              </Button>
            </DialogActions>
          </Dialog>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeviceManagement;
