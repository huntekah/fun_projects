"""
Data Models for Nearby Places Recommendation System

This module defines all the data structures used throughout the system,
including database models, API schemas, and internal data transfer objects.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json
from decimal import Decimal


# ============================================================================
# Enums and Constants
# ============================================================================

class InteractionType(Enum):
    VIEW = "view"
    CLICK = "click"
    VISIT = "visit"
    RATE = "rate"
    SHARE = "share"
    SAVE = "save"


class PlaceCategory(Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SERVICES = "services"
    TRAVEL = "travel"
    EDUCATION = "education"
    RECREATION = "recreation"


class DeviceType(Enum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    WEB = "web"


# ============================================================================
# Core Data Models
# ============================================================================

@dataclass
class LocationPoint:
    """Geographic location with precision metadata"""
    latitude: float
    longitude: float
    accuracy_meters: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Point",
            "coordinates": [self.longitude, self.latitude]
        }
    
    def distance_to(self, other: 'LocationPoint') -> float:
        """Calculate haversine distance to another point in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c


@dataclass
class Address:
    """Structured address information"""
    street_address: Optional[str] = None
    city: str = ""
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = ""
    formatted_address: Optional[str] = None
    
    def __str__(self) -> str:
        if self.formatted_address:
            return self.formatted_address
        
        parts = [
            self.street_address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))


@dataclass
class ContactInfo:
    """Business contact information"""
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = field(default_factory=dict)


