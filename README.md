# 🚛 Fleet Tracker

Real-time GPS vehicle tracking system built with microservices architecture.

## 🎯 Project Status

### ✅ **COMPLETED (85%)**
- **Infrastructure**: 100% - Docker, databases, MQTT, Redis
- **Backend Services**: 85% - 4/5 services operational
- **API Gateway**: 100% - Routing & authentication
- **Database Models**: 90% - All core models implemented
- **Integration Tests**: 100% - All tests passing

### 🚧 **IN PROGRESS (15%)**
- **Frontend Development**: 30% - Basic components created
- **Notification Service**: 80% - Minor Pydantic issues
- **Real-time Features**: 20% - WebSocket setup in progress

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)

### 1. Start Backend Services
```bash
# Start all backend services
docker compose -f docker-compose.dev.yml up -d

# Check status
./scripts/test-integration.sh
```

### 2. Start Frontend Development
```bash
# Option 1: Using Docker (Recommended)
./scripts/dev-frontend.sh

# Option 2: Local development
cd frontend
npm install
npm start
```

### 3. Access Services
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │  Auth Service   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Vehicle Service │    │ Location Service│
                       │   (FastAPI)     │    │   (FastAPI)     │
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Notification    │    │   Databases     │
                       │   Service       │    │  (PostgreSQL)   │
                       └─────────────────┘    └─────────────────┘
```

## 📊 Service Status

| Service | Status | Port | Health |
|---------|--------|------|--------|
| API Gateway | ✅ Running | 8000 | Healthy |
| Auth Service | ✅ Running | 8001 | Healthy |
| Vehicle Service | ✅ Running | 8002 | Healthy |
| Location Service | ✅ Running | 8003 | Healthy |
| Notification Service | ⚠️ Issues | 8004 | Error |
| Frontend | 🚧 Development | 3000 | - |

## 🗄️ Database Schema

### Auth Service
- **Users**: Authentication & user management
- **Roles**: Role-based access control
- **Sessions**: User session tracking

### Vehicle Service
- **Vehicles**: Vehicle information & metadata
- **Devices**: GPS device management

### Location Service
- **Locations**: GPS coordinates & tracking data
- **Geofences**: Geographic boundaries
- **Trips**: Journey tracking & analysis

### Notification Service
- **Alerts**: Real-time notifications
- **Rules**: Alert configuration
- **WebSocket**: Real-time connections

## 🔧 Development

### Backend Development
```bash
# Start development environment
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f [service-name]

# Restart service
docker compose -f docker-compose.dev.yml restart [service-name]
```

### Frontend Development
```bash
# Start frontend development
./scripts/dev-frontend.sh

# Or local development
cd frontend
npm install
npm start
```

### Testing
```bash
# Run integration tests
./scripts/test-integration.sh

# Run frontend tests
cd frontend && npm test
```

## 📁 Project Structure

```
Fleet Tracker/
├── .cursor-plan/           # Project planning documents
├── services/               # Microservices
│   ├── api-gateway/        # API Gateway service
│   ├── auth-service/       # Authentication service
│   ├── vehicle-service/    # Vehicle management
│   ├── location-service/   # GPS & geofencing
│   └── notification-service/ # Alerts & notifications
├── frontend/               # React frontend application
├── infrastructure/         # Infrastructure configs
│   ├── databases/          # Database initialization
│   ├── mqtt-broker/        # MQTT configuration
│   └── nginx/              # Reverse proxy config
├── shared/                 # Shared libraries
├── scripts/                # Development scripts
├── tests/                  # Integration tests
└── docker-compose.dev.yml  # Development environment
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/validate-token` - Token validation

### Vehicles
- `GET /vehicles/` - List vehicles
- `POST /vehicles/` - Create vehicle
- `GET /vehicles/{id}` - Get vehicle details
- `PUT /vehicles/{id}` - Update vehicle
- `DELETE /vehicles/{id}` - Delete vehicle

### Locations
- `GET /locations/` - Get location history
- `POST /locations/` - Add location data
- `GET /locations/current` - Current locations
- `GET /geofences/` - List geofences

### Notifications
- `GET /alerts/` - List alerts
- `POST /alerts/` - Create alert
- `WS /ws` - WebSocket connection

## 🚧 Roadmap

### Phase 1: Core Services ✅ (85% Complete)
- [x] Infrastructure setup
- [x] API Gateway
- [x] Authentication service
- [x] Vehicle management
- [x] Location tracking
- [ ] Notification service (minor issues)

### Phase 2: Frontend Development 🚧 (30% Complete)
- [x] Project structure
- [x] Basic components
- [ ] Authentication pages
- [ ] Dashboard
- [ ] Live map
- [ ] Vehicle management UI

### Phase 3: Real-time Features 🚧 (20% Complete)
- [x] WebSocket setup
- [ ] Real-time location updates
- [ ] Live alerts
- [ ] Geofence notifications

### Phase 4: Production Deployment 📋 (0% Complete)
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Monitoring & logging
- [ ] Performance optimization

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Use conventional commits

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Trương Quốc Huân** - [truonghuan0709@gmail.com](mailto:truonghuan0709@gmail.com)

---

**Last Updated**: August 25, 2024  
**Status**: Development in Progress (85% Complete)
