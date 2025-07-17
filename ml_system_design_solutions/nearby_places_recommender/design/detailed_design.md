# Detailed Design

## Component Architecture

### 1. API Gateway (Kong)
```
Responsibilities:
- SSL termination and certificate management
- Request authentication via JWT tokens
- Rate limiting: 1000 requests/hour per user
- Request/response transformation
- API versioning and routing
- Metrics collection and logging

Configuration:
- Load balancer with health checks
- Circuit breaker pattern for downstream services
- Request timeout: 30 seconds
- Retry policy: 3 attempts with exponential backoff
```

### 2. Recommendation Service
```
Components:
├── RecommendationController
│   └── Handles HTTP requests and response formatting
├── CandidateGenerator  
│   └── Geographic filtering + collaborative filtering
├── RankingEngine
│   └── ML model inference and scoring
├── PostProcessor
│   └── Business rules, diversity, and result formatting
└── FeatureEnricher
    └── Fetches user, place, and context features

Technology Stack:
- Framework: FastAPI with async/await
- ML Serving: TensorFlow Serving via gRPC
- Caching: Redis for feature caching
- Database: PostgreSQL connection pooling
```

### 3. Feature Store (Feast + Redis)
```
Architecture:
├── Offline Store (PostgreSQL)
│   ├── User historical features
│   ├── Place aggregate features  
│   └── Training dataset generation
├── Online Store (Redis)
│   ├── Real-time user features
│   ├── Place features
│   └── Context features
└── Feature Registry
    ├── Feature definitions and metadata
    ├── Data lineage tracking
    └── Feature validation rules

Feature Categories:
- User Features: age, preferences, interaction_history, location_history
- Place Features: category, rating, price, popularity, open_hours
- Context Features: time_of_day, day_of_week, weather, local_events
```

### 4. ML Pipeline (Apache Airflow)
```
DAGs (Directed Acyclic Graphs):
├── daily_feature_engineering
│   ├── Extract user interactions from Kafka
│   ├── Aggregate place statistics
│   ├── Generate negative samples for training
│   └── Update feature store
├── weekly_model_training
│   ├── Fetch training data from feature store
│   ├── Train candidate generation model
│   ├── Train ranking model
│   ├── Model validation and A/B testing
│   └── Model deployment to TensorFlow Serving
└── hourly_feature_refresh
    ├── Update real-time features in Redis
    ├── Refresh place business hours
    └── Update context features (weather, events)
```

### 5. User Service
```
Database Schema (PostgreSQL):
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    created_at TIMESTAMP,
    age_group VARCHAR(20),
    gender VARCHAR(10),
    preferences JSONB,
    location_settings JSONB
);

CREATE TABLE user_interactions (
    interaction_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    place_id BIGINT,
    interaction_type VARCHAR(20), -- view, click, visit, rate
    timestamp TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_user_interactions_user_time 
ON user_interactions(user_id, timestamp DESC);
```

### 6. Place Service
```
Database Schema (PostgreSQL with PostGIS):
CREATE TABLE places (
    place_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(50),
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    phone VARCHAR(20),
    business_hours JSONB,
    attributes JSONB,
    created_at TIMESTAMP
);

CREATE TABLE place_stats (
    place_id BIGINT REFERENCES places(place_id),
    rating DECIMAL(3,2),
    review_count INTEGER,
    price_level INTEGER,
    popularity_score DECIMAL(5,2),
    last_updated TIMESTAMP
);

-- Geospatial index for location queries
CREATE INDEX idx_places_location ON places USING GIST(location);
```

### 7. Location Service
```
Components:
├── LocationTracker
│   ├── Receives GPS updates from mobile apps
│   ├── Validates location accuracy
│   └── Publishes location events to Kafka
├── GeofenceManager
│   ├── Defines geographic boundaries
│   ├── Triggers events when users enter/exit areas
│   └── Manages location-based push notifications
└── PrivacyManager
    ├── Anonymizes precise coordinates
    ├── Applies geohashing for privacy
    └── Manages user consent preferences

Redis Geospatial Commands:
- GEOADD: Add user locations
- GEORADIUS: Find nearby users/places
- GEODIST: Calculate distances
```

## Data Models

### User Profile Model
```python
@dataclass
class UserProfile:
    user_id: int
    age_group: str  # "18-25", "26-35", etc.
    gender: Optional[str]
    preferences: Dict[str, float]  # category preferences
    dietary_restrictions: List[str]
    location_history: List[LocationPoint]
    interaction_history: List[Interaction]
    privacy_settings: PrivacySettings
```

### Place Model
```python
@dataclass
class Place:
    place_id: int
    name: str
    category: str
    subcategory: Optional[str]
    location: LocationPoint
    address: Address
    contact_info: ContactInfo
    business_hours: Dict[str, str]
    attributes: Dict[str, Any]  # WiFi, parking, etc.
    stats: PlaceStats
    metadata: PlaceMetadata
```

### Recommendation Response
```python
@dataclass
class RecommendationResponse:
    recommendations: List[PlaceRecommendation]
    metadata: ResponseMetadata
    
@dataclass
class PlaceRecommendation:
    place: Place
    score: float
    rank: int
    explanation: str
    distance_km: float
    estimated_time_minutes: int
```

## API Design

### Core Endpoints
```
GET /api/v1/recommendations/nearby
Parameters:
- lat: float (required)
- lng: float (required)  
- radius_km: float = 5.0
- category: str = null
- limit: int = 20
- user_id: int (from auth token)

Response:
{
  "recommendations": [...],
  "metadata": {
    "total_count": 150,
    "search_radius_km": 5.0,
    "response_time_ms": 85,
    "model_version": "v2.1.3"
  }
}
```

### Feedback Endpoints
```
POST /api/v1/interactions
Body:
{
  "user_id": 12345,
  "place_id": 67890,
  "interaction_type": "click",
  "context": {
    "recommendation_id": "abc123",
    "position": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Security Design

### Authentication & Authorization
- **OAuth 2.0 + JWT**: Token-based authentication
- **Scope-based permissions**: Read/write access control
- **Rate limiting**: Per-user and per-IP limits
- **API key management**: For partner integrations

### Data Protection
- **Encryption**: AES-256 for PII, TLS 1.3 for transport
- **Data masking**: Hide sensitive fields in logs
- **Access logging**: Audit trail for all data access
- **Privacy compliance**: GDPR/CCPA data handling

## Deployment Architecture

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-service
spec:
  replicas: 6
  selector:
    matchLabels:
      app: recommendation-service
  template:
    spec:
      containers:
      - name: recommendation-service
        image: recommendation-service:v2.1.3
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi" 
            cpu: "2000m"
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
```

### Load Balancing Strategy
- **Geographic routing**: Route to nearest data center
- **Weighted round-robin**: Distribute load based on capacity
- **Health checks**: Remove unhealthy instances automatically
- **Auto-scaling**: Scale based on CPU/memory and request queue length