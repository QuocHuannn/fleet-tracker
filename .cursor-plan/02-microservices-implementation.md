# Fleet Tracker - Kế hoạch triển khai Microservices

## 1. Chiến lược triển khai

### 1.1 Nguyên tắc thiết kế Microservices

- **Single Responsibility**: Mỗi service chịu trách nhiệm cho một domain cụ thể
- **Database per Service**: Mỗi service có database riêng
- **API Gateway Pattern**: Tập trung request routing và authentication
- **Event-Driven Communication**: Sử dụng message broker cho async communication
- **Independent Deployment**: Mỗi service có CI/CD pipeline riêng
- **Domain-Driven Design**: Thiết kế dựa trên business domains
- **Smart Endpoints, Dumb Pipes**: Logic xử lý nằm trong services, không ở message layer

### 1.2 Service Boundaries

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│                 │     │              │     │                  │
│   API Gateway   │────▶│ Auth Service │     │ Vehicle Service  │
│                 │     │              │     │                  │
└────────┬────────┘     └──────────────┘     └──────────────────┘
         │                                               ▲
         │                                               │
         │                                               │
         ▼                                               │
┌─────────────────┐                            ┌─────────┴────────┐
│                 │                            │                  │
│ Location Service│◀───────────────────────────│ Notification Svc │
│                 │                            │                  │
└─────────────────┘                            └──────────────────┘
```

## 2. Microservices Implementation

### 2.1 Phase 1: API Gateway & Auth Service (Tuần 1-2) - ✅ COMPLETED

#### API Gateway
- **Tech Stack**: FastAPI, httpx, Redis
- **Responsibilities**:
  - Request routing đến các services
  - Authentication & authorization
  - Rate limiting
  - Request/Response logging
  - Service discovery

```python
# API Gateway code structure
services/api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI setup
│   ├── config.py            # Gateway config
│   ├── middleware/          # Rate limiting, logging
│   ├── auth.py              # Auth middleware
│   └── routes/              # Service routes
├── Dockerfile
└── requirements.txt
```

#### Auth Service
- **Tech Stack**: FastAPI, PostgreSQL, Firebase Admin SDK
- **Responsibilities**:
  - User authentication & management
  - JWT token generation & validation
  - Role-based permissions
  - User session management

```python
# Auth Service code structure
services/auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI setup
│   ├── config.py            # Auth config
│   ├── models.py            # Data models
│   ├── database.py          # Database connection
│   └── routes/              # API endpoints
├── migrations/              # Database migrations
├── Dockerfile
└── requirements.txt
```

### 2.2 Phase 2: Vehicle & Location Services (Tuần 3-4) - ✅ COMPLETED

#### Vehicle Service
- **Tech Stack**: FastAPI, PostgreSQL
- **Responsibilities**:
  - Vehicle CRUD operations
  - Device registration & management
  - Vehicle status updates
  - Fleet management

```python
# Vehicle Service code structure
services/vehicle-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI setup
│   ├── config.py            # Vehicle service config
│   ├── models.py            # Vehicle models
│   ├── database.py          # Database connection
│   └── routes/              # Vehicle APIs
├── migrations/              # Database migrations
├── Dockerfile
└── requirements.txt
```

#### Location Service
- **Tech Stack**: FastAPI, PostgreSQL + PostGIS, MQTT client
- **Responsibilities**:
  - GPS data processing
  - Spatial queries & geofencing
  - Location history & tracking
  - MQTT message consumption

```python
# Location Service code structure
services/location-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI setup
│   ├── config.py            # Location service config
│   ├── models.py            # Spatial models
│   ├── database.py          # PostGIS connection
│   ├── mqtt/                # MQTT client & handlers
│   ├── services/            # Location processing
│   └── routes/              # Location APIs
├── migrations/              # Database migrations
├── Dockerfile
└── requirements.txt
```

### 2.3 Phase 3: Notification Service & Integration (Tuần 5-6)

#### Notification Service
- **Tech Stack**: FastAPI, PostgreSQL, WebSockets, Redis
- **Responsibilities**:
  - Real-time notifications via WebSocket
  - Alert rules management
  - Alert history storage
  - Email/SMS notifications

```python
# Notification Service code structure
services/notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI setup
│   ├── config.py            # Notification config
│   ├── models.py            # Alert models
│   ├── database.py          # Database connection
│   ├── websocket/           # WebSocket handlers
│   └── routes/              # Alert APIs
├── migrations/              # Database migrations
├── Dockerfile
└── requirements.txt
```

#### Event-Driven Communication
- **Tech Stack**: Redis Pub/Sub (hoặc RabbitMQ)
- **Responsibilities**:
  - Async communication giữa services
  - Event serialization & deserialization
  - Event routing

```python
# Event system code structure
shared/events/
├── __init__.py
├── base_event.py            # Base event class
├── vehicle_events.py        # Vehicle-related events
├── location_events.py       # Location-related events
└── notification_events.py   # Alert-related events
```

## 3. Frontend Implementation (Tuần 7-9)

### 3.1 Frontend Structure
- **Tech Stack**: React, TypeScript, Material-UI, Mapbox/Leaflet

```typescript
// Frontend structure
frontend/
├── src/
│   ├── components/          # Reusable components
│   ├── pages/               # Page components
│   ├── contexts/            # React contexts
│   ├── hooks/               # Custom hooks
│   ├── services/            # API clients
│   │   ├── authService.ts   # Auth API client
│   │   ├── vehicleService.ts# Vehicle API client
│   │   ├── locationService.ts# Location API client
│   │   └── alertService.ts  # Alert API client
│   ├── utils/               # Helper utilities
│   └── types/               # TypeScript definitions
├── package.json
└── Dockerfile
```

### 3.2 API Clients
Mỗi service sẽ có client riêng:

```typescript
// authService.ts
export class AuthService {
  login(credentials: LoginCredentials): Promise<User>;
  refreshToken(token: string): Promise<TokenResponse>;
  logout(): Promise<void>;
}