@dataclass
class BusinessHours:
    """Business operating hours"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None
    special_hours: Dict[str, str] = field(default_factory=dict)  # Holiday hours
    
    def is_open_at(self, timestamp: datetime) -> bool:
        """Check if business is open at given timestamp"""
        # Simplified implementation - in practice would handle timezone, parsing, etc.
        day_name = timestamp.strftime("%A").lower()
        hours = getattr(self, day_name)
        
        if not hours or hours.lower() == "closed":
            return False
        
        # Parse hours like "09:00-17:00" and check if timestamp falls within
        # This is a simplified version - production would use proper time parsing
        return True


@dataclass
class PlaceStats:
    """Aggregated statistics for a place"""
    rating: Optional[Decimal] = None
    review_count: int = 0
    price_level: Optional[int] = None  # 1-4 scale
    popularity_score: Optional[Decimal] = None
    check_in_count: int = 0
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rating": float(self.rating) if self.rating else None,
            "review_count": self.review_count,
            "price_level": self.price_level,
            "popularity_score": float(self.popularity_score) if self.popularity_score else None,
            "check_in_count": self.check_in_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


@dataclass
class Place:
    """Complete place entity"""
    place_id: int
    name: str
    category: PlaceCategory
    subcategory: Optional[str] = None
    location: Optional[LocationPoint] = None
    address: Optional[Address] = None
    contact_info: Optional[ContactInfo] = None
    business_hours: Optional[BusinessHours] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    stats: Optional[PlaceStats] = None
    description: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "place_id": self.place_id,
            "name": self.name,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            } if self.location else None,
            "address": str(self.address) if self.address else None,
            "contact_info": {
                "phone": self.contact_info.phone,
                "website": self.contact_info.website
            } if self.contact_info else None,
            "attributes": self.attributes,
            "stats": self.stats.to_dict() if self.stats else None,
            "description": self.description,
            "photos": self.photos
        }


# ============================================================================
# User Models
# ============================================================================

@dataclass
class UserPreferences:
    """User preference settings"""
    categories: Dict[PlaceCategory, float] = field(default_factory=dict)
    price_preference: Optional[int] = None  # 1-4 scale
    max_distance_km: float = 5.0
    dietary_restrictions: List[str] = field(default_factory=list)
    accessibility_needs: List[str] = field(default_factory=list)
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "categories": {cat.value: score for cat, score in self.categories.items()},
            "price_preference": self.price_preference,
            "max_distance_km": self.max_distance_km,
            "dietary_restrictions": self.dietary_restrictions,
            "accessibility_needs": self.accessibility_needs,
            "language": self.language
        }


@dataclass
class PrivacySettings:
    """User privacy configuration"""
    location_tracking: bool = True
    personalized_recommendations: bool = True
    social_sharing: bool = False
    marketing_communications: bool = False
    data_retention_days: int = 730  # 2 years default
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_tracking": self.location_tracking,
            "personalized_recommendations": self.personalized_recommendations,
            "social_sharing": self.social_sharing,
            "marketing_communications": self.marketing_communications,
            "data_retention_days": self.data_retention_days
        }


@dataclass
class UserProfile:
    """Complete user profile"""
    user_id: int
    age_group: Optional[str] = None  # "18-25", "26-35", etc.
    gender: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    privacy_settings: Optional[PrivacySettings] = None
    home_location: Optional[LocationPoint] = None
    work_location: Optional[LocationPoint] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "age_group": self.age_group,
            "gender": self.gender,
            "preferences": self.preferences.to_dict() if self.preferences else None,
            "privacy_settings": self.privacy_settings.to_dict() if self.privacy_settings else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None
        }


# ============================================================================
# Interaction Models
# ============================================================================

@dataclass
class InteractionContext:
    """Context information for user interactions"""
    session_id: Optional[str] = None
    device_type: Optional[DeviceType] = None
    app_version: Optional[str] = None
    search_query: Optional[str] = None
    recommendation_id: Optional[str] = None
    position_in_results: Optional[int] = None
    weather_condition: Optional[str] = None
    time_of_day: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "device_type": self.device_type.value if self.device_type else None,
            "app_version": self.app_version,
            "search_query": self.search_query,
            "recommendation_id": self.recommendation_id,
            "position_in_results": self.position_in_results,
            "weather_condition": self.weather_condition,
            "time_of_day": self.time_of_day
        }


@dataclass
class UserInteraction:
    """User interaction event"""
    interaction_id: Optional[str] = None
    user_id: int = 0
    place_id: int = 0
    interaction_type: InteractionType = InteractionType.VIEW
    timestamp: Optional[datetime] = None
    rating: Optional[int] = None  # 1-5 scale for ratings
    duration_seconds: Optional[int] = None
    location: Optional[LocationPoint] = None
    context: Optional[InteractionContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "interaction_type": self.interaction_type.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "rating": self.rating,
            "duration_seconds": self.duration_seconds,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            } if self.location else None,
            "context": self.context.to_dict() if self.context else None,
            "metadata": self.metadata
        }


# ============================================================================
# Recommendation Models
# ============================================================================

@dataclass
class RecommendationExplanation:
    """Explanation for why a place was recommended"""
    primary_reason: str
    factors: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_reason": self.primary_reason,
            "factors": self.factors,
            "confidence_score": self.confidence_score
        }


@dataclass
class PlaceRecommendation:
    """Single place recommendation with metadata"""
    place: Place
    score: float
    rank: int
    distance_km: Optional[float] = None
    estimated_time_minutes: Optional[int] = None
    explanation: Optional[RecommendationExplanation] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "place": self.place.to_dict(),
            "score": self.score,
            "rank": self.rank,
            "distance_km": self.distance_km,
            "estimated_time_minutes": self.estimated_time_minutes,
            "explanation": self.explanation.to_dict() if self.explanation else None
        }


@dataclass
class RecommendationRequest:
    """Request for recommendations"""
    user_id: int
    location: LocationPoint
    radius_km: float = 5.0
    category: Optional[PlaceCategory] = None
    limit: int = 20
    context: Optional[InteractionContext] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            },
            "radius_km": self.radius_km,
            "category": self.category.value if self.category else None,
            "limit": self.limit,
            "context": self.context.to_dict() if self.context else None,
            "filters": self.filters
        }


@dataclass
class RecommendationMetadata:
    """Metadata about the recommendation response"""
    request_id: str
    total_candidates: int
    search_radius_km: float
    response_time_ms: int
    model_version: str
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "total_candidates": self.total_candidates,
            "search_radius_km": self.search_radius_km,
            "response_time_ms": self.response_time_ms,
            "model_version": self.model_version,
            "cache_hit": self.cache_hit
        }


@dataclass
class RecommendationResponse:
    """Complete recommendation response"""
    recommendations: List[PlaceRecommendation]
    metadata: RecommendationMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "metadata": self.metadata.to_dict()
        }


# ============================================================================
# Feature Models (for ML pipeline)
# ============================================================================

@dataclass
class UserFeatures:
    """User features for ML models"""
    user_id: int
    age_group_encoded: int
    gender_encoded: int
    total_interactions: int
    avg_rating_given: float
    preferred_categories: List[int]
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    exploration_radius_km: float = 5.0
    active_days_last_month: int = 0
    last_activity_days_ago: int = 999
    
    def to_feature_vector(self) -> Dict[str, Union[int, float, List[int]]]:
        """Convert to ML feature vector"""
        return {
            "user_id": self.user_id,
            "age_group": self.age_group_encoded,
            "gender": self.gender_encoded,
            "total_interactions": self.total_interactions,
            "avg_rating_given": self.avg_rating_given,
            "preferred_categories": self.preferred_categories,
            "home_lat": self.home_lat or 0.0,
            "home_lng": self.home_lng or 0.0,
            "exploration_radius": self.exploration_radius_km,
            "activity_recency": max(0, 30 - self.last_activity_days_ago) / 30.0
        }


@dataclass
class PlaceFeatures:
    """Place features for ML models"""
    place_id: int
    category_encoded: int
    latitude: float
    longitude: float
    rating: float
    review_count: int
    price_level: int
    popularity_score: float
    is_open: bool
    weekly_visits: int = 0
    unique_visitors: int = 0
    
    def to_feature_vector(self) -> Dict[str, Union[int, float]]:
        """Convert to ML feature vector"""
        return {
            "place_id": self.place_id,
            "category": self.category_encoded,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rating": self.rating,
            "log_review_count": min(10.0, max(0.0, float(self.review_count))),
            "price_level": self.price_level,
            "popularity_score": self.popularity_score,
            "is_open": float(self.is_open),
            "weekly_visits_normalized": min(1.0, self.weekly_visits / 1000.0),
            "visitor_diversity": min(1.0, self.unique_visitors / max(1, self.weekly_visits))
        }


@dataclass
class ContextFeatures:
    """Context features for ML models"""
    distance_km: float
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    weather_score: float = 0.5  # 0-1 scale
    local_events_count: int = 0
    
    def to_feature_vector(self) -> Dict[str, Union[int, float]]:
        """Convert to ML feature vector"""
        return {
            "distance_km": self.distance_km,
            "distance_normalized": min(1.0, self.distance_km / 10.0),
            "hour_of_day": self.hour_of_day,
            "day_of_week": self.day_of_week,
            "is_weekend": float(self.is_weekend),
            "weather_score": self.weather_score,
            "has_local_events": float(self.local_events_count > 0)
        }


# ============================================================================
# Database Models (for ORM mapping)
# ============================================================================

class DatabaseModel:
    """Base class for database models"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseModel':
        """Create instance from dictionary"""
        # Filter out None values and unknown fields
        filtered_data = {
            k: v for k, v in data.items() 
            if v is not None and k in cls.__dataclass_fields__
        }
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            
            if value is None:
                continue
            elif isinstance(value, datetime):
                result[field_name] = value.isoformat()
            elif isinstance(value, Enum):
                result[field_name] = value.value
            elif isinstance(value, (list, dict)):
                result[field_name] = value
            else:
                result[field_name] = value
                
        return result


