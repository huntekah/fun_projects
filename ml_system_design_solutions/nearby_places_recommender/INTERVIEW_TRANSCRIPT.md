# Interview Transcript: Nearby Places Recommender System

*This is a comprehensive interview transcript for designing a nearby places recommendation system, similar to what you'd find in Yelp, Google Maps, or Foursquare.*

---

## **Interviewer**: "Design a nearby places recommender system that suggests relevant places to users based on their location and preferences."

## **Candidate**: 

Thank you for the interesting problem. Before I dive into the design, I'd like to clarify a few key aspects to ensure I'm building the right system.

### **1. Problem Clarification & Requirements**

**Candidate**: Let me start with some clarifying questions:

**Business Objective**: What's the primary goal? Are we optimizing for user engagement (clicks, time spent), commercial outcomes (reservations, calls to businesses), or discovery of new places? 

*Let's assume we're optimizing for user engagement while helping users discover relevant places.*

**Platform & Context**: Is this for mobile apps, web, or both? Given "nearby" implies location-based recommendations, I'll assume primarily mobile with real-time GPS access.

**Scope of Places**: What types of places - restaurants, retail, entertainment, all POIs? I'll design for a general system covering all Points of Interest.

**Definition of "Nearby"**: Fixed radius or contextual? A 1km radius means different things in Manhattan vs rural areas. I'll assume dynamic, context-aware proximity.

**Scale**: What's the expected scale? I'll design for large scale: 100M DAU, 50M places globally, similar to a FAANG-level service.

### **2. Functional Requirements**

Based on our discussion, here are the core functional requirements:

✅ **Location-based Discovery**: Find places within configurable radius (default 5km, max 50km)
✅ **Personalized Recommendations**: Rank places based on user preferences and history  
✅ **Real-time Context**: Consider time of day, weather, business hours
✅ **Search & Filtering**: Filter by category, price, rating, distance
✅ **User Interactions**: Support views, clicks, ratings, saves, check-ins
✅ **Place Management**: Add new places, update business information

### **3. Non-Functional Requirements**

**Performance**: 
- API response time: <100ms P95
- Support 10K QPS peak, 3K average
- 500K concurrent users

**Scale**:
- 100M monthly active users
- 50M places worldwide  
- 1B interactions per day

**Availability**: 99.9% uptime with graceful degradation
**Consistency**: Eventually consistent for place updates, strong consistency for user interactions

### **4. Capacity Estimation**

Let me do some back-of-the-envelope calculations:

**Traffic**:
- 100M MAU × 0.3 daily activity = 30M DAU
- 30M DAU × 5 sessions/day = 150M sessions/day
- 150M sessions × 3 recommendations = 450M requests/day
- Peak QPS: 450M / 86400 × 3 (peak factor) ≈ 15K QPS

**Storage**:
- Places: 50M × 2KB metadata = 100GB
- User profiles: 100M × 1KB = 100GB  
- Interactions: 1B/day × 365 days × 500 bytes = 180TB annually
- Features: 100GB hot features in Redis

**Infrastructure**:
- API servers: 20 instances (2 cores, 4GB each)
- ML inference: 10 GPU instances (V100/A100)
- Feature store: 6 Redis instances (500GB total)
- Database: 3 PostgreSQL instances (primary + 2 replicas)

## **Interviewer**: "That's a good start. Now walk me through your high-level architecture."

## **Candidate**:

### **5. High-Level System Architecture**

I'll use a **two-stage recommendation architecture** - this is the industry standard for large-scale recommender systems as it balances latency and quality.

```
[Mobile Apps] → [API Gateway] → [Recommendation Service]
                                        ↓
[Feature Store] ← [ML Pipeline] → [Candidate Generation] → [Ranking Engine]
        ↓                              ↓                       ↓
[User/Place/Context Features]    [~500 candidates]    [Top 20 ranked results]
        ↓                              ↓                       ↓
[PostgreSQL + Redis]           [Geospatial + ML]         [Business Rules]
```

