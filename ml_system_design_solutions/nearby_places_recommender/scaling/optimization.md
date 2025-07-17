# Performance Optimization Strategies

## ML Model Optimizations

### Model Quantization
```python
# Convert FP32 model to INT8 for 3x speedup
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_saved_model('model/')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.int8]

# Representative dataset for calibration
def representative_dataset():
    for sample in calibration_data:
        yield [sample.astype(np.float32)]

converter.representative_dataset = representative_dataset
quantized_model = converter.convert()
```

### Batch Inference Optimization
```python
class BatchInferenceOptimizer:
    def __init__(self, max_batch_size=64, max_wait_ms=10):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_requests = []
        
    async def predict(self, features):
        # Accumulate requests for batching
        future = asyncio.Future()
        self.pending_requests.append((features, future))
        
        if len(self.pending_requests) >= self.max_batch_size:
            await self._process_batch()
            
        return await future
    
    async def _process_batch(self):
        if not self.pending_requests:
            return
            
        # Extract features and futures
        batch_features = []
        futures = []
        
        for features, future in self.pending_requests:
            batch_features.append(features)
            futures.append(future)
            
        # Batch inference
        batch_predictions = await self.model.predict(
            np.array(batch_features)
        )
        
        # Return results
        for future, prediction in zip(futures, batch_predictions):
            future.set_result(prediction)
            
        self.pending_requests.clear()
```

### Model Distillation
```python
# Teacher-student distillation for model compression
def create_student_model(teacher_model, compression_ratio=0.5):
    """Create smaller student model"""
    student = tf.keras.Sequential([
        tf.keras.layers.Dense(
            int(teacher_model.layers[0].units * compression_ratio),
            activation='relu'
        ),
        tf.keras.layers.Dense(
            int(teacher_model.layers[1].units * compression_ratio), 
            activation='relu'
        ),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    return student

def distillation_loss(y_true, y_pred, teacher_pred, temperature=3.0, alpha=0.7):
    """Combined loss for distillation"""
    # Hard target loss
    hard_loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    
    # Soft target loss (knowledge distillation)
    soft_loss = tf.keras.losses.KLDivergence()(
        tf.nn.softmax(teacher_pred / temperature),
        tf.nn.softmax(y_pred / temperature)
    )
    
    return alpha * soft_loss + (1 - alpha) * hard_loss
```

## Caching Optimizations

### Multi-Level Caching Strategy
```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory (1000 items)
        self.l2_cache = Redis()  # Redis (100K items)
        self.l3_cache = PostgreSQL()  # Database (persistent)
        
    async def get(self, key):
        # L1: Application cache
        if key in self.l1_cache:
            return self.l1_cache[key]
            
        # L2: Redis cache  
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value  # Populate L1
            return value
            
        # L3: Database fallback
        value = await self.l3_cache.get(key)
        if value:
            await self.l2_cache.set(key, value, ttl=300)  # Populate L2
            self.l1_cache[key] = value  # Populate L1
            
        return value
```

### Intelligent Cache Warming
```python
# Pre-compute popular recommendations
async def warm_cache_for_popular_locations():
    """Pre-compute recommendations for high-traffic areas"""
    popular_locations = await get_popular_locations()
    
    for location in popular_locations:
        # Pre-compute for different user segments
        for user_segment in ['young_professionals', 'families', 'tourists']:
            request = RecommendationRequest(
                user_id=get_representative_user(user_segment),
                location=location,
                radius_km=5.0
            )
            
            # Warm cache
            await inference_pipeline.get_recommendations(request)
```

## Database Optimizations

### Query Optimization
```sql
-- Optimized geospatial query with proper indexing
CREATE INDEX CONCURRENTLY idx_places_location_category 
ON places USING GIST(location, category);

-- Partitioned user interactions table
CREATE TABLE user_interactions_y2024m01 
PARTITION OF user_interactions 
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for aggregated features
CREATE MATERIALIZED VIEW place_stats_hourly AS
SELECT 
    place_id,
    date_trunc('hour', timestamp) as hour,
    count(*) as visit_count,
    avg(rating) as avg_rating
FROM user_interactions 
WHERE timestamp >= current_date - interval '7 days'
GROUP BY place_id, date_trunc('hour', timestamp);

-- Refresh materialized views
REFRESH MATERIALIZED VIEW CONCURRENTLY place_stats_hourly;
```

