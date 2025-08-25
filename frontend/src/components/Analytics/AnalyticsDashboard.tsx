import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert as MuiAlert
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  TrendingUp as TrendingUpIcon,
  DirectionsCar as CarIcon,
  LocalGasStation as FuelIcon,
  Speed as SpeedIcon,
  Warning as AlertIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

import { analyticsService, AnalyticsData, TimeSeriesData, DateRange } from '../../services/analyticsService.ts';

const AnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<DateRange>({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  const [timeSeriesMetric, setTimeSeriesMetric] = useState<'distance' | 'fuel' | 'alerts' | 'vehicles'>('distance');

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  useEffect(() => {
    fetchTimeSeriesData();
  }, [timeSeriesMetric, dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsService.getAnalyticsData(dateRange);
      setAnalyticsData(data);
    } catch (err) {
      setError('Không thể tải dữ liệu phân tích');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTimeSeriesData = async () => {
    try {
      const data = await analyticsService.getTimeSeriesData(timeSeriesMetric, 'day', dateRange);
      setTimeSeriesData(data);
    } catch (err) {
      console.error('Error fetching time series data:', err);
    }
  };

  const handleDownloadReport = async (reportType: 'fleet_summary' | 'vehicle_performance' | 'fuel_analysis' | 'alert_summary') => {
    try {
      const blob = await analyticsService.generateReport(reportType, dateRange);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Không thể tạo báo cáo');
      console.error('Error generating report:', err);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  if (loading && !analyticsData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!analyticsData) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="textSecondary">
          Không có dữ liệu phân tích
        </Typography>
      </Box>
    );
  }

  const pieChartData = [
    { name: 'Hoạt động', value: analyticsData.fleet_overview.active_vehicles, color: '#4caf50' },
    { name: 'Nghỉ', value: analyticsData.fleet_overview.idle_vehicles, color: '#ff9800' },
    { name: 'Offline', value: analyticsData.fleet_overview.offline_vehicles, color: '#f44336' },
  ];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Analytics Dashboard
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Từ ngày</InputLabel>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({
                ...dateRange,
                start_date: e.target.value
              })}
              style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            />
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Đến ngày</InputLabel>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({
                ...dateRange,
                end_date: e.target.value
              })}
              style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            />
          </FormControl>
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

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Tổng số xe
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData.fleet_overview.total_vehicles}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    {analyticsData.fleet_overview.active_vehicles} đang hoạt động
                  </Typography>
                </Box>
                <CarIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Quãng đường hôm nay
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData.distance_analytics.total_distance_today.toFixed(1)} km
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    TB: {analyticsData.distance_analytics.average_distance_per_vehicle.toFixed(1)} km/xe
                  </Typography>
                </Box>
                <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Chi phí nhiên liệu
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(analyticsData.fuel_analytics.fuel_cost_today)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    TB: {analyticsData.fuel_analytics.average_fuel_efficiency.toFixed(1)} L/100km
                  </Typography>
                </Box>
                <FuelIcon sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Cảnh báo hôm nay
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData.alerts_summary.total_alerts_today}
                  </Typography>
                  <Typography variant="body2" color="error.main">
                    {analyticsData.alerts_summary.critical_alerts} nghiêm trọng
                  </Typography>
                </Box>
                <AlertIcon sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} mb={4}>
        {/* Time Series Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Xu hướng theo thời gian
                </Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Chỉ số</InputLabel>
                  <Select
                    value={timeSeriesMetric}
                    onChange={(e) => setTimeSeriesMetric(e.target.value as any)}
                  >
                    <MenuItem value="distance">Quãng đường</MenuItem>
                    <MenuItem value="fuel">Nhiên liệu</MenuItem>
                    <MenuItem value="vehicles">Số xe hoạt động</MenuItem>
                    <MenuItem value="alerts">Cảnh báo</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                    />
                    <YAxis />
                    <RechartsTooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString('vi-VN')}
                    />
                    <Line 
                      type="monotone" 
                      dataKey={
                        timeSeriesMetric === 'distance' ? 'total_distance' :
                        timeSeriesMetric === 'fuel' ? 'fuel_consumed' :
                        timeSeriesMetric === 'vehicles' ? 'vehicles_active' :
                        'alerts_count'
                      }
                      stroke="#1976d2" 
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Fleet Status Pie Chart */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trạng thái đội xe
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Tables */}
      <Grid container spacing={3} mb={4}>
        {/* Top Performing Vehicles */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Xe hoạt động tốt nhất
                </Typography>
                <Button
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadReport('vehicle_performance')}
                >
                  Xuất báo cáo
                </Button>
              </Box>
              <Box>
                {analyticsData.top_performing_vehicles.map((vehicle, index) => (
                  <Box key={vehicle.vehicle_id} mb={2} p={2} border={1} borderColor="grey.300" borderRadius={1}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">
                          #{index + 1} {vehicle.license_plate}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Quãng đường: {vehicle.distance_covered.toFixed(1)} km
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Hiệu suất nhiên liệu: {vehicle.fuel_efficiency.toFixed(1)} L/100km
                        </Typography>
                      </Box>
                      <Box textAlign="center">
                        <Typography variant="h6" color="success.main">
                          {vehicle.uptime_percentage.toFixed(1)}%
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Thời gian hoạt động
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Route Efficiency */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Hiệu quả tuyến đường
              </Typography>
              <Box>
                {analyticsData.route_efficiency.map((route, index) => (
                  <Box key={index} mb={2} p={2} border={1} borderColor="grey.300" borderRadius={1}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {route.route_name}
                    </Typography>
                    <Grid container spacing={2} mt={1}>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="textSecondary">
                          Thời gian TB
                        </Typography>
                        <Typography variant="body1">
                          {route.average_time.toFixed(1)} phút
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="textSecondary">
                          Quãng đường
                        </Typography>
                        <Typography variant="body1">
                          {route.distance.toFixed(1)} km
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="textSecondary">
                          Điểm hiệu quả
                        </Typography>
                        <Typography variant="body1" color="success.main">
                          {route.efficiency_score.toFixed(1)}/10
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Report Generation */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Tạo báo cáo
          </Typography>
          <Grid container spacing={2}>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownloadReport('fleet_summary')}
              >
                Báo cáo tổng quan đội xe
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownloadReport('fuel_analysis')}
              >
                Phân tích nhiên liệu
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownloadReport('alert_summary')}
              >
                Tóm tắt cảnh báo
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalyticsDashboard;