**Stage 1: Candidate Generation** (~10-20ms)
- **Geospatial Filtering**: Redis geospatial queries for nearby places within radius
- **Collaborative Filtering**: Two-tower model generating user/place embeddings, ANN search for similar preferences
- **Business Rules**: Include trending, new, or sponsored places
- **Output**: ~500 candidate places

**Stage 2: Ranking** (~30-50ms)  
- **Feature Enrichment**: Fetch user, place, and context features from feature store
- **ML Ranking**: Wide & Deep model scoring all candidates
- **Post-processing**: Apply diversity, business rules, filtering
- **Output**: Top 20 ranked recommendations

**Supporting Services**:
- **Feature Store**: Redis for real-time features, PostgreSQL for historical
- **Geospatial Index**: Redis GEORADIUS for efficient location queries
- **ML Pipeline**: Airflow for training, MLflow for experimentation
- **API Gateway**: Authentication, rate limiting, load balancing

## **Interviewer**: "Interesting. Can you dive deeper into the ML models you'd use?"

## **Candidate**:

### **6. Machine Learning Architecture**

**Candidate Generation Model: Two-Tower Architecture**

```python
# User Tower
user_features = [user_id, age_group, preferences, interaction_history]
user_embedding = embedding_layer(user_features) → dense_layers → user_vector(64d)

# Place Tower  
place_features = [place_id, category, rating, price_level]
place_embedding = embedding_layer(place_features) → dense_layers → place_vector(64d)

# Similarity Score
score = dot_product(user_vector, place_vector)
```

**Training**: Use positive pairs (user clicked/visited place) vs negative samples. Optimize with contrastive loss to maximize similarity for positive pairs.

**Ranking Model: Wide & Deep Architecture**

```python
# Wide Component (Linear)
wide_features = [distance, price_difference, category_affinity]
wide_output = linear_layer(wide_features)

# Deep Component (Neural Network)  
deep_features = [user_embedding, place_embedding, context_features]
deep_output = dense_layers([256, 128, 64]) → output

# Combined Score
final_score = wide_output + deep_output → sigmoid → P(click)
```

**Key Features**:
- **User**: age_group, historical_categories, avg_rating_given, location_history
- **Place**: category, rating, review_count, price_level, popularity_score  
- **Context**: distance, hour_of_day, weather, is_weekend
- **Cross**: user_category_affinity, embedding_similarity

**Training Data**: User interaction logs (clicks=1, non-clicks=0) with 1:4 positive:negative ratio

## **Interviewer**: "How would you handle the geospatial aspects efficiently?"

## **Candidate**:

### **7. Geospatial Design**

**Primary Approach: Redis Geospatial**

```python
# Add places to geospatial index
GEOADD places_geo [lng] [lat] [place_id]

# Find nearby places
GEORADIUS places_geo [user_lng] [user_lat] 5 km 
    WITHCOORD WITHDIST ASC COUNT 500
```

**Benefits**: Sub-millisecond queries, built-in distance calculation, easy integration

**Alternative: PostGIS for Complex Queries**

```sql
-- For more complex spatial operations
SELECT place_id, ST_Distance(location, ST_Point(?, ?)) as distance 
FROM places 
WHERE ST_DWithin(location, ST_Point(?, ?), 5000)
ORDER BY distance LIMIT 500;
```

**Geospatial Partitioning Strategy**:
- **By Region**: Partition data by country/state for better cache locality
- **S2 Cells**: Use Google's S2 library for hierarchical spatial indexing
- **Hot Spot Handling**: Replicate popular urban areas across multiple nodes

**Optimization Techniques**:
- **Precomputed Grids**: Cache popular locations in geographic grids
- **Multi-level Caching**: L1 (app), L2 (Redis), L3 (PostGIS)
- **Edge Deployment**: Deploy geospatial indices closer to users

## **Interviewer**: "What about your data models and APIs?"

## **Candidate**:

### **8. Data Models & API Design**

**Core Data Models**:

