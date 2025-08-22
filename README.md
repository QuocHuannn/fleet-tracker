# 🚚 Fleet Tracker

### Real-time GPS Vehicle Tracking System

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=3FB3D3&width=435&lines=Real-time+GPS+Vehicle+Tracking;True+Microservices+Architecture;Distributed+Systems+Learning)

Fleet Tracker là hệ thống quản lý đội xe enterprise-grade được xây dựng theo **True Microservices Architecture**. Hệ thống cung cấp theo dõi GPS thời gian thực, lịch sử di chuyển, geofencing và phân tích fleet với khả năng mở rộng và độ tin cậy cao.

## ✨ Core Features

- 🗺️ **Real-time GPS Tracking** - Cập nhật vị trí xe theo thời gian thực
- 📊 **Interactive Dashboard** - Tổng quan fleet với map và metrics
- 🚗 **Vehicle Management** - Quản lý thông tin xe và trạng thái  
- 🔐 **Authentication & Authorization** - Firebase Auth với role-based permissions
- 🚨 **Smart Alerts** - Cảnh báo vi phạm tốc độ, geofence violations
- 📈 **Analytics & Reports** - Báo cáo hiệu suất và thống kê fleet

## 🏗️ Microservices Architecture

```
                            ┌─────────────────┐
                            │   API Gateway   │ ← Frontend (React)
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
GPS Devices ────────────────┴────────────────────┘
```

### 🎯 Microservices Overview
- **API Gateway (8000)**: Request routing, authentication, rate limiting
- **Auth Service (8001)**: User authentication & authorization với Firebase
- **Vehicle Service (8002)**: Vehicle management & device registration  
- **Location Service (8003)**: GPS data processing & spatial operations
- **Notification Service (8004)**: Real-time alerts & WebSocket connections

## 🛠️ Tech Stack

<div align="center">

### Backend
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-6+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-brightgreen?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Authentication-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

### Frontend
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Mapbox](https://img.shields.io/badge/Mapbox-000000?style=for-the-badge&logo=mapbox&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-Client-4A90E2?style=for-the-badge)
![MaterialUI](https://img.shields.io/badge/Material--UI-0081CB?style=for-the-badge&logo=material-ui&logoColor=white)

### Infrastructure
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)

</div>

## 🚀 Quick Development Setup

### Prerequisites
- Docker & Docker Compose
- Git
- Firebase project
- Mapbox access token

### Getting Started
```bash
# 1. Clone repository
git clone https://github.com/QuocHuannn/fleet-tracker.git
cd fleet-tracker

# 2. Setup environment
cp .env.example .env
# Edit .env with your configurations

# 3. Start all services
docker-compose up -d

# 4. Run database migrations cho tất cả services
docker-compose exec auth-service alembic upgrade head
docker-compose exec vehicle-service alembic upgrade head  
docker-compose exec location-service alembic upgrade head
docker-compose exec notification-service alembic upgrade head

# 5. Access microservices
# API Gateway: http://localhost:8000
# Auth Service: http://localhost:8001/docs
# Vehicle Service: http://localhost:8002/docs
# Location Service: http://localhost:8003/docs
# Notification Service: http://localhost:8004/docs
# Frontend: http://localhost:3000
```

## 🐳 Microservices Containers

- **api-gateway** (port 8000) - Request routing & authentication
- **auth-service** (port 8001) - User management & JWT validation
- **vehicle-service** (port 8002) - Vehicle CRUD & device management
- **location-service** (port 8003) - GPS processing & spatial queries
- **notification-service** (port 8004) - Alerts & real-time notifications
- **frontend** (port 3000) - React SPA với map integration
- **Multiple Databases** - PostgreSQL per service + Redis shared cache
- **mosquitto** (ports 1883/8883) - MQTT broker cho GPS devices

## 📚 API Overview

**API Gateway (Port 8000)**
- `GET /health` - System health check
- `POST /auth/*` - Proxy to Auth Service
- `GET /vehicles/*` - Proxy to Vehicle Service
- `GET /locations/*` - Proxy to Location Service
- `WebSocket /ws` - Real-time notifications

**Auth Service (Port 8001)**
- `POST /login` - Firebase authentication
- `POST /refresh` - JWT token refresh
- `GET /users/profile` - User profile management

**Vehicle Service (Port 8002)**
- `GET /vehicles` - Vehicle management
- `POST /vehicles` - Register new vehicle
- `PUT /vehicles/{id}` - Update vehicle info

**Location Service (Port 8003)**
- `GET /locations/current` - Real-time positions
- `GET /locations/history` - Historical GPS data
- `POST /geofences` - Geofence management

**Notification Service (Port 8004)**
- `GET /alerts` - Alert management
- `WebSocket /notifications` - Real-time updates
- `POST /notifications/rules` - Alert rules

Xem chi tiết: http://localhost:8000/docs (API Gateway)

## 📊 Key Features Implementation

**Microservices Benefits**
- **Independent Scaling**: Mỗi service scale riêng biệt based on load
- **Fault Isolation**: Service failure không affect toàn bộ system
- **Technology Diversity**: Different tech stacks per service optimization
- **Parallel Development**: Teams có thể work independently trên services

**Distributed Architecture**
- **Service Discovery**: Automatic service registration & discovery
- **Load Balancing**: Multiple instances per service
- **Circuit Breaker**: Fault tolerance patterns implementation
- **Event-Driven**: Async communication với message queues

**Enterprise Security**
- **JWT Authentication**: Service-to-service security
- **API Gateway**: Central authentication & authorization point
- **Database Isolation**: Separate databases per service
- **mTLS Communication**: Secure inter-service communication

## 🚀 Production Deployment

```bash
# Production deployment với Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# SSL setup với Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

CI/CD pipeline tự động test, build images và deploy khi push to main branch.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 📞 Contact & Author

| <img src="https://media.giphy.com/media/MeJgB3yMwRILY5YDKR/giphy.gif" width="30"> **Email** | <img src="https://media.giphy.com/media/Q7LHmoFwVP6Yc3lU8r/giphy.gif" width="30"> **Location** | <img src="https://media.giphy.com/media/WUlplcMpOCEmTGBtBW/giphy.gif" width="30"> **Phone** |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| [truonghuan0709@gmail.com](mailto:truonghuan0709@gmail.com) | TP. Hồ Chí Minh, Việt Nam | +84 335 597 676 |

### 🚀 Professional Highlights

| <img src="https://media.giphy.com/media/SWoSkN6DxTszqIKEqv/giphy.gif" width="30"> **Microservices Expert** | <img src="https://media.giphy.com/media/kHkDbKpH8PFe8OnxrM/giphy.gif" width="30"> **Cloud Native Specialist** | <img src="https://media.giphy.com/media/VgGthkhUvGgOit75Y9i/giphy.gif" width="30"> **Performance Optimizer** |
| ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Architected scalable systems | Kubernetes & Docker mastery | High-performance applications |

---

**⭐ Crafted with passion by [Trương Quốc Huân](https://github.com/QuocHuannn)** ❤️
