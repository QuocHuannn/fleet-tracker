# Fleet Tracker - Microservices Error Handling

## 1. Các thách thức của Error Handling trong Microservices

Microservice architecture đưa ra các thách thức độc đáo cho error handling so với monolithic:

### 1.1 Distributed System Challenges

- **Network Failures**: Service-to-service communication có thể thất bại
- **Partial Failures**: Một phần của request có thể thành công, một phần thất bại
- **Cascading Failures**: Lỗi từ 1 service có thể lan ra toàn hệ thống
- **Tracing Errors**: Khó theo dõi error qua nhiều services
- **Timeouts**: Service overload hoặc network latency

### 1.2 Consistency Challenges

- **Distributed Transactions**: Khó đảm bảo ACID properties
- **Eventual Consistency**: Dữ liệu có thể không đồng bộ ngay lập tức
- **Database per Service**: Mỗi service có database riêng, transaction xuyên service phức tạp
- **Event Sourcing Failures**: Message processing failures

## 2. Error Handling Strategies cho Microservices

### 2.1 API Gateway Error Handling

```python
# services/api-gateway/app/middleware.py
class ErrorHandlingMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            # Process request
            response = await call_next(request)
            return response
            
        except httpx.RequestError as e:
            # Service communication error
            logger.error(f"Service request error: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": "Upstream service is temporarily unavailable",
                    "request_id": request.state.request_id,
                    "service": extract_service_from_url(str(e.request.url))
                }
            )
            
        except httpx.HTTPStatusError as e:
            # Propagate status code from upstream service
            try:
                error_body = e.response.json()
                return JSONResponse(
                    status_code=e.response.status_code,
                    content=error_body
                )
            except ValueError:
                return JSONResponse(
                    status_code=e.response.status_code,
                    content={
                        "error": "upstream_error",
                        "message": f"Service returned error {e.response.status_code}",
                        "request_id": request.state.request_id
                    }
                )
                
        except Exception as e:
            # Unexpected error
            logger.exception(f"Unhandled gateway error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "request_id": request.state.request_id
                }
            )
```

### 2.2 Circuit Breaker Pattern

Ngăn cascading failures bằng cách tạm dừng request khi service lỗi liên tục:

```python
# services/api-gateway/app/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0

    async def execute(self, func, *args, **kwargs):
        if self.state == "OPEN":
            # Check if timeout has elapsed
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            
            # Success in HALF_OPEN means we can reset
            if self.state == "HALF_OPEN":
                self.reset()
                
            return result
            
        except Exception as e:
            self.record_failure()
            raise e
            
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            
    def reset(self):
        self.failure_count = 0
        self.state = "CLOSED"
```

### 2.3 Retry Pattern với Exponential Backoff

```python
# shared/utils/retry.py
async def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=30):
    retries = 0
    last_exception = None
    
    while retries <= max_retries:
        try:
            return await func()
        except RetryableError as e:
            last_exception = e
            retries += 1
            
            if retries > max_retries:
                break
                
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** (retries - 1)) + random.uniform(0, 1), max_delay)
            
            logger.info(f"Retry {retries}/{max_retries} after {delay:.2f}s")
            await asyncio.sleep(delay)
    
    # If we get here, all retries failed
    raise last_exception
```

### 2.4 Service-Specific Error Handling

#### Auth Service

```python
# services/auth-service/app/error_handlers.py
@app.exception_handler(JWTError)
async def handle_jwt_error(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=401,
        content={
            "error": "invalid_token",
            "message": "Authentication token is invalid or expired",
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(FirebaseAuthError)
async def handle_firebase_error(request: Request, exc: FirebaseAuthError):
    return JSONResponse(
        status_code=401,
        content={
            "error": "firebase_auth_error",
            "message": str(exc),
            "request_id": request.state.request_id
        }
    )
```

#### Vehicle Service