```python
# User Profile
class User:
    user_id: int
    age_group: str
    preferences: Dict[category, weight]
    home_location: LocationPoint
    privacy_settings: PrivacySettings

# Place Entity  
class Place:
    place_id: int
    name: str
    category: PlaceCategory
    location: LocationPoint
    rating: float
    price_level: int
    business_hours: BusinessHours
    attributes: Dict[str, Any]

# User Interaction
class Interaction:
    user_id: int
    place_id: int
    interaction_type: InteractionType  # view, click, visit, rate
    timestamp: datetime
    context: InteractionContext
```

**API Endpoints**:

```http
# Get Recommendations
GET /api/v1/recommendations/nearby
Parameters: lat, lng, radius_km=5, category, limit=20
Response: {recommendations: [...], metadata: {...}}

# Log Interaction
POST /api/v1/interactions
Body: {place_id, interaction_type, rating, context}

# Place Details
GET /api/v1/places/{place_id}
Response: {place_info, reviews, photos, business_hours}
```

**Database Schema**:

```sql
-- Places table with geospatial index
CREATE TABLE places (
    place_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(50),
    location GEOGRAPHY(POINT, 4326),
    rating DECIMAL(3,2),
    created_at TIMESTAMP
);
CREATE INDEX idx_places_location ON places USING GIST(location);

-- User interactions partitioned by time
CREATE TABLE user_interactions (
    user_id BIGINT,
    place_id BIGINT,
    interaction_type VARCHAR(20),
    timestamp TIMESTAMP,
    metadata JSONB
) PARTITION BY RANGE (timestamp);
```

## **Interviewer**: "How would you scale this system to handle 10x more traffic?"

## **Candidate**:

### **9. Scaling Strategies**

**Horizontal Scaling Approach**:

**API Layer**:
- **Current**: 20 instances (10K QPS)
- **10x Scale**: 200 instances (100K QPS)
- **Auto-scaling**: CPU-based (70%) + request queue length
- **Load Balancing**: Geographic routing to nearest data center

**ML Inference**:
- **Current**: 10 GPU instances  
- **10x Scale**: 100 A100 instances
- **Optimization**: Model quantization (INT8) for 3x speedup
- **Batching**: Dynamic batching with 10ms max wait time

**Database Scaling**:
- **Read Replicas**: Scale from 3 to 9 instances (3 regions × 3 replicas)
- **Sharding**: Partition by user_id hash for interactions
- **Caching**: Scale Redis from 6 to 18 instances (5TB total)

**Geospatial Scaling**:
- **Geographic Partitioning**: Separate indices per region/country  
- **Hot Spot Replication**: 3x replicas for dense urban areas
- **Edge Caching**: Deploy Redis clusters in 10+ edge locations

**Feature Store Scaling**:
- **Streaming Pipeline**: Kafka + Flink for real-time feature updates
- **Tiered Storage**: Hot (Redis), Warm (SSD), Cold (S3)
- **Precomputation**: Background jobs for expensive feature aggregations

**Potential Bottlenecks & Solutions**:

1. **ML Inference Latency** (40ms → target 20ms)
   - Model distillation: Student model 50% smaller
   - GPU optimization: TensorRT for inference acceleration
   - Feature caching: Pre-compute user embeddings

2. **Database Connection Pool** (90% utilization)
   - Connection pooling: PgBouncer with 1000 max connections
   - Query optimization: Materialized views for aggregations
   - Async patterns: Non-blocking database queries

3. **Feature Store Latency** (15ms → target 5ms)
   - Memory optimization: Sparse feature representations
   - Batch fetching: Group feature requests by user/place
   - Locality**: Co-locate features with compute

## **Interviewer**: "What about handling edge cases and operational concerns?"

## **Candidate**:

### **10. Edge Cases & Operational Excellence**

**Cold Start Problems**:

**New Users**:
- **Fallback**: Popularity-based recommendations by location + time
- **Quick Learning**: Onboarding flow to capture initial preferences  
- **Contextual Signals**: Device type, time of day, location patterns
- **Exploration**: Multi-armed bandit for preference discovery

**New Places**:
- **Content-based**: Use category, description, photos for initial embedding
- **Exploration Boost**: Slight ranking boost for new places to gather data
- **Human Curation**: Editorial recommendations for quality new places

**Operational Monitoring**:

