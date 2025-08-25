# Fleet Tracker - Microservices Architecture Redesign

## 🏗️ True Microservices Architecture

### Kiến trúc tổng quan
```
                            ┌─────────────────┐
                            │   API Gateway   │
                            │    (Port 8000)  │
                            └─────────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
            ┌───────▼──────┐ ┌───────▼──────┐ ┌───────▼──────┐
            │ Auth Service │ │Vehicle Service│ │Location Service│
            │ (Port 8001)  │ │ (Port 8002)  │ │ (Port 8003)  │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │                 │                 │
            ┌───────▼──────┐          │         ┌───────▼──────┐
            │   User DB    │          │         │  Location DB │
            │ (PostgreSQL) │          │         │ (PostgreSQL  │
            └──────────────┘          │         │  + PostGIS)  │
                                      │         └──────────────┘
                              ┌───────▼──────┐
                              │  Vehicle DB  │         ┌─────────────────┐
                              │ (PostgreSQL) │         │Notification Svc │
                              └──────────────┘         │ (Port 8004)     │
                                                       └─────────────────┘
                                      │
                            ┌─────────▼──────────┐
                            │    Shared Layer    │
                            │ Redis + MQTT Broker │
                            └────────────────────┘
```

## 🎯 Microservices Definition

### 1. API Gateway Service (Port 8000)
**Responsibility**: Request routing, authentication, rate limiting
- **Technology**: FastAPI + HTTP Reverse Proxy
- **Functions**:
  - Route requests to appropriate services
  - Aggregate responses từ multiple services
  - Authentication token validation
  - Rate limiting và request throttling
  - Request/Response logging
  - Load balancing
  - CORS handling

### 2. Auth Service (Port 8001) 
**Responsibility**: User authentication & authorization
- **Database**: PostgreSQL (`auth_db`)
- **Functions**:
  - Firebase token validation
  - JWT token generation/validation
  - User profile management
  - Role-based permissions (RBAC)
  - Session management
  - Password reset workflows

**Data Models**:
```python
User: id, firebase_uid, email, role, permissions, created_at
UserSession: user_id, token, expires_at, device_info
Role: id, name, permissions
Permission: id, resource, action
```

### 3. Vehicle Service (Port 8002)
**Responsibility**: Vehicle management và metadata
- **Database**: PostgreSQL (`vehicle_db`)  
- **Functions**:
  - Vehicle CRUD operations
  - Vehicle status management
  - Device registration/management
  - Vehicle categorization
  - Maintenance scheduling
  - Vehicle assignments

**Data Models**:
```python
Vehicle: id, name, license_plate, device_id, type, status, owner_id
Device: id, vehicle_id, imei, sim_card, last_heartbeat
VehicleAssignment: vehicle_id, user_id, assigned_at, role
MaintenanceRecord: vehicle_id, type, date, cost, notes
```

### 4. Location Service (Port 8003)
**Responsibility**: GPS data processing & spatial operations
- **Database**: PostgreSQL + PostGIS (`location_db`)
- **Functions**:
  - MQTT GPS data consumption
  - Real-time location processing
  - Location history storage
  - Spatial queries (geofencing)
  - Speed calculations
  - Trip detection và analysis
  - Location-based alerts

**Data Models**:
```python
Location: id, vehicle_id, position, speed, heading, timestamp
CurrentLocation: vehicle_id, position, speed, last_update, is_online
Geofence: id, name, boundary, type, created_by
GeofenceViolation: id, vehicle_id, geofence_id, violation_type, timestamp
Trip: id, vehicle_id, start_location, end_location, start_time, end_time
```

### 5. Notification Service (Port 8004)
**Responsibility**: Alerts, notifications & communications
- **Database**: PostgreSQL (`notification_db`)
- **Functions**:
  - Real-time alert generation
  - WebSocket connections management
  - Email/SMS notifications
  - Push notifications
  - Alert rules management
  - Notification templates
  - Communication history

**Data Models**:
```python
Alert: id, vehicle_id, type, severity, message, created_at, resolved_at
NotificationRule: id, user_id, alert_type, channels, conditions
NotificationChannel: id, type, config, is_active
NotificationHistory: id, alert_id, channel, status, sent_at
WebSocketConnection: id, user_id, connection_id, created_at
```

## 🔗 Service Communication Patterns

### 1. Synchronous Communication (HTTP REST)
- **API Gateway ↔ All Services**: Request routing
- **Vehicle Service ↔ Auth Service**: User validation
- **Location Service ↔ Vehicle Service**: Vehicle existence check
- **Notification Service ↔ All Services**: Alert context gathering

### 2. Asynchronous Communication (Events)
- **Message Queue**: Redis Pub/Sub hoặc RabbitMQ
- **Event Types**:
  - `vehicle.created`
  - `vehicle.status.changed`
  - `location.updated`
  - `geofence.violated`
  - `trip.started`
  - `trip.completed`

### 3. Real-time Communication
- **MQTT**: GPS device → Location Service
- **WebSocket**: Notification Service → Frontend clients
- **Server-Sent Events**: Real-time updates

## 📁 Project Structure Redesign

