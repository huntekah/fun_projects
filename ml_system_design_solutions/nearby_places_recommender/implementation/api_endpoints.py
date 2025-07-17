"""
API Endpoints for Nearby Places Recommendation System

This module implements the REST API endpoints using FastAPI, including
request validation, authentication, rate limiting, and error handling.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import redis
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from data_models import (
    LocationPoint, PlaceCategory, DeviceType, InteractionType,
    RecommendationRequest, RecommendationResponse, UserInteraction,
    InteractionContext
)
from inference_pipeline import InferencePipeline, InferenceConfig


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for API Request/Response
# ============================================================================

class LocationRequest(BaseModel):
    """Location input model"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    accuracy_meters: Optional[int] = Field(None, ge=1, le=10000, description="GPS accuracy in meters")


class RecommendationFilters(BaseModel):
    """Filters for recommendation requests"""
    category: Optional[PlaceCategory] = Field(None, description="Filter by place category")
    min_rating: Optional[float] = Field(None, ge=1, le=5, description="Minimum rating filter")
    max_distance_km: Optional[float] = Field(None, ge=0.1, le=50, description="Maximum distance in kilometers")
    price_level: Optional[List[int]] = Field(None, description="Price level filter (1-4)")
    open_now: Optional[bool] = Field(None, description="Filter for places open now")


class RecommendationRequestAPI(BaseModel):
    """API request model for recommendations"""
    location: LocationRequest
    radius_km: float = Field(5.0, ge=0.1, le=50, description="Search radius in kilometers")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of recommendations")
    filters: Optional[RecommendationFilters] = None
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    
    @validator('radius_km')
    def validate_radius(cls, v):
        if v > 50:
            raise ValueError('Radius cannot exceed 50km')
        return v


class InteractionRequestAPI(BaseModel):
    """API request model for user interactions"""
    place_id: int = Field(..., description="ID of the place")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5) for rating interactions")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duration of interaction in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")


class PlaceDetailRequest(BaseModel):
    """Request model for place details"""
    place_id: int = Field(..., description="ID of the place")
    include_reviews: bool = Field(False, description="Include recent reviews")
    include_photos: bool = Field(False, description="Include photos")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    timestamp: datetime
    request_id: str


# ============================================================================
# Authentication and Security
# ============================================================================

security = HTTPBearer()

class AuthService:
    """Handles JWT token validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


auth_service = AuthService("your-secret-key")  # In production, use environment variable


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract current user from JWT token"""
    return auth_service.decode_token(credentials.credentials)


# ============================================================================
# Rate Limiting
# ============================================================================

# Redis for rate limiting
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Nearby Places Recommendation API",
    description="Real-time personalized place recommendations based on location and user preferences",
    version="2.1.3",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.example.com", "localhost", "127.0.0.1"]
)

# Rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global inference pipeline
inference_pipeline = None


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global inference_pipeline
    
    logger.info("Starting Nearby Places Recommendation API...")
    
    # Initialize inference pipeline
    config = InferenceConfig()
    inference_pipeline = InferencePipeline(config)
    await inference_pipeline.initialize()
    
    logger.info("API startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")
    # Cleanup connections, save state, etc.


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            timestamp=datetime.now(),
            request_id=str(uuid.uuid4())
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            timestamp=datetime.now(),
            request_id=str(uuid.uuid4())
        ).dict()
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", status_code=200)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.1.3"
    }


@app.get("/metrics", status_code=200)
async def metrics():
    """Metrics endpoint for monitoring"""
    # In production, this would return Prometheus metrics
    return {
        "requests_total": 12345,
        "requests_per_second": 150,
        "average_response_time_ms": 85,
        "cache_hit_rate": 0.75,
        "model_version": "v2.1.3"
    }


@app.post("/api/v1/recommendations", 
         response_model=RecommendationResponse,
         status_code=200,
         summary="Get personalized place recommendations",
         description="Returns a list of personalized place recommendations based on user location and preferences")
@limiter.limit("100/minute")  # Rate limit: 100 requests per minute
async def get_recommendations(
    request: Request,
    recommendation_request: RecommendationRequestAPI,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> RecommendationResponse:
    """Get personalized place recommendations"""
    
    start_time = time.time()
    
    try:
        # Extract user ID from token
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )
        
        # Convert API request to internal request model
        location = LocationPoint(
            latitude=recommendation_request.location.latitude,
            longitude=recommendation_request.location.longitude,
            accuracy_meters=recommendation_request.location.accuracy_meters
        )
        
        # Create context from request headers and body
        context = InteractionContext(
            device_type=DeviceType.MOBILE,  # Could extract from User-Agent
            app_version=request.headers.get("X-App-Version"),
            session_id=request.headers.get("X-Session-ID")
        )
        
        internal_request = RecommendationRequest(
            user_id=user_id,
            location=location,
            radius_km=recommendation_request.radius_km,
            category=recommendation_request.filters.category if recommendation_request.filters else None,
            limit=recommendation_request.limit,
            context=context,
            filters=recommendation_request.filters.dict() if recommendation_request.filters else {}
        )
        
        # Get recommendations from inference pipeline
        response = await inference_pipeline.get_recommendations(internal_request)
        
        # Log request for analytics
        await _log_request(user_id, internal_request, response, time.time() - start_time)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


@app.post("/api/v1/interactions",
         status_code=201,
         summary="Log user interaction",
         description="Log user interaction with a place for improving recommendations")
