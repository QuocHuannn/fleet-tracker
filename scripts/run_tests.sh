#!/bin/bash
# Fleet Tracker System Test Runner

set -e

echo "🧪 Fleet Tracker System Integration Tests"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Compose is running
print_status "Checking if services are running..."
if ! docker compose ps | grep -q "Up"; then
    print_error "Services are not running. Starting services..."
    docker compose up -d
    print_status "Waiting for services to be ready..."
    sleep 30
else
    print_success "Services are already running"
fi

# Install test dependencies
print_status "Installing test dependencies..."
pip install httpx aiomqtt pytest pytest-asyncio > /dev/null 2>&1 || {
    print_warning "Could not install dependencies via pip. Trying with python3 -m pip..."
    python3 -m pip install httpx aiomqtt pytest pytest-asyncio > /dev/null 2>&1 || {
        print_error "Failed to install test dependencies"
        exit 1
    }
}

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API Gateway is healthy"
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Services failed to become healthy within timeout"
    print_status "Service status:"
    docker compose ps
    exit 1
fi

echo "" # New line after dots

# Run the integration tests
print_status "Running system integration tests..."
cd "$(dirname "$0")/.."

python3 tests/test_system_integration.py

test_exit_code=$?

# Generate test report
print_status "Generating test report..."
echo ""
echo "🏁 TEST EXECUTION SUMMARY"
echo "========================"
echo "Date: $(date)"
echo "Services tested: API Gateway, Auth Service, Vehicle Service, Location Service, Notification Service, MQTT Broker"

if [ $test_exit_code -eq 0 ]; then
    print_success "All integration tests PASSED ✅"
    echo ""
    echo "🎉 Fleet Tracker system is working correctly!"
    echo ""
    echo "🌐 Available endpoints:"
    echo "  - API Gateway: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📡 MQTT Broker: localhost:1883"
    echo "💾 Databases: PostgreSQL instances on ports 5432-5435"
    echo "🔥 Redis: localhost:6379"
else
    print_error "Some integration tests FAILED ❌"
    echo ""
    echo "🔍 Troubleshooting tips:"
    echo "  1. Check service logs: docker compose logs <service-name>"
    echo "  2. Verify all services are running: docker compose ps"
    echo "  3. Check database connections: docker compose exec <db-name> psql -U <user> -d <database>"
    echo "  4. Test individual services: curl http://localhost:<port>/health"
fi

echo ""
echo "📊 System Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

exit $test_exit_code
