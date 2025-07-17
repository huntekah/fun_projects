# Observability Strategy

## Logging Architecture

### Structured Logging
```python
import structlog
import json

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Usage example
logger = structlog.get_logger()

logger.info(
    "recommendation_request",
    user_id=12345,
    location={"lat": 37.7749, "lng": -122.4194},
    num_results=10,
    response_time_ms=85,
    cache_hit=True
)
```

### Log Levels and Categories
```yaml
# Application logs
levels:
  DEBUG: Development debugging
  INFO: Normal operations, business events
  WARN: Degraded performance, retries
  ERROR: Service errors, failed requests
  FATAL: Service crashes, data corruption

categories:
  business: User interactions, recommendations
  performance: Latency, throughput metrics  
  security: Authentication, authorization
  infrastructure: Database, cache, network
  ml: Model training, inference, drift
```

### Centralized Logging (ELK Stack)
```yaml
# Logstash configuration
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "recommendation-service" {
    json {
      source => "message"
    }
    
    # Parse request_id for tracing
    if [request_id] {
      mutate {
        add_field => { "trace_id" => "%{request_id}" }
      }
    }
    
    # Categorize log levels
    if [level] == "ERROR" {
      mutate {
        add_tag => ["error"]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "recommendations-%{+YYYY.MM.dd}"
  }
}
```

## Distributed Tracing

### OpenTelemetry Integration
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Usage in recommendation pipeline
async def get_recommendations(request):
    with tracer.start_as_current_span("recommendation_pipeline") as span:
        span.set_attribute("user_id", request.user_id)
        span.set_attribute("location.lat", request.location.latitude)
        span.set_attribute("location.lng", request.location.longitude)
        
        # Geographic filtering
        with tracer.start_as_current_span("geospatial_query") as geo_span:
            nearby_places = await geo_index.find_nearby_places(request)
            geo_span.set_attribute("candidates_found", len(nearby_places))
        
        # Feature enrichment
        with tracer.start_as_current_span("feature_enrichment") as feat_span:
            features = await feature_store.get_features(request, nearby_places)
            feat_span.set_attribute("features_loaded", len(features))
        
        # ML inference
        with tracer.start_as_current_span("ml_inference") as ml_span:
            scores = await model.predict(features)
            ml_span.set_attribute("inference_time_ms", ml_span.duration)
            
        return recommendations
```

### Trace Correlation
```python
# Correlate logs with traces
import uuid
from opentelemetry import trace

def generate_correlation_id():
    """Generate correlation ID for request tracking"""
    span = trace.get_current_span()
    if span:
        return span.get_span_context().trace_id
    return str(uuid.uuid4())

# Add to all log statements
logger.info(
    "recommendation_request",
    correlation_id=correlation_id,
    user_id=user_id,
    # ... other fields
)
```

## Metrics Collection

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# Business metrics
RECOMMENDATION_REQUESTS = Counter(
    'recommendation_requests_total',
    'Total recommendation requests',
    ['user_segment', 'category', 'location_region']
)

RECOMMENDATION_LATENCY = Histogram(
    'recommendation_latency_seconds',
    'Recommendation request latency',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

CACHE_HIT_RATE = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

# ML metrics
MODEL_INFERENCE_TIME = Summary(
    'model_inference_duration_seconds',
    'Time spent on model inference'
)

FEATURE_FRESHNESS = Gauge(
    'feature_freshness_seconds',
    'Age of features in seconds',
    ['feature_type']
)

# Usage example
@MODEL_INFERENCE_TIME.time()
async def predict(features):
    # ML inference code
    return predictions

# Record metrics
RECOMMENDATION_REQUESTS.labels(
    user_segment='young_professionals',
    category='restaurant',
    location_region='san_francisco'
).inc()

CACHE_HIT_RATE.set(cache_hit_percentage)
```

### Custom Metrics Dashboard
```yaml
# Grafana dashboard configuration
dashboard:
  title: "Recommendation System Overview"
  panels:
    - title: "Request Rate"
      type: "graph"
      targets:
        - expr: "rate(recommendation_requests_total[5m])"
          legend: "Requests/sec"
    
    - title: "Response Time"
      type: "graph"  
      targets:
        - expr: "histogram_quantile(0.95, rate(recommendation_latency_seconds_bucket[5m]))"
          legend: "95th percentile"
        - expr: "histogram_quantile(0.50, rate(recommendation_latency_seconds_bucket[5m]))"
          legend: "50th percentile"
    
    - title: "Cache Performance"
      type: "singlestat"
      targets:
        - expr: "cache_hit_rate"
          legend: "Hit Rate %"
    
    - title: "ML Model Performance"
      type: "graph"
      targets:
        - expr: "model_inference_duration_seconds"
          legend: "Inference Time"
        - expr: "recommendation_ctr"
          legend: "Click-Through Rate"
```

## Health Checks

### Liveness and Readiness Probes
```python
from fastapi import FastAPI, status

app = FastAPI()

@app.get("/health/live", status_code=200)
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.now()}

@app.get("/health/ready", status_code=200)  
async def readiness():
    """Kubernetes readiness probe"""
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "ml_model": await check_model_availability(),
        "feature_store": await check_feature_store()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )

async def check_database_connection():
    """Check PostgreSQL connection"""
    try:
        async with database_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False
```

### Deep Health Checks
```python
@app.get("/health/deep", status_code=200)
async def deep_health_check():
    """Comprehensive health check for monitoring"""
    checks = {
        "system": {
            "cpu_usage": get_cpu_usage(),
            "memory_usage": get_memory_usage(),
            "disk_usage": get_disk_usage()
        },
        "dependencies": {
            "database_latency_ms": await measure_database_latency(),
            "redis_latency_ms": await measure_redis_latency(),
            "ml_model_latency_ms": await measure_model_latency()
        },
        "business": {
            "cache_hit_rate": get_cache_hit_rate(),
            "error_rate": get_error_rate(),
            "average_response_time": get_avg_response_time()
        }
    }
    
    return checks
```

## Error Tracking

### Sentry Integration
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[
        FastApiIntegration(auto_enabling_integrations=False),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
)

# Custom error context
def add_recommendation_context(user_id, request):
    """Add context for error tracking"""
    sentry_sdk.set_user({"id": user_id})
    sentry_sdk.set_context("recommendation_request", {
        "location": f"{request.location.latitude},{request.location.longitude}",
        "radius_km": request.radius_km,
        "category": request.category,
        "limit": request.limit
    })
```

## Performance Profiling

### Continuous Profiling
```python
import pyflame
import py-spy

# CPU profiling for performance optimization
def profile_recommendation_pipeline():
    """Profile CPU usage in recommendation pipeline"""
    with pyflame.profile():
        # Run recommendation pipeline
        result = get_recommendations(request)
    
    # Analyze hotspots and optimize

# Memory profiling
@memory_profiler.profile
def analyze_memory_usage():
    """Profile memory usage patterns"""
    # Load features
    features = load_user_features()
    
    # ML inference
    predictions = model.predict(features)
    
    # Post-processing
    recommendations = post_process(predictions)
```