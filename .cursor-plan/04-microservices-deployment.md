# Fleet Tracker - Microservices Deployment Plan

## 1. Deployment Strategy cho Microservices

Triển khai hệ thống microservices yêu cầu strategy khác với monolith application. Mỗi service cần được deploy và scale độc lập.

### 1.1 Deployment Principles

- **Independent Deployments**: Mỗi service có pipeline và version riêng
- **Infrastructure as Code**: Docker + Docker Compose/Kubernetes
- **Zero-downtime Deployments**: Blue-green hoặc rolling updates
- **Automated Testing**: Tự động test trước mỗi deployment
- **Observability**: Comprehensive monitoring và logging
- **Deployment Environments**: Dev, Staging, Production

### 1.2 Deployment Architecture

```
                   ┌─────────────────┐
                   │  Load Balancer  │
                   └───────┬─────────┘
                           │
                           ▼
                   ┌─────────────────┐
             ┌─────│   API Gateway   │─────┐
             │     └─────────────────┘     │
             │                             │
     ┌───────▼──────┐             ┌───────▼──────┐
     │ Auth Service │             │Vehicle Service│
     │ Instances    │             │ Instances     │
     └──────────────┘             └──────────────┘
             │                             │
     ┌───────▼──────┐             ┌───────▼──────┐
     │   Auth DB    │             │  Vehicle DB  │
     └──────────────┘             └──────────────┘

    ┌────────────────┐           ┌────────────────┐
    │Location Service│           │Notification Svc│
    │ Instances      │           │ Instances      │
    └───────┬────────┘           └───────┬────────┘
            │                            │
    ┌───────▼──────┐             ┌───────▼──────┐
    │ Location DB  │             │Notification DB│
    └──────────────┘             └──────────────┘

         ┌───────────────────────────────┐
         │  Shared Infrastructure        │
         │  Redis, MQTT, Monitoring      │
         └───────────────────────────────┘
```

## 2. Docker Container Strategy

### 2.1 Base Images

```dockerfile
# Base image for Python services
FROM python:3.11-slim as python-base

# Common setup
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Health check utility
COPY ./shared/healthcheck.sh /usr/local/bin/healthcheck
RUN chmod +x /usr/local/bin/healthcheck

WORKDIR /app
USER appuser
```

### 2.2 Multi-stage Builds

```dockerfile
# Build stage
FROM python-base as builder

USER root
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python-base as runtime

# Copy installed packages from builder
COPY --from=builder /home/appuser/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Runtime libs only
USER root
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD healthcheck

# Start command
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 2.3 Common Docker Compose Base

```yaml
# Base service definitions
x-service-defaults: &service-defaults
  restart: unless-stopped
  logging:
    driver: "json-file"
    options:
      max-size: "100m"
      max-file: "3"

# Python service defaults
x-python-service: &python-service
  <<: *service-defaults
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M

# Database defaults
x-database: &database
  <<: *service-defaults
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
  volumes:
    - database_data:/var/lib/postgresql/data