### Connection Pool Optimization
```python
# Optimized connection pool configuration
DATABASE_CONFIG = {
    'min_size': 10,
    'max_size': 50,
    'max_queries': 50000,
    'max_inactive_connection_lifetime': 300,
    'command_timeout': 5,
    'server_settings': {
        'shared_preload_libraries': 'pg_stat_statements',
        'max_connections': 200,
        'shared_buffers': '8GB',
        'work_mem': '256MB',
        'maintenance_work_mem': '1GB'
    }
}
```

## Feature Engineering Optimizations

### Sparse Feature Representations
```python
from scipy.sparse import csr_matrix

class SparseFeatureStore:
    def __init__(self):
        self.feature_matrices = {}
        
    def store_user_features(self, user_id, features):
        """Store user features as sparse matrix"""
        # Convert dense features to sparse
        feature_indices = []
        feature_values = []
        
        for i, value in enumerate(features):
            if value != 0:  # Only store non-zero values
                feature_indices.append(i)
                feature_values.append(value)
                
        sparse_features = csr_matrix(
            (feature_values, ([0] * len(feature_values), feature_indices)),
            shape=(1, len(features))
        )
        
        self.feature_matrices[user_id] = sparse_features
```

### Feature Streaming Pipeline
```python
# Kafka streaming for real-time feature updates
from kafka import KafkaProducer, KafkaConsumer

class FeatureStreaming:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    async def stream_user_interaction(self, interaction):
        """Stream interaction for real-time feature updates"""
        feature_update = {
            'user_id': interaction.user_id,
            'place_id': interaction.place_id,
            'feature_type': 'interaction_count',
            'increment': 1,
            'timestamp': interaction.timestamp.isoformat()
        }
        
        self.producer.send('user_features', feature_update)
```

## Network and Infrastructure Optimizations

### CDN and Edge Caching
```yaml
# CloudFlare CDN configuration
cdn_config:
  cache_rules:
    - pattern: "/api/v1/places/*"
      ttl: 3600  # 1 hour for place details
      
    - pattern: "/api/v1/recommendations*"
      ttl: 300   # 5 minutes for recommendations
      cache_key: "${user_segment}_${lat_lng_grid}_${category}"
      
  edge_functions:
    - name: "geo_routing"
      code: |
        // Route users to nearest data center
        const region = getRegionFromIP(request.cf.colo);
        const datacenter = getClosestDatacenter(region);
        return fetch(request, { cf: { cacheEverything: true } });
```

### Compression and Serialization
```python
# Optimized serialization for API responses
import orjson  # Faster JSON serialization
import gzip
import brotli

class OptimizedSerializer:
    def serialize_response(self, data, accept_encoding=None):
        """Optimized serialization with compression"""
        # Use orjson for faster serialization
        json_data = orjson.dumps(data)
        
        # Apply compression based on Accept-Encoding
        if 'br' in accept_encoding:
            return brotli.compress(json_data), 'br'
        elif 'gzip' in accept_encoding:
            return gzip.compress(json_data), 'gzip'
        else:
            return json_data, None
```

## Monitoring and Alerting Optimizations

### Performance Metrics Collection
```python
# Efficient metrics collection
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('recommendations_requests_total', 
                       'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('recommendations_request_duration_seconds',
                           'Request latency')
CACHE_HIT_RATE = Gauge('recommendations_cache_hit_rate', 
                      'Cache hit rate percentage')

# Model metrics  
MODEL_INFERENCE_TIME = Histogram('model_inference_duration_seconds',
                                'Model inference time')
MODEL_ACCURACY = Gauge('model_accuracy', 'Model accuracy score')

# Business metrics
RECOMMENDATION_CTR = Gauge('recommendation_click_through_rate',
                          'Recommendation CTR')
```

### Adaptive Scaling Policies
```yaml
# Kubernetes HPA with custom metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recommendation-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-service
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: request_latency_p95
      target:
        type: AverageValue
        averageValue: "100m"  # 100ms
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent  
        value: 50
        periodSeconds: 60
```