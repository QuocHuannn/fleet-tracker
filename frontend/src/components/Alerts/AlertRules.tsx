import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Alert as MuiAlert,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Speed as SpeedIcon,
  LocationOn as LocationIcon,
  Warning as WarningIcon,
  Build as MaintenanceIcon
} from '@mui/icons-material';

import { AlertRule, alertService } from '../../services/alertService';

const AlertRules: React.FC = () => {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      setError(null);
      const rulesData = await alertService.getAlertRules();
      setRules(rulesData);
    } catch (err) {
      setError('Không thể tải danh sách quy tắc cảnh báo');
      console.error('Error fetching alert rules:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      await alertService.updateAlertRule(ruleId, { enabled });
      await fetchRules();
    } catch (err) {
      setError('Không thể cập nhật quy tắc');
      console.error('Error updating rule:', err);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa quy tắc này?')) {
      try {
        await alertService.deleteAlertRule(ruleId);
        await fetchRules();
      } catch (err) {
        setError('Không thể xóa quy tắc');
        console.error('Error deleting rule:', err);
      }
    }
  };

  const handleAddRule = () => {
    setEditingRule(null);
    setDialogOpen(true);
  };

  const handleEditRule = (rule: AlertRule) => {
    setEditingRule(rule);
    setDialogOpen(true);
  };

  const getTypeIcon = (type: AlertRule['type']) => {
    switch (type) {
      case 'speed_limit':
        return <SpeedIcon />;
      case 'geofence':
        return <LocationIcon />;
      case 'maintenance':
        return <MaintenanceIcon />;
      default:
        return <WarningIcon />;
    }
  };

  const getTypeLabel = (type: AlertRule['type']) => {
    const labels = {
      geofence: 'Vùng địa lý',
      speed_limit: 'Giới hạn tốc độ',
      engine_fault: 'Lỗi động cơ',
      maintenance: 'Bảo dưỡng',
      unauthorized_access: 'Truy cập trái phép',
      low_fuel: 'Nhiên liệu thấp',
      route_deviation: 'Lệch tuyến đường'
    };
    return labels[type] || type;
  };

  const getSeverityColor = (severity: AlertRule['severity']) => {
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Quy tắc Cảnh báo
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddRule}
        >
          Thêm quy tắc
        </Button>
      </Box>

      {error && (
        <MuiAlert severity="error" sx={{ mb: 2 }}>
          {error}
        </MuiAlert>
      )}

      <Card>
        <CardContent>
          {rules.length === 0 ? (
            <Typography color="textSecondary" textAlign="center" py={4}>
              Chưa có quy tắc cảnh báo nào
            </Typography>
          ) : (
            <List>
              {rules.map((rule) => (
                <ListItem key={rule.id} divider>
                  <Box display="flex" alignItems="center" mr={2}>
                    {getTypeIcon(rule.type)}
                  </Box>
                  
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">
                          {rule.name}
                        </Typography>
                        <Chip
                          label={getTypeLabel(rule.type)}
                          size="small"
                          color={getSeverityColor(rule.severity) as any}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Mức độ: {rule.severity} | 
                          Trạng thái: {rule.enabled ? 'Kích hoạt' : 'Tạm dừng'}
                        </Typography>
                        {rule.type === 'speed_limit' && rule.conditions.speed_limit && (
                          <Typography variant="caption" color="textSecondary">
                            Giới hạn: {rule.conditions.speed_limit} km/h
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <Box display="flex" alignItems="center" gap={1}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={rule.enabled}
                            onChange={(e) => handleToggleRule(rule.id, e.target.checked)}
                            size="small"
                          />
                        }
                        label=""
                      />
                      <IconButton
                        size="small"
                        onClick={() => handleEditRule(rule)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteRule(rule.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <AlertRuleDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        rule={editingRule}
        onSuccess={() => {
          setDialogOpen(false);
          fetchRules();
        }}
      />
    </Box>
  );
};

// Alert Rule Dialog Component
interface AlertRuleDialogProps {
  open: boolean;
  onClose: () => void;
  rule: AlertRule | null;
  onSuccess: () => void;
}

const AlertRuleDialog: React.FC<AlertRuleDialogProps> = ({
  open,
  onClose,
  rule,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'speed_limit' as AlertRule['type'],
    severity: 'medium' as AlertRule['severity'],
    enabled: true,
    conditions: {} as any
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (rule) {
      setFormData({
        name: rule.name,
        type: rule.type,
        severity: rule.severity,
        enabled: rule.enabled,
        conditions: rule.conditions
      });
    } else {
      setFormData({
        name: '',
        type: 'speed_limit',
        severity: 'medium',
        enabled: true,
        conditions: {}
      });
    }
  }, [rule]);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      if (rule) {
        await alertService.updateAlertRule(rule.id, formData);
      } else {
        await alertService.createAlertRule(formData);
      }

      onSuccess();
    } catch (err) {
      setError('Không thể lưu quy tắc');
      console.error('Error saving rule:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderConditionFields = () => {
    switch (formData.type) {
      case 'speed_limit':
        return (
          <TextField
            fullWidth
            margin="normal"
            label="Giới hạn tốc độ (km/h)"
            type="number"
            value={formData.conditions.speed_limit || ''}
            onChange={(e) => setFormData({
              ...formData,
              conditions: {
                ...formData.conditions,
                speed_limit: parseInt(e.target.value) || 0
              }
            })}
            required
          />
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {rule ? 'Chỉnh sửa quy tắc' : 'Thêm quy tắc mới'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <MuiAlert severity="error" sx={{ mb: 2 }}>
            {error}
          </MuiAlert>
        )}

        <TextField
          fullWidth
          margin="normal"
          label="Tên quy tắc"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <FormControl fullWidth margin="normal">
          <InputLabel>Loại cảnh báo</InputLabel>
          <Select
            value={formData.type}
            onChange={(e) => setFormData({
              ...formData,
              type: e.target.value as AlertRule['type'],
              conditions: {} // Reset conditions when type changes
            })}
          >
            <MenuItem value="speed_limit">Giới hạn tốc độ</MenuItem>
            <MenuItem value="geofence">Vùng địa lý</MenuItem>
            <MenuItem value="engine_fault">Lỗi động cơ</MenuItem>
            <MenuItem value="maintenance">Bảo dưỡng</MenuItem>
            <MenuItem value="unauthorized_access">Truy cập trái phép</MenuItem>
            <MenuItem value="low_fuel">Nhiên liệu thấp</MenuItem>
            <MenuItem value="route_deviation">Lệch tuyến đường</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth margin="normal">
          <InputLabel>Mức độ nghiêm trọng</InputLabel>
          <Select
            value={formData.severity}
            onChange={(e) => setFormData({
              ...formData,
              severity: e.target.value as AlertRule['severity']
            })}
          >
            <MenuItem value="low">Thấp</MenuItem>
            <MenuItem value="medium">Trung bình</MenuItem>
            <MenuItem value="high">Cao</MenuItem>
            <MenuItem value="critical">Nghiêm trọng</MenuItem>
          </Select>
        </FormControl>

        {renderConditionFields()}

        <FormControlLabel
          control={
            <Switch
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
            />
          }
          label="Kích hoạt quy tắc"
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>
          Hủy
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !formData.name.trim()}
        >
          {loading ? <CircularProgress size={20} /> : (rule ? 'Cập nhật' : 'Thêm')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AlertRules;