// vehicleService.ts
export class VehicleService {
  getVehicles(filters?: VehicleFilters): Promise<Vehicle[]>;
  getVehicle(id: string): Promise<Vehicle>;
  createVehicle(data: VehicleCreate): Promise<Vehicle>;
  updateVehicle(id: string, data: VehicleUpdate): Promise<Vehicle>;
}

// locationService.ts
export class LocationService {
  getCurrentLocation(vehicleId: string): Promise<Location>;
  getLocationHistory(vehicleId: string, timeRange: TimeRange): Promise<Location[]>;
  getGeofences(): Promise<Geofence[]>;
}
```

### 3.3 WebSocket Client
```typescript
// websocketService.ts
export class WebSocketService {
  connect(token: string): void;
  subscribeToVehicleUpdates(vehicleIds: string[]): void;
  subscribeToAlerts(): void;
  onLocationUpdate(callback: (data: LocationUpdate) => void): void;
  onAlert(callback: (data: Alert) => void): void;
  disconnect(): void;
}
```

### 3.4 Frontend Implementation Status (August 2024)

#### **✅ COMPLETED FRONTEND COMPONENTS:**

##### **Authentication System**
```typescript
// AuthContext.tsx - Context-based authentication
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  const login = async (email: string, password: string) => {
    const { user: userData, token } = await authService.login({ email, password });
    setUser(userData);
    localStorage.setItem('authToken', token);
  };
  
  const logout = () => {
    setUser(null);
    localStorage.removeItem('authToken');
  };
};
```

##### **Vehicle Management System**
```typescript
// VehicleList.tsx - Complete CRUD operations
const VehicleList: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [formOpen, setFormOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  
  // CRUD operations with forms and modals
  const handleAddVehicle = () => setFormOpen(true);
  const handleEditVehicle = (vehicle: Vehicle) => setSelectedVehicle(vehicle);
  const handleViewDetails = (vehicle: Vehicle) => setDetailsOpen(true);
};
```

##### **Live Map Integration**
```typescript
// LiveMap.tsx - Mapbox GL JS integration
const LiveMap: React.FC = () => {
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<{ [key: string]: mapboxgl.Marker }>({});
  
  // Real-time vehicle markers with WebSocket updates
  useEffect(() => {
    websocketService.on('location_update', handleLocationUpdate);
    websocketService.on('alert', handleAlert);
  }, []);
};
```

##### **WebSocket Service**
```typescript
// websocketService.ts - Real-time communication
class WebSocketService {
  private ws: WebSocket | null = null;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();
  