```
fleet-tracker/
├── services/
│   ├── api-gateway/           # Kong, Zuul, hoặc FastAPI Gateway
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── auth-service/          # Authentication & Authorization
│   │   ├── app/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── vehicle-service/       # Vehicle Management
│   │   ├── app/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── location-service/      # GPS & Spatial Operations
│   │   ├── app/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── notification-service/  # Alerts & Communications
│       ├── app/
│       ├── migrations/
│       ├── Dockerfile
│       └── requirements.txt
├── frontend/                  # React Frontend (unchanged)
├── shared/                    # Shared libraries & utils
│   ├── common/               # Common utilities
│   ├── events/               # Event schemas
│   └── proto/                # Protocol buffers (if using gRPC)
├── infrastructure/
│   ├── databases/            # Database initialization scripts
│   ├── monitoring/           # Prometheus, Grafana configs
│   ├── mqtt-broker/          # MQTT broker configuration
│   └── message-queue/        # Redis/RabbitMQ configuration
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
└── k8s/                      # Kubernetes manifests (future)
    ├── deployments/
    ├── services/
    └── ingress/
```

## 🐳 Docker Configuration

### Development Docker Compose
```yaml
version: '3.8'

services:
  # API Gateway
  api-gateway:
    build: ./services/api-gateway
    ports: ["8000:8000"]
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8001
      - VEHICLE_SERVICE_URL=http://vehicle-service:8002
      - LOCATION_SERVICE_URL=http://location-service:8003
      - NOTIFICATION_SERVICE_URL=http://notification-service:8004
    depends_on: [auth-service, vehicle-service, location-service, notification-service]

  # Microservices
  auth-service:
    build: ./services/auth-service
    ports: ["8001:8001"]
    environment:
      - DATABASE_URL=postgresql://auth_user:password@auth-db:5432/auth_db
      - REDIS_URL=redis://redis:6379
    depends_on: [auth-db, redis]

  vehicle-service:
    build: ./services/vehicle-service  
    ports: ["8002:8002"]
    environment:
      - DATABASE_URL=postgresql://vehicle_user:password@vehicle-db:5432/vehicle_db
      - AUTH_SERVICE_URL=http://auth-service:8001
    depends_on: [vehicle-db, auth-service]

  location-service:
    build: ./services/location-service
    ports: ["8003:8003"] 
    environment:
      - DATABASE_URL=postgresql://location_user:password@location-db:5432/location_db
      - MQTT_BROKER_URL=mqtt://mosquitto:1883
      - REDIS_URL=redis://redis:6379
    depends_on: [location-db, mosquitto, redis]

  notification-service:
    build: ./services/notification-service
    ports: ["8004:8004"]
    environment:
      - DATABASE_URL=postgresql://notification_user:password@notification-db:5432/notification_db
      - REDIS_URL=redis://redis:6379
    depends_on: [notification-db, redis]

  # Databases
  auth-db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: auth_user
      POSTGRES_PASSWORD: password

  vehicle-db:
    image: postgres:15
    environment:
      POSTGRES_DB: vehicle_db
      POSTGRES_USER: vehicle_user  
      POSTGRES_PASSWORD: password

  location-db:
    image: postgis/postgis:15-master
    environment:
      POSTGRES_DB: location_db
      POSTGRES_USER: location_user
      POSTGRES_PASSWORD: password

  notification-db:
    image: postgres:15
    environment:
      POSTGRES_DB: notification_db
      POSTGRES_USER: notification_user
      POSTGRES_PASSWORD: password

  # Shared Infrastructure
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  mosquitto:
    image: eclipse-mosquitto:2
    ports: ["1883:1883", "9001:9001"]
    volumes: ["./infrastructure/mqtt-broker:/mosquitto/config"]

  # Frontend  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

## 🔧 Technology Decisions

### Service Communication
- **REST APIs**: Primary service-to-service communication
- **gRPC**: High-performance internal communication (optional)
- **Event Streaming**: Redis Pub/Sub cho async messaging
- **Message Queue**: RabbitMQ for reliable messaging (future)

### Data Management
- **Database per Service**: PostgreSQL instances
- **Shared Cache**: Redis for cross-service caching
- **Event Store**: For event sourcing (future enhancement)

### Security
- **JWT Tokens**: Service-to-service authentication
- **API Gateway**: Central authentication point
- **mTLS**: Service mesh security (production)
- **Secret Management**: Docker secrets/Kubernetes secrets

### Observability
- **Distributed Tracing**: Jaeger/Zipkin
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Health Checks**: Per-service health endpoints

## 🚀 Implementation Phases

### Phase 1: Core Services (2-3 tuần)
1. API Gateway setup
2. Auth Service implementation
3. Basic service-to-service communication

### Phase 2: Domain Services (3-4 tuần) 
1. Vehicle Service implementation
2. Location Service với MQTT integration
3. Database setup và migrations

### Phase 3: Advanced Features (2-3 tuần)
1. Notification Service
2. Event-driven architecture
3. WebSocket real-time updates

### Phase 4: Production Ready (2-3 tuần)
1. Monitoring và observability
2. Performance optimization
3. Security hardening
4. CI/CD pipeline

## 📊 Benefits của Microservices Architecture

### Technical Benefits
- **Scalability**: Independent scaling của từng service
- **Technology Diversity**: Different tech stacks per service
- **Fault Isolation**: Service failure không affect others
- **Development Speed**: Parallel development teams
- **Deployment Flexibility**: Independent deployment cycles

### Learning Benefits cho Boss
- **Distributed Systems**: Service discovery, load balancing
- **API Design**: RESTful services, gRPC, GraphQL
- **Data Management**: Database per service, event sourcing
- **DevOps Skills**: Container orchestration, monitoring
- **Architecture Patterns**: CQRS, Event Sourcing, Saga Pattern

Đây sẽ là excellent learning experience cho modern software architecture! 🎯