```

## 3. Production Deployment Strategy

### 3.1 Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # API Gateway
  api-gateway:
    <<: *python-service
    image: ${DOCKER_REGISTRY}/fleet-tracker/api-gateway:${TAG}
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8001
      - VEHICLE_SERVICE_URL=http://vehicle-service:8002
      - LOCATION_SERVICE_URL=http://location-service:8003
      - NOTIFICATION_SERVICE_URL=http://notification-service:8004
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
      - vehicle-service
      - location-service
      - notification-service
      - redis

  # Auth Service
  auth-service:
    <<: *python-service
    image: ${DOCKER_REGISTRY}/fleet-tracker/auth-service:${TAG}
    environment:
      - DATABASE_URL=postgresql://auth_user:${AUTH_DB_PASSWORD}@auth-db:5432/auth_db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - FIREBASE_SERVICE_ACCOUNT_KEY=${FIREBASE_SERVICE_ACCOUNT_KEY}
    depends_on:
      - auth-db
      - redis

  # Vehicle Service
  vehicle-service:
    <<: *python-service
    image: ${DOCKER_REGISTRY}/fleet-tracker/vehicle-service:${TAG}
    environment:
      - DATABASE_URL=postgresql://vehicle_user:${VEHICLE_DB_PASSWORD}@vehicle-db:5432/vehicle_db
      - AUTH_SERVICE_URL=http://auth-service:8001
      - LOG_LEVEL=INFO
    depends_on:
      - vehicle-db

  # Location Service
  location-service:
    <<: *python-service
    image: ${DOCKER_REGISTRY}/fleet-tracker/location-service:${TAG}
    environment:
      - DATABASE_URL=postgresql://location_user:${LOCATION_DB_PASSWORD}@location-db:5432/location_db
      - MQTT_BROKER_URL=mqtt://mosquitto:1883
      - MQTT_USERNAME=${MQTT_USERNAME}
      - MQTT_PASSWORD=${MQTT_PASSWORD}
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - location-db
      - mosquitto
      - redis

  # Notification Service
  notification-service:
    <<: *python-service
    image: ${DOCKER_REGISTRY}/fleet-tracker/notification-service:${TAG}
    environment:
      - DATABASE_URL=postgresql://notification_user:${NOTIFICATION_DB_PASSWORD}@notification-db:5432/notification_db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - notification-db
      - redis

  # Frontend
  frontend:
    <<: *service-defaults
    image: ${DOCKER_REGISTRY}/fleet-tracker/frontend:${TAG}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    environment:
      - REACT_APP_API_URL=https://api.fleettracker.com
      - REACT_APP_WS_URL=wss://api.fleettracker.com/ws

  # Databases
  auth-db:
    <<: *database
    image: postgres:15
    environment:
      - POSTGRES_DB=auth_db
      - POSTGRES_USER=auth_user
      - POSTGRES_PASSWORD=${AUTH_DB_PASSWORD}
    volumes:
      - auth_db_data:/var/lib/postgresql/data

  vehicle-db:
    <<: *database
    image: postgres:15
    environment:
      - POSTGRES_DB=vehicle_db
      - POSTGRES_USER=vehicle_user
      - POSTGRES_PASSWORD=${VEHICLE_DB_PASSWORD}
    volumes:
      - vehicle_db_data:/var/lib/postgresql/data

  location-db:
    <<: *database
    image: postgis/postgis:15-master
    environment:
      - POSTGRES_DB=location_db
      - POSTGRES_USER=location_user
      - POSTGRES_PASSWORD=${LOCATION_DB_PASSWORD}
    volumes:
      - location_db_data:/var/lib/postgresql/data

  notification-db:
    <<: *database
    image: postgres:15
    environment:
      - POSTGRES_DB=notification_db
      - POSTGRES_USER=notification_user
      - POSTGRES_PASSWORD=${NOTIFICATION_DB_PASSWORD}
    volumes:
      - notification_db_data:/var/lib/postgresql/data

  # Shared Infrastructure
  redis:
    <<: *service-defaults
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data

  mosquitto:
    <<: *service-defaults
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "8883:8883"
    volumes:
      - ./infrastructure/mqtt-broker/mosquitto.prod.conf:/mosquitto/config/mosquitto.conf:ro
      - ./infrastructure/mqtt-broker/passwd:/mosquitto/config/passwd:ro
      - ./infrastructure/mqtt-broker/acl:/mosquitto/config/acl:ro
      - ./ssl:/mosquitto/ssl:ro
      - mosquitto_data:/mosquitto/data

  # Monitoring
  prometheus:
    <<: *service-defaults
    image: prom/prometheus
    volumes:
      - ./infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    profiles:
      - monitoring

  grafana:
    <<: *service-defaults
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    profiles:
      - monitoring

volumes:
  auth_db_data:
  vehicle_db_data:
  location_db_data:
  notification_db_data:
  redis_data:
  mosquitto_data:
  prometheus_data:
  grafana_data:
```

### 3.2 Kubernetes Setup