```python
# services/vehicle-service/app/error_handlers.py
@app.exception_handler(VehicleNotFoundError)
async def handle_vehicle_not_found(request: Request, exc: VehicleNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "vehicle_not_found",
            "message": f"Vehicle with ID {exc.vehicle_id} not found",
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(DuplicateLicensePlateError)
async def handle_duplicate_license(request: Request, exc: DuplicateLicensePlateError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "duplicate_license_plate",
            "message": f"Vehicle with license plate {exc.license_plate} already exists",
            "request_id": request.state.request_id
        }
    )
```

#### Location Service

```python
# services/location-service/app/error_handlers.py
@app.exception_handler(InvalidCoordinatesError)
async def handle_invalid_coordinates(request: Request, exc: InvalidCoordinatesError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_coordinates",
            "message": "Invalid GPS coordinates provided",
            "details": exc.details,
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(MQTTConnectionError)
async def handle_mqtt_error(request: Request, exc: MQTTConnectionError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "mqtt_unavailable",
            "message": "MQTT broker connection failed",
            "request_id": request.state.request_id
        }
    )
```

## 3. Distributed Tracing

### 3.1 Request Tracing Infrastructure

```python
# services/api-gateway/app/tracing.py
class TracingMiddleware:
    async def __call__(self, request: Request, call_next):
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        request.state.trace_start = time.time()
        
        # Add tracing headers to response
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        
        # Calculate processing time
        processing_time = time.time() - request.state.trace_start
        response.headers["X-Processing-Time"] = f"{processing_time:.4f}"
        
        # Log request completion
        logger.info(
            f"Request completed",
            request_id=request_id,
            trace_id=trace_id,
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            processing_time=processing_time
        )
        
        return response
```

### 3.2 Structured Logging

```python
# shared/logging/logger.py
import structlog
from datetime import datetime

def setup_logger():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

# Usage in services
logger = setup_logger()
logger.info(
    "Processing location update",
    vehicle_id="abc123",
    trace_id=trace_id,
    request_id=request_id,
    coordinates={"lat": 10.762622, "lng": 106.660172}
)
```

### 3.3 Correlation IDs

```python
# shared/http_client/client.py
class TracedHTTPClient:
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        
    async def request(self, method: str, path: str, request: Request = None, **kwargs):
        # Propagate tracing headers
        headers = kwargs.get("headers", {})
        if request:
            headers["X-Request-ID"] = getattr(request.state, "request_id", str(uuid.uuid4()))
            headers["X-Trace-ID"] = getattr(request.state, "trace_id", str(uuid.uuid4()))
            headers["X-Caller-Service"] = self.service_name
            
        kwargs["headers"] = headers
            
        # Log outgoing request
        logger.info(
            f"Outgoing request to {self.service_name}",
            method=method,
            path=path,
            request_id=headers.get("X-Request-ID"),
            trace_id=headers.get("X-Trace-ID")
        )
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                **kwargs
            )
            
        # Log response
        logger.info(
            f"Response from {self.service_name}",
            status_code=response.status_code,
            request_id=headers.get("X-Request-ID"),
            trace_id=headers.get("X-Trace-ID")
        )
        
        return response
```

## 4. Fault Tolerance Patterns

### 4.1 Fallbacks

```python
# services/location-service/app/services/location_service.py
async def get_current_location(self, vehicle_id: str):
    # Try Redis cache first (fast)
    try:
        cached_location = await self.cache.get(f"vehicle:{vehicle_id}:location")
        if cached_location:
            return json.loads(cached_location)
    except RedisError:
        logger.warning(f"Redis error, falling back to database", vehicle_id=vehicle_id)
    
    # Fallback to database
    try:
        location = await self.repository.get_latest_location(vehicle_id)
        return location
    except Exception as e:
        logger.error(f"Database error: {str(e)}", vehicle_id=vehicle_id)
        
        # Last resort: Return empty result with error flag
        return {
            "error": True,
            "message": "Location temporarily unavailable",
            "vehicle_id": vehicle_id,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### 4.2 Bulkhead Pattern

Isolate failures bằng cách chia resources:

```python
# services/api-gateway/app/limiter.py
class ServiceLimiter:
    def __init__(self, max_concurrent=100):
        self.semaphores = {}
        self.max_concurrent = max_concurrent
        
    def get_semaphore(self, service_name: str):
        if service_name not in self.semaphores:
            self.semaphores[service_name] = asyncio.Semaphore(self.max_concurrent)
        return self.semaphores[service_name]
    
    async def execute(self, service_name: str, func, *args, **kwargs):
        sem = self.get_semaphore(service_name)
        
        async with sem:
            return await func(*args, **kwargs)
