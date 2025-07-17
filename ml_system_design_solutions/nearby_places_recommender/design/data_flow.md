# Data Flow Design

## Overall Data Architecture

```
Data Sources → Ingestion → Processing → Storage → Serving → Analytics
     ↓            ↓           ↓          ↓         ↓          ↓
[Mobile Apps] → [Kafka] → [Spark] → [PostgreSQL] → [API] → [Snowflake]
[Web Apps]    → [Kinesis] → [Flink] → [Redis]     → [Cache] → [DataDog]
[3rd Party]   → [Batch]   → [Airflow] → [S3]     → [CDN]   → [Tableau]
```

## 1. Data Ingestion Flow

### Real-time Event Streaming
```
Mobile/Web Apps → API Gateway → Kafka → Stream Processing → Feature Store
                     ↓             ↓          ↓               ↓
                [Validation] → [Partitioning] → [Enrichment] → [Storage]
                [Rate Limit]   [Load Balance]   [Transform]   [Indexing]
```

#### Event Schema
```json
{
  "event_type": "user_interaction",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 12345,
  "session_id": "abc123xyz",
  "data": {
    "interaction_type": "place_view",
    "place_id": 67890,
    "location": {
      "lat": 37.7749,
      "lng": -122.4194,
      "accuracy": 10
    },
    "context": {
      "search_query": "italian restaurant",
      "recommendation_id": "rec_456",
      "position_in_results": 3,
      "device_type": "mobile",
      "app_version": "2.1.3"
    }
  }
}
```

#### Kafka Configuration
```yaml
# Kafka topics and partitioning strategy
topics:
  user-interactions:
    partitions: 24  # Partitioned by user_id hash
    replication: 3
    retention: 7_days
    
  place-updates:
    partitions: 12  # Partitioned by place_id hash
    replication: 3
    retention: 30_days
    
  location-events:
    partitions: 36  # High volume, partitioned by geographic region
    replication: 3
    retention: 1_day
```

### Batch Data Ingestion
```
External APIs → ETL Pipeline → Data Lake → Data Warehouse → Feature Store
     ↓              ↓            ↓           ↓              ↓
[Foursquare] → [Airflow] → [S3] → [Snowflake] → [PostgreSQL]
[Yelp API]     [Spark]     [Parquet] [dbt]      [Redis]
[Google Maps]  [Glue]      [Delta]   [SQL]      [Feast]
```

## 2. Stream Processing Flow

### Real-time Feature Engineering (Apache Flink)
```python
# Flink streaming job for real-time user features
def process_user_interactions(stream):
    return (stream
        .key_by('user_id')
        .window(TumblingEventTimeWindows.of(Time.minutes(10)))
        .aggregate(UserFeatureAggregator())
        .map(lambda x: update_redis_features(x))
    )

class UserFeatureAggregator:
    def aggregate(self, interactions):
        return {
            'user_id': interactions[0].user_id,
            'recent_categories': Counter([i.place_category for i in interactions]),
            'interaction_count': len(interactions),
            'avg_rating': mean([i.rating for i in interactions if i.rating]),
            'last_location': interactions[-1].location,
            'session_duration': (interactions[-1].timestamp - interactions[0].timestamp).seconds
        }
```

### Event Processing Pipeline
```
Raw Events → Validation → Enrichment → Aggregation → Feature Store
     ↓           ↓           ↓            ↓             ↓
[JSON]    → [Schema]   → [Join]     → [Window]   → [Redis]
[Kafka]     [Validate]   [Lookup]     [Tumble]     [Update]
[Stream]    [Filter]     [GeoCode]    [Session]    [Notify]
```

## 3. Batch Processing Flow

### Daily Feature Engineering (Apache Spark)
```python
# Spark job for daily batch feature computation
def daily_feature_pipeline():
    # 1. Extract interactions from last 24 hours
    interactions = spark.read.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "user-interactions") \
        .option("startingOffsets", "earliest") \
        .load()
    
    # 2. Compute user aggregate features
    user_features = compute_user_daily_features(interactions)
    
    # 3. Compute place aggregate features  
    place_features = compute_place_daily_features(interactions)
    
    # 4. Write to feature store
    write_to_feature_store(user_features, place_features)
    
    # 5. Update ML training dataset
    update_training_data(interactions)
```

### Data Lineage Flow
```
Source Data → Transformation → Intermediate → Final Features → Model Training
     ↓             ↓              ↓              ↓              ↓
[Raw Events] → [Clean/Filter] → [Aggregate] → [Feature Store] → [MLflow]
[Metadata]     [Validate]       [Join]        [Versioned]      [Tracking]
[Quality]      [Enrich]         [Window]      [Monitored]      [Registry]
```

## 4. Feature Store Data Flow

### Feature Store Architecture
```
Offline Features (PostgreSQL) ←→ Feature Registry ←→ Online Features (Redis)
         ↑                             ↑                       ↑
    [Batch ETL]                  [Metadata]              [Stream Updates]
    [Training Data]              [Lineage]               [Real-time Serving]
    [Historical]                 [Validation]            [Low Latency]
```

### Feature Serving Flow
```python
# Feature retrieval for real-time inference
async def get_features_for_inference(user_id, place_ids, context):
    # Get user features from Redis (real-time)
    user_features = await redis_client.hgetall(f"user_features:{user_id}")
    
    # Get place features from Redis (batch updated)
    place_features = await redis_client.hmget(
        f"place_features", 
        [f"place:{pid}" for pid in place_ids]
    )
    
    # Compute context features on-the-fly
    context_features = compute_context_features(
        location=context.location,
        timestamp=context.timestamp,
        weather_api_response=await get_weather(context.location)
    )
    
    return combine_features(user_features, place_features, context_features)
```

