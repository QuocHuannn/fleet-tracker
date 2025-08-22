# Fleet Tracker - Setup Guide

Complete setup guide cho việc development và deployment Fleet Tracker system.

## 📋 Prerequisites

### Required Software
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** 2.30+
- **Node.js** 18+ (cho local frontend development)
- **Python** 3.11+ (cho local backend development)

### External Services
- **Firebase Project** cho authentication
- **Mapbox Account** cho map services
- **SMTP Server** cho email notifications (optional)

## 🚀 Quick Start (Development)

### 1. Clone Repository
```bash
git clone https://github.com/QuocHuannn/fleet-tracker.git
cd fleet-tracker
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit với actual values
nano .env
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# Check services status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Verify database
docker-compose exec database psql -U fleet_user -d fleet_tracker -c "\\dt"
```

### 5. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (fleet_user/fleet_password)
- **Redis**: localhost:6379
- **MQTT**: localhost:1883

## ⚙️ Development Workflow

### Backend Development
```bash
# Enter backend container
docker-compose exec backend bash

# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Frontend Development
```bash
# Enter frontend container
docker-compose exec frontend sh

# Install new packages
npm install package_name

# Run tests
npm test

# Lint và format
npm run lint
npm run format
```

### Database Management
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Database backup
docker-compose exec database pg_dump -U fleet_user fleet_tracker > backup.sql
```

## 🔧 Configuration

### Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://fleet_user:password@database:5432/fleet_tracker

# Redis
REDIS_URL=redis://redis:6379

# MQTT
MQTT_BROKER_HOST=mosquitto
MQTT_USERNAME=fleet_user
MQTT_PASSWORD=secure_password

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_KEY=base64_encoded_key

# JWT
JWT_SECRET_KEY=your-secure-secret-key

# Maps
MAPBOX_ACCESS_TOKEN=your-mapbox-token
```

### Optional Configuration
```env
# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
PROMETHEUS_ENABLED=true

# Performance
REDIS_MAX_CONNECTIONS=100
DB_POOL_SIZE=20
```

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database health
docker-compose exec database pg_isready -U fleet_user

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Follow logs với timestamps
docker-compose logs -f -t
```

### Performance Monitoring
```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Prometheus: http://localhost:9090
# Access Grafana: http://localhost:3001 (admin/admin)
```

## 🧪 Testing

### Backend Tests
```bash
# Unit tests
docker-compose exec backend pytest tests/

# With coverage
docker-compose exec backend pytest --cov=app tests/

# Integration tests
docker-compose exec backend pytest tests/integration/

# Load testing
docker-compose exec backend locust -f tests/load/locustfile.py
```

### Frontend Tests
```bash
# Unit tests
docker-compose exec frontend npm test

# E2E tests
docker-compose exec frontend npm run test:e2e

# Component tests
docker-compose exec frontend npm run test:component
```

## 🔒 Security

### Development Security
- Change default passwords trong .env
- Enable authentication trong MQTT broker
- Use HTTPS cho production
- Validate tất cả user inputs

### Production Security Checklist
- [ ] Strong passwords và secrets
- [ ] SSL/TLS certificates configured
- [ ] Firebase security rules setup
- [ ] Database access restricted
- [ ] MQTT broker authentication enabled
- [ ] API rate limiting configured
- [ ] Regular security updates

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports trong docker-compose.yml
```

**Database connection errors:**
```bash
# Check database container
docker-compose logs database

# Reset database
docker-compose down -v
docker-compose up database -d
```

**Frontend not loading:**
```bash
# Check node_modules
docker-compose exec frontend npm install

# Clear cache
docker-compose down
docker volume prune
docker-compose up --build
```

**MQTT connection issues:**
```bash
# Check broker status
docker-compose logs mosquitto

# Test connection
docker-compose exec mosquitto mosquitto_pub -h localhost -t test -m "hello"
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Optimize database
docker-compose exec database psql -U fleet_user -d fleet_tracker -c "VACUUM ANALYZE;"

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

## 🚀 Production Deployment

Xem [deployment guide](./DEPLOYMENT.md) để detailed production setup instructions.

## 📞 Support

- **Documentation**: [docs/](.)
- **Issues**: [GitHub Issues](https://github.com/QuocHuannn/fleet-tracker/issues)
- **Email**: truonghuan0709@gmail.com

---

**Happy coding! 🚚✨**
