// Alert System Types

export interface Alert {
  id: string;
  type: 'geofence' | 'speed_limit' | 'engine_fault' | 'maintenance' | 'unauthorized_access' | 'low_fuel' | 'route_deviation';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  vehicle_id: string;
  vehicle_license_plate?: string;
  location?: {
    lat: number;
    lng: number;
    address?: string;
  };
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
  metadata?: {
    speed?: number;
    speed_limit?: number;
    geofence_name?: string;
    route_id?: string;
    [key: string]: any;
  };
}

export interface AlertRule {
  id: string;
  name: string;
  type: Alert['type'];
  enabled: boolean;
  severity: Alert['severity'];
  conditions: {
    speed_limit?: number;
    geofence_ids?: string[];
    time_ranges?: Array<{
      start: string;
      end: string;
      days: number[];
    }>;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}

export interface AlertStats {
  total: number;
  unacknowledged: number;
  unresolved: number;
  by_severity: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  by_type: {
    [key in Alert['type']]: number;
  };
}

export interface AlertFilter {
  severity?: Alert['severity'][];
  type?: Alert['type'][];
  vehicle_id?: string[];
  acknowledged?: boolean;
  resolved?: boolean;
  start_date?: string;
  end_date?: string;
}