```yaml
# kubernetes/api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: fleet-tracker
  labels:
    app: api-gateway
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: ${DOCKER_REGISTRY}/fleet-tracker/api-gateway:${TAG}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:8001"
        - name: VEHICLE_SERVICE_URL
          value: "http://vehicle-service:8002"
        - name: LOCATION_SERVICE_URL
          value: "http://location-service:8003"
        - name: NOTIFICATION_SERVICE_URL
          value: "http://notification-service:8004"
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: LOG_LEVEL
          value: "INFO"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 60
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
      imagePullSecrets:
      - name: docker-registry-secret

---
# kubernetes/api-gateway-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: fleet-tracker
spec:
  selector:
    app: api-gateway
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fleet-tracker-ingress
  namespace: fleet-tracker
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.fleettracker.com
    - fleettracker.com
    secretName: fleet-tracker-tls
  rules:
  - host: api.fleettracker.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000
  - host: fleettracker.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop

env:
  DOCKER_REGISTRY: ghcr.io
  ORGANIZATION: quochuannn

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api-gateway, auth-service, vehicle-service, location-service, notification-service]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install pytest pytest-cov
          
      - name: Run tests
        run: |
          cd services/${{ matrix.service }}
          pytest --cov=app tests/
          
  build:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api-gateway, auth-service, vehicle-service, location-service, notification-service, frontend]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Set image tags
        id: set-tags
        run: |
          # Set different tags for main vs other branches
          if [[ $GITHUB_REF == 'refs/heads/main' ]]; then
            echo "::set-output name=tags::${DOCKER_REGISTRY}/${ORGANIZATION}/fleet-tracker/${{ matrix.service }}:latest,${DOCKER_REGISTRY}/${ORGANIZATION}/fleet-tracker/${{ matrix.service }}:$(echo $GITHUB_SHA | cut -c1-7)"
          else
            echo "::set-output name=tags::${DOCKER_REGISTRY}/${ORGANIZATION}/fleet-tracker/${{ matrix.service }}:dev-$(echo $GITHUB_SHA | cut -c1-7)"
          fi
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v3
        with:
          context: ./services/${{ matrix.service }}
          push: true
          tags: ${{ steps.set-tags.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          
  deploy-staging:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
          
      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name fleet-tracker-staging
        
      - name: Deploy to Staging
        run: |
          export TAG=$(echo $GITHUB_SHA | cut -c1-7)
          envsubst < kubernetes/staging/kustomization.template.yaml > kubernetes/staging/kustomization.yaml
          kubectl apply -k kubernetes/staging/
          
  deploy-production:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
          
      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name fleet-tracker-production
        
      - name: Deploy to Production
        run: |
          export TAG=$(echo $GITHUB_SHA | cut -c1-7)
          envsubst < kubernetes/production/kustomization.template.yaml > kubernetes/production/kustomization.yaml
          kubectl apply -k kubernetes/production/
```

## 5. Infrastructure Setup

### 5.1 Server Setup

```bash
#!/bin/bash
# infrastructure/scripts/setup-server.sh

set -e

echo "Setting up Fleet Tracker production server..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/fleet-tracker
sudo chown $USER:$USER /opt/fleet-tracker

# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Setup firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 1883  # MQTT
sudo ufw allow 8883  # MQTT SSL
sudo ufw --force enable

# Clone repository
cd /opt/fleet-tracker
git clone https://github.com/QuocHuannn/fleet-tracker.git .

echo "Server setup completed!"
```

### 5.2 SSL Setup

```bash
#!/bin/bash
# infrastructure/scripts/setup-ssl.sh

# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificates
sudo certbot --nginx -d fleettracker.com -d api.fleettracker.com -d www.fleettracker.com

# Auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Copy certificates for use with services
sudo mkdir -p /opt/fleet-tracker/ssl
sudo cp /etc/letsencrypt/live/fleettracker.com/fullchain.pem /opt/fleet-tracker/ssl/
sudo cp /etc/letsencrypt/live/fleettracker.com/privkey.pem /opt/fleet-tracker/ssl/
sudo chown -R $USER:$USER /opt/fleet-tracker/ssl
```

### 5.3 Database Initialization