```

### 4.3 Timeout Pattern

```python
# shared/utils/timeout.py
async def with_timeout(coro, timeout_seconds=10):
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
```

## 5. Monitoring & Alerting

### 5.1 Service Health Checks

Mỗi service cần endpoint `/health`:

```python
@router.get("/health")
async def health_check():
    health = {"status": "healthy", "service": "location-service"}
    
    # Database check
    try:
        await check_database_connection()
        health["database"] = "connected"
    except Exception as e:
        health["status"] = "degraded"
        health["database"] = f"error: {str(e)}"
    
    # Redis check
    try:
        await check_redis_connection()
        health["redis"] = "connected"
    except Exception as e:
        health["status"] = "degraded"
        health["redis"] = f"error: {str(e)}"
    
    # MQTT check
    try:
        await check_mqtt_connection()
        health["mqtt"] = "connected"
    except Exception as e:
        health["status"] = "degraded"
        health["mqtt"] = f"error: {str(e)}"
    
    # Return appropriate status code
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)
```

### 5.2 Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# HTTP request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['service', 'method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['service', 'method', 'endpoint']
)

# Service-specific metrics
LOCATION_UPDATES = Counter(
    'location_updates_total',
    'Total location updates received',
    ['success']
)

GEOFENCE_VIOLATIONS = Counter(
    'geofence_violations_total',
    'Total geofence violations detected',
    ['type']
)

ACTIVE_VEHICLES = Gauge(
    'active_vehicles',
    'Number of currently active vehicles'
)
```

### 5.3 Centralized Logging với ELK Stack

```yaml
# monitoring/docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      
  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch
      
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
      
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.0
    user: root
    volumes:
      - ./monitoring/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - elasticsearch
      - logstash

volumes:
  elasticsearch_data:
```

## 6. Testing Error Scenarios

### 6.1 Service Chaos Testing

```python
# tests/chaos/service_failures.py
async def test_auth_service_failure(self):
    # Simulate Auth Service down
    with patch('app.services.auth_client.request') as mock_request:
        mock_request.side_effect = httpx.RequestError("Connection failed")
        
        # Attempt login
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        
        # Verify response
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "service_unavailable"
        assert "auth" in data["service"]
```

### 6.2 Circuit Breaker Testing

```python
# tests/resilience/circuit_breaker_test.py
async def test_circuit_breaker_trips_after_threshold(self):
    breaker = CircuitBreaker(failure_threshold=3)
    
    # Fail 3 times
    for _ in range(3):
        with pytest.raises(ValueError):
            await breaker.execute(lambda: asyncio.raise(ValueError("Test error")))
    
    # Verify circuit is open
    assert breaker.state == "OPEN"
    
    # Verify circuit rejects requests
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.execute(lambda: "This should not execute")
```

### 6.3 Timeout Testing

```python
# tests/resilience/timeout_test.py
async def test_operation_times_out():
    async def slow_operation():
        await asyncio.sleep(2)
        return "Result"
    
    with pytest.raises(TimeoutError):
        await with_timeout(slow_operation(), timeout_seconds=1)
```

## 7. Error Handling Best Practices

1. **Fail Fast**: Phát hiện lỗi sớm và báo cáo lỗi ngay lập tức
2. **Graceful Degradation**: Service should continue functioning with reduced functionality
3. **Default Behavior**: Provide sensible defaults when dependencies fail
4. **Consistent Error Formats**: Use consistent error response format across services
5. **Correlation IDs**: Include request_id và trace_id trong mọi error response
6. **Retries with Backoff**: Retry failed operations with increasing delays
7. **Circuit Breakers**: Prevent cascading failures with circuit breakers
8. **Health Checks**: Regular monitoring of service dependencies
9. **Detailed Logging**: Log all errors với context đầy đủ
10. **Documentation**: Document all error codes và recovery procedures