## 5. Model Training Data Flow

### Training Data Pipeline
```
Feature Store → Data Sampling → Label Generation → Model Training → Model Registry
      ↓              ↓              ↓                 ↓               ↓
[Historical] → [Positive/Negative] → [Join] → [Train/Validate] → [Version]
[Features]     [Time Windows]       [Labels]   [Hyperparameter]   [Deploy]
[Snapshots]    [Stratified]         [Clean]    [Cross-validation] [A/B Test]
```

### Training Dataset Generation
```sql
-- Generate training samples with labels
WITH positive_samples AS (
  SELECT 
    ui.user_id,
    ui.place_id,
    1 as label,
    ui.timestamp
  FROM user_interactions ui
  WHERE ui.interaction_type IN ('visit', 'rating')
    AND ui.rating >= 3
    AND ui.timestamp >= CURRENT_DATE - INTERVAL '30 days'
),
negative_samples AS (
  -- Random negative sampling
  SELECT 
    u.user_id,
    p.place_id,
    0 as label,
    CURRENT_TIMESTAMP as timestamp
  FROM users u 
  CROSS JOIN places p
  WHERE NOT EXISTS (
    SELECT 1 FROM user_interactions ui2 
    WHERE ui2.user_id = u.user_id 
    AND ui2.place_id = p.place_id
  )
  ORDER BY RANDOM()
  LIMIT (SELECT COUNT(*) * 4 FROM positive_samples)  -- 1:4 ratio
)
SELECT * FROM positive_samples
UNION ALL
SELECT * FROM negative_samples;
```

## 6. Real-time Serving Data Flow

### Recommendation Request Flow
```
Client Request → API Gateway → Recommendation Service → Feature Store → ML Model
      ↓              ↓                ↓                    ↓              ↓
[HTTP/JSON] → [Auth/Rate Limit] → [Orchestration] → [Feature Fetch] → [Inference]
[Mobile App]   [Load Balance]     [Caching]         [Redis/Postgres]  [TF Serving]
[Web App]      [Monitoring]       [Logging]         [Context Enrich]  [Post-process]
```

### Caching Strategy
```python
# Multi-level caching for recommendation serving
class RecommendationCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory (application level)
        self.l2_cache = Redis()  # Redis (cluster level)
        self.l3_cache = CDN()  # CDN (global level)
    
    async def get_recommendations(self, cache_key):
        # L1: Check application cache (fastest)
        if cache_key in self.l1_cache:
            return self.l1_cache[cache_key]
        
        # L2: Check Redis cache
        result = await self.l2_cache.get(cache_key)
        if result:
            self.l1_cache[cache_key] = result  # Populate L1
            return result
        
        # L3: Check CDN cache for popular queries
        if is_popular_query(cache_key):
            result = await self.l3_cache.get(cache_key)
            if result:
                await self.l2_cache.set(cache_key, result, ttl=300)
                self.l1_cache[cache_key] = result
                return result
        
        return None  # Cache miss - compute recommendations
```

## 7. Analytics and Monitoring Data Flow

### Metrics Collection Flow
```
Application Metrics → Monitoring System → Alerting → Dashboard
        ↓                   ↓               ↓          ↓
[Custom Metrics] → [Prometheus] → [AlertManager] → [Grafana]
[Business KPIs]    [DataDog]      [PagerDuty]     [Tableau]
[ML Metrics]       [CloudWatch]   [Slack]         [Custom UI]
```

### Data Warehouse Flow
```python
# Daily ETL to data warehouse
def daily_analytics_pipeline():
    # Extract from operational databases
    interactions = extract_from_postgres("user_interactions")
    recommendations = extract_from_postgres("recommendation_logs")
    features = extract_from_redis("feature_snapshots")
    
    # Transform for analytics
    fact_recommendations = transform_recommendations(interactions, recommendations)
    dim_users = transform_user_dimensions()
    dim_places = transform_place_dimensions()
    
    # Load to Snowflake
    load_to_warehouse(fact_recommendations, "fact_recommendations")
    load_to_warehouse(dim_users, "dim_users")
    load_to_warehouse(dim_places, "dim_places")
```

## 8. Data Quality and Governance

### Data Validation Flow
```
Raw Data → Schema Validation → Quality Checks → Data Lineage → Governance
    ↓            ↓                 ↓              ↓              ↓
[Ingestion] → [Great Expectations] → [Anomaly] → [Apache Atlas] → [Catalog]
[Stream]      [JSON Schema]         [Detection] [Lineage Graph] [Privacy]
[Batch]       [Type Checking]       [Alerts]    [Dependencies]  [Compliance]
```

### Privacy and Compliance Flow
```python
# Data privacy pipeline
def apply_privacy_controls(data):
    # 1. PII detection and masking
    pii_fields = detect_pii(data)
    masked_data = mask_sensitive_fields(data, pii_fields)
    
    # 2. Geographic privacy (location fuzzing)
    if 'location' in data:
        data['location'] = apply_geohashing(data['location'], precision=7)
    
    # 3. User consent validation
    if not has_consent(data['user_id'], 'location_tracking'):
        data = remove_location_data(data)
    
    # 4. Data retention enforcement
    if is_expired(data['timestamp'], retention_policy):
        schedule_for_deletion(data)
    
    return masked_data
```

This data flow design ensures:
- **Real-time responsiveness** with stream processing
- **Batch processing scalability** with Spark/Airflow
- **Feature consistency** across training and serving
- **Data quality** with validation and monitoring
- **Privacy compliance** with automated controls
- **Analytics capabilities** with data warehouse integration