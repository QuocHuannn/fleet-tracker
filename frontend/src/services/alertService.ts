// Alert Service
// Manages alert data and API communication

import { Alert, AlertRule, AlertStats, AlertFilter } from '../types/alert.ts';
import { config } from '../config/environment.ts';

class AlertService {
  private baseURL = config.API_URL;

  // Get alerts with filtering and pagination
  async getAlerts(
    filter?: AlertFilter,
    page: number = 1,
    limit: number = 20
  ): Promise<{
    alerts: Alert[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  }> {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...this.buildFilterParams(filter)
      });

      const response = await fetch(`${this.baseURL}/api/alerts?${params}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching alerts:', error);
      // Return mock data for development
      return this.getMockAlerts(filter, page, limit);
    }
  }

  // Get alert statistics
  async getAlertStats(filter?: AlertFilter): Promise<AlertStats> {
    try {
      const params = new URLSearchParams(this.buildFilterParams(filter));
      
      const response = await fetch(`${this.baseURL}/api/alerts/stats?${params}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch alert stats: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching alert stats:', error);
      // Return mock data for development
      return this.getMockAlertStats();
    }
  }

  // Acknowledge an alert
  async acknowledgeAlert(alertId: string): Promise<Alert> {
    try {
      const response = await fetch(`${this.baseURL}/api/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to acknowledge alert: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      throw error;
    }
  }

  // Resolve an alert
  async resolveAlert(alertId: string): Promise<Alert> {
    try {
      const response = await fetch(`${this.baseURL}/api/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to resolve alert: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error resolving alert:', error);
      throw error;
    }
  }

  // Get alert rules
  async getAlertRules(): Promise<AlertRule[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/alert-rules`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch alert rules: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching alert rules:', error);
      return this.getMockAlertRules();
    }
  }

  // Create alert rule
  async createAlertRule(rule: Omit<AlertRule, 'id' | 'created_at' | 'updated_at'>): Promise<AlertRule> {
    try {
      const response = await fetch(`${this.baseURL}/api/alert-rules`, {
        method: 'POST',
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(rule),
      });

      if (!response.ok) {
        throw new Error(`Failed to create alert rule: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating alert rule:', error);
      throw error;
    }
  }

  // Update alert rule
  async updateAlertRule(ruleId: string, rule: Partial<AlertRule>): Promise<AlertRule> {
    try {
      const response = await fetch(`${this.baseURL}/api/alert-rules/${ruleId}`, {
        method: 'PUT',
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(rule),
      });

      if (!response.ok) {
        throw new Error(`Failed to update alert rule: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating alert rule:', error);
      throw error;
    }
  }

  // Delete alert rule
  async deleteAlertRule(ruleId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/alert-rules/${ruleId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to delete alert rule: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting alert rule:', error);
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

  private buildFilterParams(filter?: AlertFilter): Record<string, string> {
    if (!filter) return {};

    const params: Record<string, string> = {};

    if (filter.severity) {
      params.severity = filter.severity.join(',');
    }
    if (filter.type) {
      params.type = filter.type.join(',');
    }
    if (filter.vehicle_id) {
      params.vehicle_id = filter.vehicle_id.join(',');
    }
    if (filter.acknowledged !== undefined) {
      params.acknowledged = filter.acknowledged.toString();
    }
    if (filter.resolved !== undefined) {
      params.resolved = filter.resolved.toString();
    }
    if (filter.start_date) {
      params.start_date = filter.start_date;
    }
    if (filter.end_date) {
      params.end_date = filter.end_date;
    }

    return params;
  }

  // Mock data for development
  private getMockAlerts(filter?: AlertFilter, page: number = 1, limit: number = 20) {
    const mockAlerts: Alert[] = [
      {
        id: '1',
        type: 'speed_limit',
        severity: 'high',
        title: 'Vượt tốc độ cho phép',
        message: 'Xe 29A-12345 đang chạy 85 km/h trong khu vực giới hạn 60 km/h',
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        vehicle_id: 'vh-001',
        vehicle_license_plate: '29A-12345',
        location: {
          lat: 10.7769,
          lng: 106.7009,
          address: 'Đường Nguyễn Huệ, Quận 1, TP.HCM'
        },
        acknowledged: false,
        resolved: false,
        metadata: {
          speed: 85,
          speed_limit: 60
        }
      },
      {
        id: '2',
        type: 'geofence',
        severity: 'medium',
        title: 'Ra khỏi vùng cho phép',
        message: 'Xe 30B-67890 đã rời khỏi vùng hoạt động được phân công',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        vehicle_id: 'vh-002',
        vehicle_license_plate: '30B-67890',
        location: {
          lat: 10.8231,
          lng: 106.6297,
          address: 'Đường Võ Văn Kiệt, Quận 5, TP.HCM'
        },
        acknowledged: true,
        acknowledged_by: 'admin',
        acknowledged_at: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
        resolved: false,
        metadata: {
          geofence_name: 'Khu vực trung tâm'
        }
      },
      {
        id: '3',
        type: 'engine_fault',
        severity: 'critical',
        title: 'Lỗi động cơ',
        message: 'Xe 31C-11111 báo lỗi động cơ nghiêm trọng, cần kiểm tra ngay lập tức',
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        vehicle_id: 'vh-003',
        vehicle_license_plate: '31C-11111',
        location: {
          lat: 10.7829,
          lng: 106.6963,
          address: 'Đường Lê Lợi, Quận 1, TP.HCM'
        },
        acknowledged: true,
        acknowledged_by: 'technician',
        acknowledged_at: new Date(Date.now() - 1000 * 60 * 50).toISOString(),
        resolved: true,
        resolved_by: 'technician',
        resolved_at: new Date(Date.now() - 1000 * 60 * 10).toISOString()
      },
      {
        id: '4',
        type: 'maintenance',
        severity: 'low',
        title: 'Bảo dưỡng định kỳ',
        message: 'Xe 32D-22222 sắp đến hạn bảo dưỡng định kỳ (còn 500km)',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        vehicle_id: 'vh-004',
        vehicle_license_plate: '32D-22222',
        acknowledged: false,
        resolved: false
      }
    ];

    // Apply filters
    let filteredAlerts = mockAlerts;
    if (filter) {
      if (filter.severity) {
        filteredAlerts = filteredAlerts.filter(alert => filter.severity!.includes(alert.severity));
      }
      if (filter.type) {
        filteredAlerts = filteredAlerts.filter(alert => filter.type!.includes(alert.type));
      }
      if (filter.acknowledged !== undefined) {
        filteredAlerts = filteredAlerts.filter(alert => alert.acknowledged === filter.acknowledged);
      }
      if (filter.resolved !== undefined) {
        filteredAlerts = filteredAlerts.filter(alert => alert.resolved === filter.resolved);
      }
    }

    const total = filteredAlerts.length;
    const start = (page - 1) * limit;
    const alerts = filteredAlerts.slice(start, start + limit);

    return {
      alerts,
      total,
      page,
      limit,
      total_pages: Math.ceil(total / limit)
    };
  }

  private getMockAlertStats(): AlertStats {
    return {
      total: 127,
      unacknowledged: 23,
      unresolved: 15,
      by_severity: {
        low: 45,
        medium: 52,
        high: 23,
        critical: 7
      },
      by_type: {
        geofence: 35,
        speed_limit: 28,
        engine_fault: 12,
        maintenance: 25,
        unauthorized_access: 8,
        low_fuel: 15,
        route_deviation: 4
      }
    };
  }

  private getMockAlertRules(): AlertRule[] {
    return [
      {
        id: 'rule-1',
        name: 'Giới hạn tốc độ trong thành phố',
        type: 'speed_limit',
        enabled: true,
        severity: 'high',
        conditions: {
          speed_limit: 60
        },
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
        updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString()
      },
      {
        id: 'rule-2',
        name: 'Vùng hoạt động cho phép',
        type: 'geofence',
        enabled: true,
        severity: 'medium',
        conditions: {
          geofence_ids: ['geo-1', 'geo-2', 'geo-3']
        },
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
        updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString()
      }
    ];
  }
}

export const alertService = new AlertService();
export * from '../types/alert.ts';