**Business Metrics**:
- **CTR**: 15% target (currently 12.8%)
- **Conversion Rate**: 8% target (currently 6.2%)
- **Diversity**: Shannon entropy >0.7 across categories
- **Coverage**: >60% of places recommended weekly

**Technical Metrics**:
- **Latency**: P95 <100ms (currently 85ms)
- **Availability**: 99.9% uptime
- **Cache Hit Rate**: >75% (currently 72%)

**ML Model Health**:
- **Model Drift**: PSI score <0.1 (Population Stability Index)
- **Feature Freshness**: <5 minutes lag for real-time features
- **A/B Testing**: Continuous experimentation framework

**Alerting Strategy**:
- **Critical**: Service down, high error rate (>0.5%), high latency (>150ms)
- **Warning**: Model drift, low CTR, cache performance degradation
- **Info**: Deployment events, auto-scaling activities

**Fault Tolerance**:
- **Circuit Breakers**: Fail-fast for downstream services (3 failures → 60s breaker)
- **Graceful Degradation**: Fall back to popularity-based ranking if ML fails
- **Multi-region**: Active-active deployment across 3 regions
- **Disaster Recovery**: 4-hour RTO, 1-hour RPO for critical data

### **11. Trade-offs & Alternative Approaches**

**Architecture Alternatives**:

**Single-stage Deep Learning**: 
- *Pros*: End-to-end optimization, no information loss
- *Cons*: Expensive inference, harder to scale to 50M places
- *Decision*: Two-stage chosen for scalability

**Technology Alternatives**:

**NoSQL vs PostgreSQL**:
- *Considered*: DynamoDB for scale, MongoDB for flexibility
- *Chosen*: PostgreSQL for ACID guarantees, rich geospatial support (PostGIS)
- *Trade-off*: Consistency over pure scalability

**Kafka vs SQS**:
- *Considered*: Amazon SQS for simplicity
- *Chosen*: Kafka for high throughput, exactly-once semantics
- *Trade-off*: Operational complexity for performance

**Caching Strategy**:
- *Alternative*: Single Redis layer
- *Chosen*: Multi-level (L1: app, L2: Redis, L3: DB)
- *Trade-off*: Complexity for optimal latency

### **12. Future Improvements**

**Short-term (3-6 months)**:
- Model quantization for 3x inference speedup
- Real-time event integration (concerts, festivals)
- Advanced negative sampling for better training

**Medium-term (6-12 months)**:
- Graph Neural Networks for user-place relationships
- Multi-task learning (CTR + conversion + satisfaction)
- Federated learning for privacy-preserving personalization

**Long-term (1-2 years)**:
- Transformer-based sequential recommendation
- Reinforcement learning for long-term engagement
- Multi-modal learning (images, text, audio)

## **Interviewer**: "Excellent! Any final thoughts on this design?"

## **Candidate**:

### **13. Summary & Key Design Principles**

This design balances several key principles:

**Scalability**: Two-stage architecture scales to 100M+ users and 50M+ places
**Performance**: <100ms latency through intelligent caching and model optimization  
**Personalization**: Rich ML models with 100+ features for relevant recommendations
**Reliability**: 99.9% availability through multi-region deployment and graceful degradation
**Extensibility**: Modular design allows easy addition of new features and models

**Key Technical Decisions**:
1. **Two-stage ML**: Candidate generation (efficiency) + ranking (accuracy)
2. **Redis Geospatial**: Sub-millisecond location queries
3. **Multi-level Caching**: Optimal latency-memory trade-off
4. **Feature Store**: Centralized feature management for ML
5. **Microservices**: Independent scaling and technology diversity

**Success Metrics**:
- **User Engagement**: 25% increase in session duration
- **Business Impact**: 15% increase in recommendation-driven revenue
- **Technical Excellence**: Sub-50ms P95 latency, 99.99% availability

This system provides a solid foundation for a world-class nearby places recommendation platform that can scale globally while delivering personalized, relevant results to users.

---

*This completes a comprehensive system design interview for a nearby places recommender system, covering all major aspects from requirements gathering to implementation details, scaling strategies, and operational considerations.*