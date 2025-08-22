# 🚚 Fleet Tracker

### Real-time GPS Vehicle Tracking System

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=3FB3D3&width=435&lines=Real-time+GPS+Vehicle+Tracking;Microservices+Architecture;Cloud+Native+Solution)

Fleet Tracker là hệ thống quản lý đội xe toàn diện, cung cấp theo dõi GPS thời gian thực, lịch sử di chuyển, geofencing và phân tích fleet. Được thiết kế cho quản trị viên để giám sát và quản lý đội xe hiệu quả.

## ✨ Core Features

- 🗺️ **Real-time GPS Tracking** - Cập nhật vị trí xe theo thời gian thực
- 📊 **Interactive Dashboard** - Tổng quan fleet với map và metrics
- 🚗 **Vehicle Management** - Quản lý thông tin xe và trạng thái  
- 🔐 **Authentication & Authorization** - Firebase Auth với role-based permissions
- 🚨 **Smart Alerts** - Cảnh báo vi phạm tốc độ, geofence violations
- 📈 **Analytics & Reports** - Báo cáo hiệu suất và thống kê fleet

## 🏗️ System Architecture

```
IoT/GPS Device → MQTT Broker → FastAPI Backend → PostgreSQL + Redis
                                      ↓
                               WebSocket + REST API  
                                      ↓
                                React Frontend
```

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

# 4. Run database migrations  
docker-compose exec backend alembic upgrade head

# 5. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🐳 Container Services

- **backend** (port 8000) - FastAPI application với MQTT subscriber
- **frontend** (port 3000) - React SPA với map integration
- **database** (port 5432) - PostgreSQL với PostGIS spatial extension
- **redis** (port 6379) - Cache và session store
- **mosquitto** (ports 1883/8883) - MQTT broker cho IoT messaging

## 📚 API Overview

**Authentication**
- `POST /auth/login` - Firebase token authentication
- `POST /auth/refresh` - Refresh access token

**Vehicles**  
- `GET /vehicles` - List vehicles với filtering và pagination
- `GET /vehicles/{id}/location` - Current GPS position
- `GET /vehicles/{id}/history` - Location history với time range

**Real-time**
- `WebSocket /ws` - Subscribe to live vehicle updates
- `GET /alerts` - System alerts và notifications

Xem chi tiết: http://localhost:8000/docs (Swagger UI)

## 📊 Key Features Implementation

**Real-time Tracking**
- MQTT message processing cho GPS data
- WebSocket broadcasting cho live updates
- PostGIS spatial indexing cho performance queries

**Security & Performance**
- JWT-based authentication với Firebase integration
- Role-based access control (Admin/Manager/Viewer)
- Redis caching cho frequent queries
- Rate limiting và input validation

**Scalability**
- Docker container architecture
- Database connection pooling
- Horizontal scaling ready
- Efficient spatial queries với PostGIS

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
---

**⭐ Crafted with passion by [Trương Quốc Huân](https://github.com/QuocHuannn)** ❤️
