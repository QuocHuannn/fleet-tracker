import { config } from '../config/environment.ts';

export interface AnalyticsData {
  fleet_overview: {
    total_vehicles: number;
    active_vehicles: number;
    idle_vehicles: number;
    offline_vehicles: number;
  };
  distance_analytics: {
    total_distance_today: number;
    total_distance_week: number;
    total_distance_month: number;
    average_distance_per_vehicle: number;
  };
  fuel_analytics: {
    total_fuel_consumed: number;
    average_fuel_efficiency: number;
    fuel_cost_today: number;
    fuel_cost_month: number;
  };
  performance_metrics: {
    average_speed: number;
    max_speed_recorded: number;
    total_driving_time: number;
    utilization_rate: number;
  };
  alerts_summary: {
    total_alerts_today: number;
    critical_alerts: number;
    resolved_alerts: number;
    pending_alerts: number;
  };
  top_performing_vehicles: Array<{
    vehicle_id: string;
    license_plate: string;
    distance_covered: number;
    fuel_efficiency: number;
    uptime_percentage: number;
  }>;
  route_efficiency: Array<{
    route_name: string;
    average_time: number;
    distance: number;
    efficiency_score: number;
  }>;
}

export interface TimeSeriesData {
  timestamp: string;
  vehicles_active: number;
  total_distance: number;
  fuel_consumed: number;
  alerts_count: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

class AnalyticsService {
  private baseURL = config.API_URL;

  // Get analytics data for dashboard
  async getAnalyticsData(dateRange?: DateRange): Promise<AnalyticsData> {
    try {
      const params = new URLSearchParams();
      if (dateRange) {
        params.append('start_date', dateRange.start_date);
        params.append('end_date', dateRange.end_date);
      }

      const response = await fetch(`${this.baseURL}/api/analytics?${params}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch analytics: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching analytics:', error);
      return this.getMockAnalyticsData();
    }
  }

  // Get time series data for charts
  async getTimeSeriesData(
    metric: 'distance' | 'fuel' | 'alerts' | 'vehicles',
    period: 'day' | 'week' | 'month',
    dateRange?: DateRange
  ): Promise<TimeSeriesData[]> {
    try {
      const params = new URLSearchParams({
        metric,
        period,
      });
      
      if (dateRange) {
        params.append('start_date', dateRange.start_date);
        params.append('end_date', dateRange.end_date);
      }

      const response = await fetch(`${this.baseURL}/api/analytics/timeseries?${params}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch time series data: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching time series data:', error);
      return this.getMockTimeSeriesData(metric, period);
    }
  }

  // Generate report
  async generateReport(
    reportType: 'fleet_summary' | 'vehicle_performance' | 'fuel_analysis' | 'alert_summary',
    dateRange: DateRange,
    format: 'pdf' | 'excel' = 'pdf'
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams({
        type: reportType,
        format,
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
      });

      const response = await fetch(`${this.baseURL}/api/analytics/report?${params}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }

  // Helper methods
  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  // Mock data for development
  private getMockAnalyticsData(): AnalyticsData {
    return {
      fleet_overview: {
        total_vehicles: 25,
        active_vehicles: 18,
        idle_vehicles: 5,
        offline_vehicles: 2,
      },
      distance_analytics: {
        total_distance_today: 2847.5,
        total_distance_week: 18925.3,
        total_distance_month: 75680.8,
        average_distance_per_vehicle: 113.9,
      },
      fuel_analytics: {
        total_fuel_consumed: 1247.8,
        average_fuel_efficiency: 8.2,
        fuel_cost_today: 2856000,
        fuel_cost_month: 89750000,
      },
      performance_metrics: {
        average_speed: 42.5,
        max_speed_recorded: 95.3,
        total_driving_time: 156.7,
        utilization_rate: 78.4,
      },
      alerts_summary: {
        total_alerts_today: 12,
        critical_alerts: 2,
        resolved_alerts: 8,
        pending_alerts: 4,
      },
      top_performing_vehicles: [
        {
          vehicle_id: 'vh-001',
          license_plate: '29A-12345',
          distance_covered: 285.7,
          fuel_efficiency: 9.2,
          uptime_percentage: 94.8,
        },
        {
          vehicle_id: 'vh-002',
          license_plate: '30B-67890',
          distance_covered: 267.3,
          fuel_efficiency: 8.9,
          uptime_percentage: 91.2,
        },
        {
          vehicle_id: 'vh-003',
          license_plate: '31C-11111',
          distance_covered: 245.1,
          fuel_efficiency: 8.5,
          uptime_percentage: 88.7,
        },
      ],
      route_efficiency: [
        {
          route_name: 'Tuyến trung tâm - Quận 1',
          average_time: 45.2,
          distance: 23.5,
          efficiency_score: 8.7,
        },
        {
          route_name: 'Tuyến vành đai - Quận 7',
          average_time: 52.8,
          distance: 31.2,
          efficiency_score: 7.9,
        },
        {
          route_name: 'Tuyến cảng - Quận 4',
          average_time: 38.7,
          distance: 18.9,
          efficiency_score: 9.1,
        },
      ],
    };
  }

  private getMockTimeSeriesData(
    metric: string,
    period: string
  ): TimeSeriesData[] {
    const now = new Date();
    const data: TimeSeriesData[] = [];
    
    const getRandomValue = (base: number, variance: number) => 
      base + (Math.random() - 0.5) * variance;

    for (let i = 0; i < 24; i++) {
      const timestamp = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
      
      data.push({
        timestamp: timestamp.toISOString(),
        vehicles_active: Math.floor(getRandomValue(18, 8)),
        total_distance: getRandomValue(120, 40),
        fuel_consumed: getRandomValue(50, 20),
        alerts_count: Math.floor(getRandomValue(2, 3)),
      });
    }

    return data;
  }
}

export const analyticsService = new AnalyticsService();