@limiter.limit("1000/minute")  # Higher limit for interaction logging
async def log_interaction(
    request: Request,
    interaction_request: InteractionRequestAPI,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Log user interaction with a place"""
    
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )
        
        # Create interaction context
        context = InteractionContext(
            session_id=request.headers.get("X-Session-ID"),
            device_type=DeviceType.MOBILE,  # Extract from User-Agent
            app_version=request.headers.get("X-App-Version"),
            recommendation_id=interaction_request.context.get("recommendation_id") if interaction_request.context else None
        )
        
        # Create interaction object
        interaction = UserInteraction(
            interaction_id=str(uuid.uuid4()),
            user_id=user_id,
            place_id=interaction_request.place_id,
            interaction_type=interaction_request.interaction_type,
            timestamp=datetime.now(),
            rating=interaction_request.rating,
            duration_seconds=interaction_request.duration_seconds,
            context=context
        )
        
        # Log interaction (would typically send to Kafka)
        await _log_interaction_event(interaction)
        
        return {
            "status": "success",
            "interaction_id": interaction.interaction_id,
            "message": "Interaction logged successfully"
        }
        
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log interaction"
        )


@app.get("/api/v1/places/{place_id}",
        status_code=200,
        summary="Get place details",
        description="Get detailed information about a specific place")
@limiter.limit("200/minute")
async def get_place_details(
    place_id: int,
    include_reviews: bool = False,
    include_photos: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed information about a place"""
    
    try:
        # This would fetch from the place service/database
        # For now, return mock data
        place_details = {
            "place_id": place_id,
            "name": f"Sample Place {place_id}",
            "category": "restaurant",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194
            },
            "address": "123 Sample Street, San Francisco, CA",
            "rating": 4.3,
            "review_count": 247,
            "price_level": 2,
            "business_hours": {
                "monday": "9:00-22:00",
                "tuesday": "9:00-22:00",
                "wednesday": "9:00-22:00",
                "thursday": "9:00-22:00",
                "friday": "9:00-23:00",
                "saturday": "10:00-23:00",
                "sunday": "10:00-21:00"
            },
            "contact": {
                "phone": "+1-555-123-4567",
                "website": "https://example.com"
            },
            "attributes": {
                "wifi": True,
                "parking": True,
                "outdoor_seating": True,
                "delivery": True
            }
        }
        
        if include_reviews:
            place_details["recent_reviews"] = [
                {
                    "user": "Anonymous",
                    "rating": 5,
                    "text": "Great food and service!",
                    "timestamp": "2024-01-10T15:30:00Z"
                }
            ]
        
        if include_photos:
            place_details["photos"] = [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg"
            ]
        
        return place_details
        
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get place details"
        )


@app.get("/api/v1/user/preferences",
        status_code=200,
        summary="Get user preferences",
        description="Get current user's recommendation preferences")
async def get_user_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's recommendation preferences"""
    
    user_id = current_user.get("user_id")
    
    # This would fetch from user service
    preferences = {
        "user_id": user_id,
        "categories": {
            "restaurant": 0.8,
            "cafe": 0.6,
            "shopping": 0.4,
            "entertainment": 0.7
        },
        "max_distance_km": 5.0,
        "price_preference": 2,
        "dietary_restrictions": ["vegetarian"],
        "accessibility_needs": []
    }
    
    return preferences


@app.put("/api/v1/user/preferences",
        status_code=200,
        summary="Update user preferences",
        description="Update user's recommendation preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user's recommendation preferences"""
    
    user_id = current_user.get("user_id")
    
    try:
        # Validate and update preferences (would typically update database)
        await _update_user_preferences(user_id, preferences)
        
        return {
            "status": "success",
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


# ============================================================================
# Helper Functions
# ============================================================================

async def _log_request(user_id: int, request: RecommendationRequest, 
                      response: RecommendationResponse, response_time: float):
    """Log recommendation request for analytics"""
    log_data = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "location": {
            "lat": request.location.latitude,
            "lng": request.location.longitude
        },
        "radius_km": request.radius_km,
        "num_recommendations": len(response.recommendations),
        "response_time_ms": int(response_time * 1000),
        "cache_hit": response.metadata.cache_hit
    }
    
    # In production, this would send to analytics pipeline (Kafka, etc.)
    logger.info(f"Recommendation request: {json.dumps(log_data)}")


async def _log_interaction_event(interaction: UserInteraction):
    """Log user interaction event"""
    # In production, this would send to Kafka for real-time processing
    logger.info(f"User interaction: {json.dumps(interaction.to_dict())}")


async def _update_user_preferences(user_id: int, preferences: Dict[str, Any]):
    """Update user preferences in database"""
    # In production, this would update the user service database
    logger.info(f"Updated preferences for user {user_id}: {preferences}")


# ============================================================================
# Admin Endpoints (Protected)
# ============================================================================

@app.get("/admin/stats",
        status_code=200,
        summary="Get system statistics",
        description="Get system-wide statistics (admin only)")
async def get_admin_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get system statistics (admin only)"""
    
    # Check admin role
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "total_users": 1250000,
        "total_places": 5000000,
        "daily_requests": 2500000,
        "average_response_time_ms": 85,
        "cache_hit_rate": 0.75,
        "model_accuracy": 0.87,
        "system_load": {
            "cpu_usage": 0.65,
            "memory_usage": 0.72,
            "disk_usage": 0.45
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "api_endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # For development only
        log_level="info"
    )