import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import { vehicleService, Vehicle, CreateVehicleRequest, UpdateVehicleRequest } from '../../services/vehicleService.ts';

interface VehicleFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  vehicle?: Vehicle | null;
  mode: 'create' | 'edit';
}

const VehicleForm: React.FC<VehicleFormProps> = ({
  open,
  onClose,
  onSuccess,
  vehicle,
  mode
}) => {
  const [formData, setFormData] = useState<CreateVehicleRequest>({
    license_plate: '',
    make: '',
    model: '',
    year: new Date().getFullYear(),
    device_id: undefined
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (vehicle && mode === 'edit') {
      setFormData({
        license_plate: vehicle.license_plate,
        make: vehicle.make,
        model: vehicle.model,
        year: vehicle.year,
        device_id: vehicle.device_id || ''
      });
    } else {
      setFormData({
        license_plate: '',
        make: '',
        model: '',
        year: new Date().getFullYear(),
        device_id: undefined
      });
    }
    setError(null);
  }, [vehicle, mode, open]);

  const handleInputChange = (field: keyof CreateVehicleRequest) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'year' ? parseInt(event.target.value) : event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'create') {
        await vehicleService.createVehicle(formData);
      } else if (vehicle) {
        const updateData: UpdateVehicleRequest = {
          license_plate: formData.license_plate,
          make: formData.make,
          model: formData.model,
          year: formData.year,
          device_id: formData.device_id || undefined
        };
        await vehicleService.updateVehicle(vehicle.id, updateData);
      }

      onSuccess();
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to save vehicle');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Add New Vehicle' : 'Edit Vehicle'}
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="License Plate"
              value={formData.license_plate}
              onChange={handleInputChange('license_plate')}
              required
              fullWidth
              disabled={loading}
            />

            <TextField
              label="Make"
              value={formData.make}
              onChange={handleInputChange('make')}
              required
              fullWidth
              disabled={loading}
            />

            <TextField
              label="Model"
              value={formData.model}
              onChange={handleInputChange('model')}
              required
              fullWidth
              disabled={loading}
            />

            <TextField
              label="Year"
              type="number"
              value={formData.year}
              onChange={handleInputChange('year')}
              required
              fullWidth
              disabled={loading}
              inputProps={{ min: 1900, max: new Date().getFullYear() + 1 }}
            />

            <TextField
              label="Device ID (Optional)"
              value={formData.device_id || ''}
              onChange={handleInputChange('device_id')}
              fullWidth
              disabled={loading}
              helperText="GPS device identifier"
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Saving...' : mode === 'create' ? 'Create Vehicle' : 'Update Vehicle'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default VehicleForm;