  public on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }
  
  public subscribeToVehicle(vehicleId: string) {
    this.sendMessage({
      type: 'subscribe',
      data: { subscription_type: `vehicle_${vehicleId}` }
    });
  }
}
```

#### **⚠️ PENDING FRONTEND COMPONENTS:**
- **Alert System UI**: Real-time alert notifications and management
- **Dashboard Analytics**: Advanced charts and performance metrics
- **End-to-End Testing**: Comprehensive testing suite

## 4. Infrastructure Setup (Tuần 10-11) - ✅ COMPLETED

### 4.1 Database Initialization

#### Auth Database
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Vehicle Database
```sql
CREATE TABLE vehicles (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    imei VARCHAR(50) UNIQUE,
    sim_card VARCHAR(50),
    last_heartbeat TIMESTAMP WITH TIME ZONE
);
```

#### Location Database
```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE locations (
    id UUID PRIMARY KEY,
    vehicle_id UUID NOT NULL,
    position GEOMETRY(Point, 4326) NOT NULL,
    speed DECIMAL(5,2),
    heading INTEGER,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE geofences (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    type VARCHAR(20) DEFAULT 'inclusion',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_vehicle_time ON locations(vehicle_id, recorded_at);
CREATE INDEX idx_locations_position ON locations USING GIST(position);
CREATE INDEX idx_geofences_boundary ON geofences USING GIST(boundary);
```

#### Notification Database
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    vehicle_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_rules (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    condition JSONB NOT NULL,
    action JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 MQTT Configuration

```conf
# MQTT Broker Configuration (mosquitto.conf)
listener 1883
protocol mqtt

listener 8883
protocol mqtt
certfile /mosquitto/ssl/server.crt
keyfile /mosquitto/ssl/server.key
require_certificate false

persistence true
persistence_location /mosquitto/data/

# Authentication
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl
allow_anonymous false
```

### 4.3 Message Topics

```
fleet/vehicles/{vehicle_id}/location
fleet/vehicles/{vehicle_id}/status
fleet/vehicles/{vehicle_id}/alert
fleet/system/broadcast
```

## 5. Development & Deployment Tools

### 5.1 Docker Compose Development Setup

```yaml
# docker-compose.yml (condensed)
version: '3.8'

services:
  # API Gateway
  api-gateway:
    build: ./services/api-gateway
    ports: ["8000:8000"]
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8001
      - VEHICLE_SERVICE_URL=http://vehicle-service:8002
      # ...other settings

  # Auth Service
  auth-service:
    build: ./services/auth-service
    ports: ["8001:8001"]
    environment:
      - DATABASE_URL=postgresql://auth_user:password@auth-db:5432/auth_db
      # ...other settings
    depends_on: [auth-db]

  # Vehicle Service  
  vehicle-service:
    build: ./services/vehicle-service
    ports: ["8002:8002"]
    environment:
      - DATABASE_URL=postgresql://vehicle_user:password@vehicle-db:5432/vehicle_db
      # ...other settings
    depends_on: [vehicle-db]

  # Location Service
  location-service:
    build: ./services/location-service
    ports: ["8003:8003"]
    environment:
      - DATABASE_URL=postgresql://location_user:password@location-db:5432/location_db
      - MQTT_BROKER_URL=mqtt://mosquitto:1883
      # ...other settings
    depends_on: [location-db, mosquitto]

  # Notification Service
  notification-service:
    build: ./services/notification-service
    ports: ["8004:8004"]
    environment:
      - DATABASE_URL=postgresql://notification_user:password@notification-db:5432/notification_db
      # ...other settings
    depends_on: [notification-db]

  # Databases
  auth-db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: auth_user
      POSTGRES_PASSWORD: password

  vehicle-db:
    image: postgres:15
    # ...similar config

  location-db:
    image: postgis/postgis:15-master
    # ...similar config

  notification-db:
    image: postgres:15
    # ...similar config

  # Shared Infrastructure
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  mosquitto:
    image: eclipse-mosquitto:2
    ports: ["1883:1883", "9001:9001"]
    volumes: ["./infrastructure/mqtt-broker:/mosquitto/config"]
```

### 5.2 Testing Strategy

#### Service-Specific Tests
- **Unit Tests**: Test individual components
- **Integration Tests**: Test service internals with DB/Redis
- **API Tests**: Test HTTP endpoints với mocked services

#### Cross-Service Tests
- **Contract Tests**: Verify service interactions
- **End-to-End Tests**: Test full user flows
- **Performance Tests**: Measure service latency
- **Fault Injection**: Test resilience patterns

## 6. Timeline & Milestones

### Sprint 1: Foundation (Week 1-2)
- Project setup & infrastructure
- API Gateway skeleton
- Auth Service implementation
- Docker Compose configuration

### Sprint 2: Core Services (Week 3-4)
- Vehicle Service implementation
- Location Service implementation
- MQTT integration
- Initial API Gateway integration

### Sprint 3: Notifications & Frontend Base (Week 5-6)
- Notification Service implementation
- WebSocket integration
- Frontend authentication
- Initial UI components

### Sprint 4: Frontend Integration (Week 7-8)
- Map integration
- Real-time location tracking
- Vehicle management UI
- Alert management UI

### Sprint 5: Testing & Optimization (Week 9-10)
- End-to-end testing
- Performance optimization
- Security hardening
- Bug fixes

### Sprint 6: Deployment & Production (Week 11-12)
- CI/CD pipeline setup
- Monitoring & logging implementation
- Production environment setup
- Documentation & handover

## 7. Success Metrics

- **Functional Requirements**:
  - All services working independently
  - Complete service-to-service communication
  - Successful end-to-end user flows

- **Performance Metrics**:
  - Service latency < 200ms (95th percentile)
  - WebSocket latency < 100ms
  - Support 500+ concurrent vehicles

- **Technical Metrics**:
  - 90%+ test coverage
  - Zero critical vulnerabilities
  - All services independently scalable