```bash
#!/bin/bash
# infrastructure/scripts/init-databases.sh

# Generate secure passwords
AUTH_DB_PASSWORD=$(openssl rand -base64 32)
VEHICLE_DB_PASSWORD=$(openssl rand -base64 32)
LOCATION_DB_PASSWORD=$(openssl rand -base64 32)
NOTIFICATION_DB_PASSWORD=$(openssl rand -base64 32)

# Create .env file with database passwords
cat > .env << EOF
AUTH_DB_PASSWORD=$AUTH_DB_PASSWORD
VEHICLE_DB_PASSWORD=$VEHICLE_DB_PASSWORD
LOCATION_DB_PASSWORD=$LOCATION_DB_PASSWORD
NOTIFICATION_DB_PASSWORD=$NOTIFICATION_DB_PASSWORD
EOF

# Start databases only
docker-compose up -d auth-db vehicle-db location-db notification-db

# Wait for databases to be ready
sleep 10

# Run migrations
docker-compose run --rm auth-service alembic upgrade head
docker-compose run --rm vehicle-service alembic upgrade head
docker-compose run --rm location-service alembic upgrade head
docker-compose run --rm notification-service alembic upgrade head

echo "Database initialization completed!"
```

## 6. Deployment Environments

### 6.1 Environment Configuration

```bash
# .env.dev
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Database credentials
AUTH_DB_PASSWORD=auth_password_dev
VEHICLE_DB_PASSWORD=vehicle_password_dev
LOCATION_DB_PASSWORD=location_password_dev
NOTIFICATION_DB_PASSWORD=notification_password_dev

# JWT settings
JWT_SECRET_KEY=dev_jwt_secret_key
JWT_EXPIRE_MINUTES=60

# MQTT settings
MQTT_USERNAME=dev_mqtt_user
MQTT_PASSWORD=dev_mqtt_password
```

```bash
# .env.staging
ENVIRONMENT=staging
LOG_LEVEL=INFO

# Database credentials
AUTH_DB_PASSWORD=auth_password_staging
VEHICLE_DB_PASSWORD=vehicle_password_staging
LOCATION_DB_PASSWORD=location_password_staging
NOTIFICATION_DB_PASSWORD=notification_password_staging

# JWT settings
JWT_SECRET_KEY=staging_jwt_secret_key
JWT_EXPIRE_MINUTES=60

# MQTT settings
MQTT_USERNAME=staging_mqtt_user
MQTT_PASSWORD=staging_mqtt_password
```

```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Database credentials
AUTH_DB_PASSWORD=${AUTH_DB_PASSWORD}
VEHICLE_DB_PASSWORD=${VEHICLE_DB_PASSWORD}
LOCATION_DB_PASSWORD=${LOCATION_DB_PASSWORD}
NOTIFICATION_DB_PASSWORD=${NOTIFICATION_DB_PASSWORD}

# JWT settings
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_EXPIRE_MINUTES=30

# MQTT settings
MQTT_USERNAME=${MQTT_USERNAME}
MQTT_PASSWORD=${MQTT_PASSWORD}

# Other production settings
DOCKER_REGISTRY=ghcr.io
TAG=${TAG:-latest}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
```

### 6.2 Environment Deployment Script

```bash
#!/bin/bash
# infrastructure/scripts/deploy.sh

# Check parameters
if [ -z "$1" ]; then
    echo "Usage: $0 <environment> [tag]"
    echo "Environments: dev, staging, production"
    exit 1
fi

ENV=$1
TAG=${2:-latest}

# Load environment variables
if [ -f ".env.$ENV" ]; then
    source .env.$ENV
else
    echo "Environment file .env.$ENV not found"
    exit 1
fi

# Export variables for Docker Compose
export ENVIRONMENT=$ENV
export TAG=$TAG
export DOCKER_REGISTRY=${DOCKER_REGISTRY:-ghcr.io/quochuannn}

echo "Deploying Fleet Tracker $ENV environment with tag $TAG..."

# Pull latest images
docker-compose -f docker-compose.$ENV.yml pull

# Deploy with zero downtime (rolling update)
docker-compose -f docker-compose.$ENV.yml up -d --remove-orphans

echo "Deployment completed!"
```

## 7. Monitoring & Observability

### 7.1 Prometheus Configuration

```yaml
# infrastructure/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api-gateway:8000']

  - job_name: 'auth-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['auth-service:8001']

  - job_name: 'vehicle-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['vehicle-service:8002']

  - job_name: 'location-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['location-service:8003']

  - job_name: 'notification-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['notification-service:8004']

  # Node Exporter for host metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis Exporter
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 7.2 Grafana Dashboards

```yaml
# infrastructure/monitoring/grafana/provisioning/dashboards/fleet-tracker.yaml
apiVersion: 1

