import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
// Simple icon imports
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import SettingsIcon from '@mui/icons-material/Settings';
import VehicleForm from './VehicleForm';
import VehicleDetails from './VehicleDetails';
import DeviceManagement from './DeviceManagement';
import { Vehicle } from '../../services/vehicleService';

interface VehicleListProps {
  onEdit?: (vehicle: Vehicle) => void;
  onDelete?: (vehicleId: string) => void;
  onView?: (vehicle: Vehicle) => void;
  onAdd?: () => void;
}

const VehicleList: React.FC<VehicleListProps> = ({
  onEdit,
  onDelete,
  onView,
  onAdd
}) => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [formOpen, setFormOpen] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [deviceManagementOpen, setDeviceManagementOpen] = useState(false);

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual API call
      // const response = await vehicleService.getVehicles();
      // setVehicles(response.data);
      
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
        },
        {
          id: '3',
          license_plate: 'DEF-456',
          make: 'Isuzu',
          model: 'D-Max',
          year: 2023,
          status: 'maintenance',
          device_id: 'GPS003',
          total_distance: 8000,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      setError('Failed to fetch vehicles');
      console.error('Error fetching vehicles:', error);
    } finally {
      setLoading(false);
    }
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

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAddVehicle = () => {
    setFormMode('create');
    setSelectedVehicle(null);
    setFormOpen(true);
  };

  const handleEditVehicle = (vehicle: Vehicle) => {
    setFormMode('edit');
    setSelectedVehicle(vehicle);
    setFormOpen(true);
  };

  const handleFormSuccess = () => {
    fetchVehicles();
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setSelectedVehicle(null);
  };

  const handleViewDetails = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle);
    setDetailsOpen(true);
  };

  const handleDeviceManagement = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle);
    setDeviceManagementOpen(true);
  };

  const handleDetailsClose = () => {
    setDetailsOpen(false);
    setSelectedVehicle(null);
  };

  const handleDeviceManagementClose = () => {
    setDeviceManagementOpen(false);
    setSelectedVehicle(null);
  };

  const handleEditFromDetails = () => {
    setDetailsOpen(false);
    setFormMode('edit');
    setFormOpen(true);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" component="h2">
          Vehicles
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddVehicle}
        >
          Add Vehicle
        </Button>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>License Plate</TableCell>
                <TableCell>Make & Model</TableCell>
                <TableCell>Year</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Device ID</TableCell>
                <TableCell>Last Location</TableCell>
                <TableCell>Current Speed</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {vehicles
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((vehicle) => (
                  <TableRow key={vehicle.id} hover>
                    <TableCell>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {vehicle.license_plate}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {vehicle.make} {vehicle.model}
                    </TableCell>
                    <TableCell>{vehicle.year}</TableCell>
                    <TableCell>
                      <Chip
                        label={vehicle.status}
                        color={getStatusColor(vehicle.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{vehicle.device_id || '-'}</TableCell>
                    <TableCell>
                      {vehicle.last_location ? (
                        <Typography variant="body2" color="textSecondary">
                          {vehicle.last_location.latitude.toFixed(6)}, {vehicle.last_location.longitude.toFixed(6)}
                        </Typography>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {vehicle.current_speed ? `${vehicle.current_speed} km/h` : '-'}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(vehicle)}
                        title="View Details"
                        color="primary"
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleEditVehicle(vehicle)}
                        title="Edit Vehicle"
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeviceManagement(vehicle)}
                        title="Device Management"
                        color="secondary"
                      >
                        <SettingsIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => onDelete?.(vehicle.id)}
                        title="Delete Vehicle"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={vehicles.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Vehicle Form Dialog */}
      <VehicleForm
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        vehicle={selectedVehicle}
        mode={formMode}
      />

      {/* Vehicle Details Dialog */}
      <VehicleDetails
        open={detailsOpen}
        onClose={handleDetailsClose}
        vehicle={selectedVehicle}
        onEdit={handleEditFromDetails}
      />

      {/* Device Management Dialog */}
      <DeviceManagement
        open={deviceManagementOpen}
        onClose={handleDeviceManagementClose}
        vehicle={selectedVehicle}
      />
    </Box>
  );
};

export default VehicleList;
