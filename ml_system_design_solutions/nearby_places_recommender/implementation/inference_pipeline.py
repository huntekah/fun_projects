"""
Inference Pipeline for Nearby Places Recommendation System

This module implements the real-time inference pipeline for serving
recommendations to users, including feature fetching, model inference,
and post-processing.
"""

import asyncio
import logging
import pickle
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import hashlib

import numpy as np
import tensorflow as tf
import redis
import asyncpg
from sklearn.preprocessing import StandardScaler, LabelEncoder

from data_models import (
    LocationPoint, RecommendationRequest, RecommendationResponse,
    PlaceRecommendation, RecommendationMetadata, RecommendationExplanation,
    Place, PlaceCategory, UserFeatures, PlaceFeatures, ContextFeatures
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InferenceConfig:
    """Configuration for inference pipeline"""
    # Model serving
    model_url: str = "http://tensorflow-serving:8501/v1/models/recommendation:predict"
    model_version: str = "v2.1.3"
    
    # Feature store
    redis_host: str = "redis-cluster"
    redis_port: int = 6379
    postgres_host: str = "postgres-primary"
    postgres_port: int = 5432
    postgres_db: str = "recommendations"
    
    # Caching
    cache_ttl_seconds: int = 300  # 5 minutes
    enable_l1_cache: bool = True
    l1_cache_size: int = 1000
    
    # Performance
    max_candidates: int = 200
    default_radius_km: float = 5.0
    max_radius_km: float = 50.0
    timeout_seconds: float = 0.1
    
    # Business rules
    min_rating: float = 3.0
    diversity_factor: float = 0.3
    novelty_boost: float = 0.1


class FeatureStore:
    """Handles feature retrieval from Redis and PostgreSQL"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.redis_pool = None
        self.postgres_pool = None
        
    async def initialize(self):
        """Initialize database connections"""
        # Redis connection pool
        self.redis_pool = redis.ConnectionPool(
            host=self.config.redis_host,
            port=self.config.redis_port,
            max_connections=100
        )
        
        # PostgreSQL connection pool
        self.postgres_pool = await asyncpg.create_pool(
            host=self.config.postgres_host,
            port=self.config.postgres_port,
            database=self.config.postgres_db,
            min_size=10,
            max_size=50
        )
        
        logger.info("Feature store initialized")
    
    async def get_user_features(self, user_id: int) -> Optional[UserFeatures]:
        """Fetch user features from Redis"""
        redis_client = redis.Redis(connection_pool=self.redis_pool)
        
        try:
            # Try Redis first (real-time features)
            feature_key = f"user_features:{user_id}"
            features_json = redis_client.get(feature_key)
            
            if features_json:
                features_dict = json.loads(features_json)
                return UserFeatures(
                    user_id=user_id,
                    age_group_encoded=features_dict.get("age_group_encoded", 0),
                    gender_encoded=features_dict.get("gender_encoded", 0),
                    total_interactions=features_dict.get("total_interactions", 0),
                    avg_rating_given=features_dict.get("avg_rating_given", 3.5),
                    preferred_categories=features_dict.get("preferred_categories", []),
                    home_lat=features_dict.get("home_lat"),
                    home_lng=features_dict.get("home_lng"),
                    exploration_radius_km=features_dict.get("exploration_radius_km", 5.0),
                    active_days_last_month=features_dict.get("active_days_last_month", 0),
                    last_activity_days_ago=features_dict.get("last_activity_days_ago", 999)
                )
            
            # Fallback to PostgreSQL for historical features
            return await self._get_user_features_from_postgres(user_id)
            
        except Exception as e:
            logger.error(f"Error fetching user features for {user_id}: {e}")
            return None
    
    async def _get_user_features_from_postgres(self, user_id: int) -> Optional[UserFeatures]:
        """Fallback to PostgreSQL for user features"""
        try:
            async with self.postgres_pool.acquire() as conn:
                query = """
                SELECT 
                    age_group_encoded,
                    gender_encoded,
                    total_interactions,
                    avg_rating_given,
                    home_lat,
                    home_lng,
                    exploration_radius_km,
                    active_days_last_month
                FROM user_features 
                WHERE user_id = $1
                """
                
                row = await conn.fetchrow(query, user_id)
                
                if row:
                    return UserFeatures(
                        user_id=user_id,
                        age_group_encoded=row['age_group_encoded'],
                        gender_encoded=row['gender_encoded'],
                        total_interactions=row['total_interactions'],
                        avg_rating_given=float(row['avg_rating_given']),
                        home_lat=float(row['home_lat']) if row['home_lat'] else None,
                        home_lng=float(row['home_lng']) if row['home_lng'] else None,
                        exploration_radius_km=float(row['exploration_radius_km']),
                        active_days_last_month=row['active_days_last_month']
                    )
                
        except Exception as e:
            logger.error(f"Error fetching user features from PostgreSQL for {user_id}: {e}")
            
        return None
    
    async def get_place_features(self, place_ids: List[int]) -> Dict[int, PlaceFeatures]:
        """Batch fetch place features"""
        redis_client = redis.Redis(connection_pool=self.redis_pool)
        features = {}
        
        try:
            # Batch fetch from Redis
            pipe = redis_client.pipeline()
            for place_id in place_ids:
                pipe.get(f"place_features:{place_id}")
            
            results = pipe.execute()
            
            for place_id, result in zip(place_ids, results):
                if result:
                    features_dict = json.loads(result)
                    features[place_id] = PlaceFeatures(
                        place_id=place_id,
                        category_encoded=features_dict.get("category_encoded", 0),
                        latitude=features_dict.get("latitude", 0.0),
                        longitude=features_dict.get("longitude", 0.0),
                        rating=features_dict.get("rating", 3.5),
                        review_count=features_dict.get("review_count", 0),
                        price_level=features_dict.get("price_level", 2),
                        popularity_score=features_dict.get("popularity_score", 0.5),
                        is_open=features_dict.get("is_open", True),
                        weekly_visits=features_dict.get("weekly_visits", 0),
                        unique_visitors=features_dict.get("unique_visitors", 0)
                    )
            
            # For missing features, fetch from PostgreSQL
            missing_ids = [pid for pid in place_ids if pid not in features]
            if missing_ids:
                postgres_features = await self._get_place_features_from_postgres(missing_ids)
                features.update(postgres_features)
                
        except Exception as e:
            logger.error(f"Error fetching place features: {e}")
            
        return features
    
    async def _get_place_features_from_postgres(self, place_ids: List[int]) -> Dict[int, PlaceFeatures]:
        """Fallback to PostgreSQL for place features"""
        features = {}
        
        try:
            async with self.postgres_pool.acquire() as conn:
                query = """
                SELECT 
                    place_id,
                    category_encoded,
                    latitude,
                    longitude,
                    rating,
                    review_count,
                    price_level,
                    popularity_score,
                    is_open,
                    weekly_visits,
                    unique_visitors
                FROM place_features 
                WHERE place_id = ANY($1)
                """
                
                rows = await conn.fetch(query, place_ids)
                
                for row in rows:
                    features[row['place_id']] = PlaceFeatures(
                        place_id=row['place_id'],
                        category_encoded=row['category_encoded'],
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        rating=float(row['rating']),
                        review_count=row['review_count'],
                        price_level=row['price_level'],
                        popularity_score=float(row['popularity_score']),
                        is_open=row['is_open'],
                        weekly_visits=row['weekly_visits'],
                        unique_visitors=row['unique_visitors']
                    )
                    
        except Exception as e:
            logger.error(f"Error fetching place features from PostgreSQL: {e}")
            
        return features


class GeospatialIndex:
    """Handles geographic queries for nearby places"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.redis_pool = None
        
    async def initialize(self):
        """Initialize Redis connection for geospatial queries"""
        self.redis_pool = redis.ConnectionPool(
            host=self.config.redis_host,
            port=self.config.redis_port,
            max_connections=100
        )
        
    async def find_nearby_places(self, lat: float, lng: float, 
                                radius_km: float, category: Optional[str] = None) -> List[int]:
        """Find places within radius using Redis geospatial commands"""
        redis_client = redis.Redis(connection_pool=self.redis_pool)
        
        try:
            # Use Redis GEORADIUS command
            geo_key = f"places_geo:{category}" if category else "places_geo:all"
            
            # Find places within radius
            results = redis_client.georadius(
                geo_key,
                lng, lat,  # Redis uses lng, lat order
                radius_km,
                unit='km',
                withcoord=True,
                withdist=True,
                sort='ASC',
                count=self.config.max_candidates
            )
            
            # Extract place IDs
            place_ids = []
            for result in results:
                place_name = result[0].decode('utf-8')
                # Place names are stored as "place_id"
                place_id = int(place_name.split('_')[1])
                place_ids.append(place_id)
                
            return place_ids
            
        except Exception as e:
            logger.error(f"Error finding nearby places: {e}")
            return []


class ModelInference:
    """Handles ML model inference"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.model = None
        self.user_encoder = None
        self.place_encoder = None
        self.feature_scaler = None
        
    async def initialize(self):
        """Load model and preprocessing artifacts"""
        try:
            # Load TensorFlow model
            self.model = tf.keras.models.load_model('models/recommendation_model')
            
            # Load preprocessing artifacts
            with open('artifacts/user_encoder.pkl', 'rb') as f:
                self.user_encoder = pickle.load(f)
            
            with open('artifacts/place_encoder.pkl', 'rb') as f:
                self.place_encoder = pickle.load(f)
                
            with open('artifacts/feature_scaler.pkl', 'rb') as f:
                self.feature_scaler = pickle.load(f)
                
            logger.info("Model and preprocessing artifacts loaded")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    async def predict(self, user_features: UserFeatures, 
                     place_features: Dict[int, PlaceFeatures],
                     context_features: Dict[int, ContextFeatures]) -> Dict[int, float]:
        """Predict recommendation scores for place candidates"""
        try:
            # Prepare feature matrix
            feature_matrix = []
            place_ids = []
            
            for place_id, place_feat in place_features.items():
                context_feat = context_features.get(place_id)
                if not context_feat:
                    continue
                    
                # Combine features
                features = [
                    user_features.user_id,
                    user_features.age_group_encoded,
                    user_features.gender_encoded,
                    place_id,
                    place_feat.category_encoded,
                    place_feat.rating,
                    place_feat.price_level,
                    context_feat.distance_km,
                    context_feat.hour_of_day,
                    context_feat.day_of_week,
                    float(context_feat.is_weekend)
                ]
                
                feature_matrix.append(features)
                place_ids.append(place_id)
            
            if not feature_matrix:
                return {}
            
            # Convert to numpy array and scale
            X = np.array(feature_matrix)
            X_scaled = self.feature_scaler.transform(X)
            
            # Get predictions
            predictions = self.model.predict(X_scaled, batch_size=len(X_scaled))
            
            # Return scores mapped to place IDs
            return dict(zip(place_ids, predictions.flatten()))
            
        except Exception as e:
            logger.error(f"Error during model inference: {e}")
            return {}


class RecommendationCache:
    """Multi-level caching for recommendations"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.l1_cache = {}  # In-memory cache
        self.redis_pool = None
        
    async def initialize(self):
        """Initialize Redis connection for L2 cache"""
        self.redis_pool = redis.ConnectionPool(
            host=self.config.redis_host,
            port=self.config.redis_port,
            max_connections=100
        )
    
    def _generate_cache_key(self, request: RecommendationRequest) -> str:
        """Generate cache key for request"""
        # Create hash of request parameters
        request_str = f"{request.user_id}:{request.location.latitude:.3f}:{request.location.longitude:.3f}:{request.radius_km}:{request.category}:{request.limit}"
        return hashlib.md5(request_str.encode()).hexdigest()
    
    async def get(self, request: RecommendationRequest) -> Optional[RecommendationResponse]:
        """Get cached recommendations"""
        if not self.config.enable_l1_cache:
            return None
            
        cache_key = self._generate_cache_key(request)
        
        # Check L1 cache first
        if cache_key in self.l1_cache:
            return self.l1_cache[cache_key]
        
        # Check L2 cache (Redis)
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            cached_data = redis_client.get(f"recommendations:{cache_key}")
            
            if cached_data:
                # Deserialize and add to L1 cache
                response_dict = json.loads(cached_data)
                response = RecommendationResponse.from_dict(response_dict)
                
                # Add to L1 cache if there's space
                if len(self.l1_cache) < self.config.l1_cache_size:
                    self.l1_cache[cache_key] = response
                    
                return response
                
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            
        return None
    
    async def set(self, request: RecommendationRequest, response: RecommendationResponse):
        """Cache recommendations"""
        if not self.config.enable_l1_cache:
            return
            
        cache_key = self._generate_cache_key(request)
        
        # Add to L1 cache
        if len(self.l1_cache) < self.config.l1_cache_size:
            self.l1_cache[cache_key] = response
        
        # Add to L2 cache (Redis)
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            redis_client.setex(
                f"recommendations:{cache_key}",
                self.config.cache_ttl_seconds,
                json.dumps(response.to_dict())
            )
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")


class InferencePipeline:
    """Main inference pipeline orchestrator"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.feature_store = FeatureStore(config)
        self.geo_index = GeospatialIndex(config)
        self.model_inference = ModelInference(config)
        self.cache = RecommendationCache(config)
        
    async def initialize(self):
        """Initialize all components"""
        await self.feature_store.initialize()
        await self.geo_index.initialize()
        await self.model_inference.initialize()
        await self.cache.initialize()
        
        logger.info("Inference pipeline initialized")
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Main recommendation pipeline"""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        try:
            # Check cache first
            cached_response = await self.cache.get(request)
            if cached_response:
                cached_response.metadata.cache_hit = True
                return cached_response
            
            # Step 1: Geographic filtering
            nearby_place_ids = await self.geo_index.find_nearby_places(
                request.location.latitude,
                request.location.longitude,
                request.radius_km,
                request.category.value if request.category else None
            )
            
            if not nearby_place_ids:
                return self._empty_response(request_id, start_time)
            
            # Step 2: Feature enrichment
            user_features = await self.feature_store.get_user_features(request.user_id)
            place_features = await self.feature_store.get_place_features(nearby_place_ids)
            context_features = self._compute_context_features(
                request, nearby_place_ids, place_features
            )
            
            # Step 3: Model inference
            if user_features:
                scores = await self.model_inference.predict(
                    user_features, place_features, context_features
                )
            else:
                # Fallback to popularity-based recommendations
                scores = self._popularity_fallback(place_features)
            
            # Step 4: Post-processing
            recommendations = await self._post_process_recommendations(
                scores, place_features, context_features, request.limit
            )
            
            # Create response
            response_time_ms = int((time.time() - start_time) * 1000)
            metadata = RecommendationMetadata(
                request_id=request_id,
                total_candidates=len(nearby_place_ids),
                search_radius_km=request.radius_km,
                response_time_ms=response_time_ms,
                model_version=self.config.model_version,
                cache_hit=False
            )
            
            response = RecommendationResponse(
                recommendations=recommendations,
                metadata=metadata
            )
            
            # Cache the response
            await self.cache.set(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in recommendation pipeline: {e}")
            return self._empty_response(request_id, start_time)
    
    def _compute_context_features(self, request: RecommendationRequest,
                                 place_ids: List[int],
                                 place_features: Dict[int, PlaceFeatures]) -> Dict[int, ContextFeatures]:
        """Compute context features for each place"""
        from datetime import datetime
        
        context_features = {}
        now = datetime.now()
        
        for place_id in place_ids:
            place_feat = place_features.get(place_id)
            if not place_feat:
                continue
                
            # Calculate distance
            distance_km = self._calculate_distance(
                request.location.latitude, request.location.longitude,
                place_feat.latitude, place_feat.longitude
            )
            
            context_features[place_id] = ContextFeatures(
                distance_km=distance_km,
                hour_of_day=now.hour,
                day_of_week=now.weekday(),
                is_weekend=now.weekday() >= 5,
                weather_score=0.7,  # Would fetch from weather API
                local_events_count=0  # Would fetch from events API
            )
            
        return context_features
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate haversine distance between two points"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1_rad, lng1_rad = radians(lat1), radians(lng1)
        lat2_rad, lng2_rad = radians(lat2), radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _popularity_fallback(self, place_features: Dict[int, PlaceFeatures]) -> Dict[int, float]:
        """Fallback to popularity-based scoring when user features unavailable"""
        scores = {}
        
        for place_id, features in place_features.items():
            # Simple popularity score based on rating and review count
            rating_score = features.rating / 5.0
            popularity_score = min(1.0, features.weekly_visits / 1000.0)
            
            scores[place_id] = (rating_score * 0.7 + popularity_score * 0.3)
            
        return scores
    
    async def _post_process_recommendations(self, scores: Dict[int, float],
                                          place_features: Dict[int, PlaceFeatures],
                                          context_features: Dict[int, ContextFeatures],
                                          limit: int) -> List[PlaceRecommendation]:
        """Post-process and rank recommendations"""
        # Apply business rules
        filtered_scores = {}
        for place_id, score in scores.items():
            place_feat = place_features.get(place_id)
            if place_feat and place_feat.rating >= self.config.min_rating:
                filtered_scores[place_id] = score
        
        # Sort by score
        sorted_places = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for rank, (place_id, score) in enumerate(sorted_places[:limit], 1):
            place_feat = place_features[place_id]
            context_feat = context_features[place_id]
            
            # Create place object (simplified)
            place = Place(
                place_id=place_id,
                name=f"Place {place_id}",  # Would fetch from database
                category=PlaceCategory.RESTAURANT,  # Would map from encoded category
                location=LocationPoint(place_feat.latitude, place_feat.longitude)
            )
            
            # Create explanation
            explanation = RecommendationExplanation(
                primary_reason="Based on your preferences and location",
                factors=["High rating", "Close to you", "Popular choice"],
                confidence_score=score
            )
            
            recommendation = PlaceRecommendation(
                place=place,
                score=score,
                rank=rank,
                distance_km=context_feat.distance_km,
                estimated_time_minutes=int(context_feat.distance_km * 12),  # ~5km/h walking
                explanation=explanation
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _empty_response(self, request_id: str, start_time: float) -> RecommendationResponse:
        """Create empty response for failed requests"""
        response_time_ms = int((time.time() - start_time) * 1000)
        
        metadata = RecommendationMetadata(
            request_id=request_id,
            total_candidates=0,
            search_radius_km=0.0,
            response_time_ms=response_time_ms,
            model_version=self.config.model_version,
            cache_hit=False
        )
        
        return RecommendationResponse(
            recommendations=[],
            metadata=metadata
        )


# Example usage
async def main():
    """Example usage of the inference pipeline"""
    config = InferenceConfig()
    pipeline = InferencePipeline(config)
    
    # Initialize pipeline
    await pipeline.initialize()
    
    # Create sample request
    request = RecommendationRequest(
        user_id=12345,
        location=LocationPoint(latitude=37.7749, longitude=-122.4194),
        radius_km=5.0,
        limit=10
    )
    
    # Get recommendations
    response = await pipeline.get_recommendations(request)
    
    print(f"Found {len(response.recommendations)} recommendations")
    print(f"Response time: {response.metadata.response_time_ms}ms")
    
    for rec in response.recommendations[:3]:
        print(f"- {rec.place.name} (score: {rec.score:.3f}, distance: {rec.distance_km:.1f}km)")


if __name__ == "__main__":
    asyncio.run(main())