providers:
  - name: 'Fleet Tracker'
    orgId: 1
    folder: 'Fleet Tracker Dashboards'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /etc/grafana/provisioning/dashboards
```

### 7.3 Alert Rules

```yaml
# infrastructure/monitoring/rules/alerts.yml
groups:
  - name: fleet-tracker-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Service {{ $labels.job }} has been down for more than 1 minute."

      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.service }}"
          description: "Service {{ $labels.service }} has error rate above 5% ({{ $value | humanizePercentage }})"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (service, le)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time on {{ $labels.service }}"
          description: "Service {{ $labels.service }} has 95th percentile response time > 1s ({{ $value }}s)"

      - alert: HighCPUUsage
        expr: (100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80% for 5 minutes ({{ $value }}%)"
```

## 8. Backup & Disaster Recovery

### 8.1 Database Backup Script

```bash
#!/bin/bash
# infrastructure/scripts/backup-databases.sh

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup each database
echo "Backing up Auth DB..."
docker exec fleet-tracker_auth-db_1 pg_dump -U auth_user auth_db > "$BACKUP_DIR/auth_db_$TIMESTAMP.sql"

echo "Backing up Vehicle DB..."
docker exec fleet-tracker_vehicle-db_1 pg_dump -U vehicle_user vehicle_db > "$BACKUP_DIR/vehicle_db_$TIMESTAMP.sql"

echo "Backing up Location DB..."
docker exec fleet-tracker_location-db_1 pg_dump -U location_user location_db > "$BACKUP_DIR/location_db_$TIMESTAMP.sql"

echo "Backing up Notification DB..."
docker exec fleet-tracker_notification-db_1 pg_dump -U notification_user notification_db > "$BACKUP_DIR/notification_db_$TIMESTAMP.sql"

# Compress backups
tar -czf "$BACKUP_DIR/databases_$TIMESTAMP.tar.gz" $BACKUP_DIR/*.sql

# Clean up raw SQL files
rm $BACKUP_DIR/*.sql

# Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR/databases_$TIMESTAMP.tar.gz" s3://fleet-tracker-backups/

# Clean old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $(date)"
```

### 8.2 Disaster Recovery Plan

```markdown
# Fleet Tracker - Disaster Recovery Plan

## 1. Recovery Objectives
- **RPO (Recovery Point Objective)**: 24 hours
- **RTO (Recovery Time Objective)**: 2 hours

## 2. Recovery Scenarios

### Database Failure
1. Stop affected services:
   ```
   docker-compose stop auth-service vehicle-service location-service notification-service
   ```
2. Restore from latest backup:
   ```
   # Example for auth-db
   cat /backups/latest/auth_db.sql | docker exec -i fleet-tracker_auth-db_1 psql -U auth_user -d auth_db
   ```
3. Start services:
   ```
   docker-compose up -d auth-service vehicle-service location-service notification-service
   ```

### Service Failure
1. Check logs:
   ```
   docker-compose logs --tail=100 <service-name>
   ```
2. Restart affected service:
   ```
   docker-compose restart <service-name>
   ```
3. If restart fails, rebuild and redeploy:
   ```
   docker-compose up -d --build <service-name>
   ```

### Full System Recovery
1. Set up new server with base requirements
2. Clone repository and configure environment
3. Restore databases from backups
4. Deploy all services:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```
5. Verify system health
6. Update DNS if needed

## 3. Recovery Testing
- Conduct quarterly recovery drills
- Document and improve recovery procedures
```

## 9. Scaling Strategy

### 9.1 Horizontal Scaling

```yaml
# kubernetes/horizontal-pod-autoscaler.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: fleet-tracker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 9.2 Database Scaling

- **Connection Pooling**: PgBouncer for PostgreSQL
- **Read Replicas**: For high-read services
- **Sharding**: Location data by time periods
- **Caching Layer**: Redis for frequently accessed data

### 9.3 Future Growth Plan

1. **Service Mesh**: Istio/Linkerd for advanced networking
2. **Stateful Services**: StatefulSets for database scaling
3. **Global Deployment**: Multi-region deployment
4. **Edge Caching**: CDN for frontend assets
