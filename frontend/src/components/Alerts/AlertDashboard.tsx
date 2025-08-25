import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  IconButton,
  Chip,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  CircularProgress,
  Alert as MuiAlert,
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
  Checkbox,
  FormControlLabel
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  Notifications as NotificationsIcon,
  NotificationsOff as NotificationsOffIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Check as AcknowledgeIcon,
  Close as ResolveIcon
} from '@mui/icons-material';
// import { formatDistanceToNow } from 'date-fns';
// import { vi } from 'date-fns/locale';

import { Alert, AlertStats, AlertFilter, alertService } from '../../services/alertService';

const AlertDashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<AlertFilter>({});
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchData();
  }, [filter, page]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [alertsResponse, statsResponse] = await Promise.all([
        alertService.getAlerts(filter, page, 10),
        alertService.getAlertStats(filter)
      ]);

      setAlerts(alertsResponse.alerts);
      setTotalPages(alertsResponse.total_pages);
      setStats(statsResponse);
    } catch (err) {
      setError('Không thể tải dữ liệu cảnh báo');
      console.error('Error fetching alert data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await alertService.acknowledgeAlert(alertId);
      await fetchData();
    } catch (err) {
      setError('Không thể xác nhận cảnh báo');
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await alertService.resolveAlert(alertId);
      await fetchData();
    } catch (err) {
      setError('Không thể giải quyết cảnh báo');
      console.error('Error resolving alert:', err);
    }
  };

  const getSeverityIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon color="warning" />;
      case 'medium':
        return <InfoIcon color="info" />;
      case 'low':
        return <CheckIcon color="success" />;
      default:
        return <InfoIcon />;
    }
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

  const getTypeLabel = (type: Alert['type']) => {
    const labels = {
      geofence: 'Vùng địa lý',
      speed_limit: 'Tốc độ',
      engine_fault: 'Lỗi động cơ',
      maintenance: 'Bảo dưỡng',
      unauthorized_access: 'Truy cập trái phép',
      low_fuel: 'Nhiên liệu thấp',
      route_deviation: 'Lệch tuyến đường'
    };
    return labels[type] || type;
  };

  const handleFilterChange = (newFilter: AlertFilter) => {
    setFilter(newFilter);
    setPage(1);
    setFilterDialogOpen(false);
  };

  if (loading && alerts.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Hệ thống Cảnh báo
        </Typography>
        <Box>
          <Tooltip title="Bộ lọc">
            <IconButton onClick={() => setFilterDialogOpen(true)}>
              <FilterIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Làm mới">
            <IconButton onClick={fetchData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <MuiAlert severity="error" sx={{ mb: 2 }}>
          {error}
        </MuiAlert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Tổng cảnh báo
                </Typography>
                <Typography variant="h4">
                  {stats.total}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Chưa xác nhận
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {stats.unacknowledged}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Chưa giải quyết
                </Typography>
                <Typography variant="h4" color="error.main">
                  {stats.unresolved}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Nghiêm trọng
                </Typography>
                <Typography variant="h4" color="error.main">
                  {stats.by_severity.critical}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Alerts List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Danh sách Cảnh báo
          </Typography>
          
          {alerts.length === 0 ? (
            <Typography color="textSecondary" textAlign="center" py={4}>
              Không có cảnh báo nào
            </Typography>
          ) : (
            <List>
              {alerts.map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem alignItems="flex-start">
                    <Box display="flex" alignItems="flex-start" width="100%">
                      <Box mr={2} mt={0.5}>
                        {getSeverityIcon(alert.severity)}
                      </Box>
                      
                      <Box flex={1} minWidth={0}>
                        <Box display="flex" alignItems="center" mb={1}>
                          <Typography variant="subtitle1" component="div" sx={{ flex: 1 }}>
                            {alert.title}
                          </Typography>
                          <Box ml={2}>
                            <Chip
                              label={getTypeLabel(alert.type)}
                              size="small"
                              color={getSeverityColor(alert.severity) as any}
                              variant="outlined"
                              sx={{ mr: 1 }}
                            />
                            {alert.vehicle_license_plate && (
                              <Chip
                                label={alert.vehicle_license_plate}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                        
                        <Typography variant="body2" color="textSecondary" mb={1}>
                          {alert.message}
                        </Typography>
                        
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography variant="caption" color="textSecondary">
                              {new Date(alert.timestamp).toLocaleString('vi-VN')}
                            </Typography>
                            {alert.location?.address && (
                              <Typography variant="caption" color="textSecondary" display="block">
                                📍 {alert.location.address}
                              </Typography>
                            )}
                          </Box>
                          
                          <Box display="flex" gap={1}>
                            {alert.acknowledged && (
                              <Chip
                                label="Đã xác nhận"
                                size="small"
                                color="info"
                                variant="filled"
                              />
                            )}
                            {alert.resolved && (
                              <Chip
                                label="Đã giải quyết"
                                size="small"
                                color="success"
                                variant="filled"
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                      
                      <ListItemSecondaryAction>
                        <Box display="flex" flexDirection="column" gap={1}>
                          {!alert.acknowledged && (
                            <Tooltip title="Xác nhận">
                              <IconButton
                                size="small"
                                onClick={() => handleAcknowledge(alert.id)}
                                color="primary"
                              >
                                <AcknowledgeIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          {alert.acknowledged && !alert.resolved && (
                            <Tooltip title="Giải quyết">
                              <IconButton
                                size="small"
                                onClick={() => handleResolve(alert.id)}
                                color="success"
                              >
                                <ResolveIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </ListItemSecondaryAction>
                    </Box>
                  </ListItem>
                  {index < alerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={2}>
              <Button
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Trước
              </Button>
              <Typography sx={{ mx: 2, alignSelf: 'center' }}>
                Trang {page} / {totalPages}
              </Typography>
              <Button
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
              >
                Sau
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Filter Dialog */}
      <FilterDialog
        open={filterDialogOpen}
        onClose={() => setFilterDialogOpen(false)}
        filter={filter}
        onApply={handleFilterChange}
      />
    </Box>
  );
};

// Filter Dialog Component
interface FilterDialogProps {
  open: boolean;
  onClose: () => void;
  filter: AlertFilter;
  onApply: (filter: AlertFilter) => void;
}

const FilterDialog: React.FC<FilterDialogProps> = ({ open, onClose, filter, onApply }) => {
  const [localFilter, setLocalFilter] = useState<AlertFilter>(filter);

  const handleApply = () => {
    onApply(localFilter);
  };

  const handleReset = () => {
    setLocalFilter({});
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Bộ lọc Cảnh báo</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          {/* Severity Filter */}
          <FormControl fullWidth margin="normal">
            <InputLabel>Mức độ nghiêm trọng</InputLabel>
            <Select
              multiple
              value={localFilter.severity || []}
              onChange={(e) => setLocalFilter({
                ...localFilter,
                severity: e.target.value as Alert['severity'][]
              })}
              renderValue={(selected) => selected.join(', ')}
            >
              <MenuItem value="low">Thấp</MenuItem>
              <MenuItem value="medium">Trung bình</MenuItem>
              <MenuItem value="high">Cao</MenuItem>
              <MenuItem value="critical">Nghiêm trọng</MenuItem>
            </Select>
          </FormControl>

          {/* Type Filter */}
          <FormControl fullWidth margin="normal">
            <InputLabel>Loại cảnh báo</InputLabel>
            <Select
              multiple
              value={localFilter.type || []}
              onChange={(e) => setLocalFilter({
                ...localFilter,
                type: e.target.value as Alert['type'][]
              })}
              renderValue={(selected) => selected.join(', ')}
            >
              <MenuItem value="geofence">Vùng địa lý</MenuItem>
              <MenuItem value="speed_limit">Tốc độ</MenuItem>
              <MenuItem value="engine_fault">Lỗi động cơ</MenuItem>
              <MenuItem value="maintenance">Bảo dưỡng</MenuItem>
              <MenuItem value="unauthorized_access">Truy cập trái phép</MenuItem>
              <MenuItem value="low_fuel">Nhiên liệu thấp</MenuItem>
              <MenuItem value="route_deviation">Lệch tuyến đường</MenuItem>
            </Select>
          </FormControl>

          {/* Status Filters */}
          <Box mt={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={localFilter.acknowledged === false}
                  onChange={(e) => setLocalFilter({
                    ...localFilter,
                    acknowledged: e.target.checked ? false : undefined
                  })}
                />
              }
              label="Chỉ hiển thị chưa xác nhận"
            />
          </Box>

          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={localFilter.resolved === false}
                  onChange={(e) => setLocalFilter({
                    ...localFilter,
                    resolved: e.target.checked ? false : undefined
                  })}
                />
              }
              label="Chỉ hiển thị chưa giải quyết"
            />
          </Box>

          {/* Date Range */}
          <TextField
            fullWidth
            margin="normal"
            label="Từ ngày"
            type="date"
            value={localFilter.start_date || ''}
            onChange={(e) => setLocalFilter({
              ...localFilter,
              start_date: e.target.value || undefined
            })}
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            fullWidth
            margin="normal"
            label="Đến ngày"
            type="date"
            value={localFilter.end_date || ''}
            onChange={(e) => setLocalFilter({
              ...localFilter,
              end_date: e.target.value || undefined
            })}
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleReset}>
          Đặt lại
        </Button>
        <Button onClick={onClose}>
          Hủy
        </Button>
        <Button onClick={handleApply} variant="contained">
          Áp dụng
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AlertDashboard;