# Example usage and utility functions
def create_sample_data():
    """Create sample data for testing"""
    
    # Sample location
    location = LocationPoint(
        latitude=37.7749,
        longitude=-122.4194,
        accuracy_meters=10
    )
    
    # Sample place
    place = Place(
        place_id=12345,
        name="Tony's Little Star Pizza",
        category=PlaceCategory.RESTAURANT,
        subcategory="Italian",
        location=location,
        address=Address(
            street_address="846 Divisadero St",
            city="San Francisco",
            state="CA",
            postal_code="94117",
            country="USA"
        ),
        stats=PlaceStats(
            rating=Decimal("4.3"),
            review_count=1247,
            price_level=2,
            popularity_score=Decimal("0.85")
        ),
        attributes={
            "delivery": True,
            "outdoor_seating": True,
            "wifi": True,
            "parking": "street"
        }
    )
    
    # Sample user interaction
    interaction = UserInteraction(
        user_id=67890,
        place_id=12345,
        interaction_type=InteractionType.VISIT,
        timestamp=datetime.now(),
        rating=4,
        location=location,
        context=InteractionContext(
            device_type=DeviceType.MOBILE,
            search_query="pizza near me"
        )
    )
    
    return place, interaction


if __name__ == "__main__":
    # Test the data models
    place, interaction = create_sample_data()
    
    print("Place JSON:")
    print(json.dumps(place.to_dict(), indent=2))
    
    print("\nInteraction JSON:")
    print(json.dumps(interaction.to_dict(), indent=2))