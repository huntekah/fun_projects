"""
ML Models for Nearby Places Recommendation System
"""

import tensorflow as tf
from typing import Dict, List, Tuple
import numpy as np


class PlaceRecommendationModel:
    """Two-stage recommendation model: Candidate Generation + Ranking"""
    
    def __init__(self, embedding_dim: int = 64, num_users: int = 100_000_000, num_places: int = 50_000_000):
        self.embedding_dim = embedding_dim
        self.num_users = num_users
        self.num_places = num_places
        
        # Build candidate generation model
        self.candidate_model = self._build_candidate_model()
        
        # Build ranking model
        self.ranking_model = self._build_ranking_model()
    
    def _build_candidate_model(self) -> tf.keras.Model:
        """
        Candidate generation using matrix factorization + geographic filtering
        Generates top-k candidates from geographically nearby places
        """
        # User and place embeddings
        user_input = tf.keras.layers.Input(shape=(), name='user_id', dtype=tf.int32)
        place_input = tf.keras.layers.Input(shape=(), name='place_id', dtype=tf.int32)
        
        user_embedding = tf.keras.layers.Embedding(
            self.num_users, self.embedding_dim, name='user_embedding'
        )(user_input)
        
        place_embedding = tf.keras.layers.Embedding(
            self.num_places, self.embedding_dim, name='place_embedding'
        )(place_input)
        
        # Flatten embeddings
        user_vec = tf.keras.layers.Flatten()(user_embedding)
        place_vec = tf.keras.layers.Flatten()(place_embedding)
        
        # Compute similarity score
        similarity = tf.keras.layers.Dot(axes=1)([user_vec, place_vec])
        
        model = tf.keras.Model(
            inputs=[user_input, place_input],
            outputs=similarity,
            name='candidate_generation'
        )
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_ranking_model(self) -> tf.keras.Model:
        """
        Ranking model using wide & deep architecture
        Takes candidate places and ranks them using rich features
        """
        # User features
        user_id = tf.keras.layers.Input(shape=(), name='user_id', dtype=tf.int32)
        user_age = tf.keras.layers.Input(shape=(), name='user_age', dtype=tf.float32)
        user_gender = tf.keras.layers.Input(shape=(), name='user_gender', dtype=tf.int32)
        
        # Place features
        place_id = tf.keras.layers.Input(shape=(), name='place_id', dtype=tf.int32)
        place_category = tf.keras.layers.Input(shape=(), name='place_category', dtype=tf.int32)
        place_rating = tf.keras.layers.Input(shape=(), name='place_rating', dtype=tf.float32)
        place_price = tf.keras.layers.Input(shape=(), name='place_price', dtype=tf.int32)
        
        # Context features
        distance = tf.keras.layers.Input(shape=(), name='distance', dtype=tf.float32)
        hour_of_day = tf.keras.layers.Input(shape=(), name='hour_of_day', dtype=tf.int32)
        day_of_week = tf.keras.layers.Input(shape=(), name='day_of_week', dtype=tf.int32)
        is_weekend = tf.keras.layers.Input(shape=(), name='is_weekend', dtype=tf.int32)
        
        # Embeddings for categorical features
        user_emb = tf.keras.layers.Embedding(self.num_users, 32)(user_id)
        place_emb = tf.keras.layers.Embedding(self.num_places, 32)(place_id)
        category_emb = tf.keras.layers.Embedding(50, 16)(place_category)  # 50 categories
        gender_emb = tf.keras.layers.Embedding(3, 8)(user_gender)
        price_emb = tf.keras.layers.Embedding(5, 8)(place_price)  # 5 price levels
        hour_emb = tf.keras.layers.Embedding(24, 8)(hour_of_day)
        dow_emb = tf.keras.layers.Embedding(7, 8)(day_of_week)
        weekend_emb = tf.keras.layers.Embedding(2, 4)(is_weekend)
        
        # Flatten embeddings
        user_vec = tf.keras.layers.Flatten()(user_emb)
        place_vec = tf.keras.layers.Flatten()(place_emb)
        category_vec = tf.keras.layers.Flatten()(category_emb)
        gender_vec = tf.keras.layers.Flatten()(gender_emb)
        price_vec = tf.keras.layers.Flatten()(price_emb)
        hour_vec = tf.keras.layers.Flatten()(hour_emb)
        dow_vec = tf.keras.layers.Flatten()(dow_emb)
        weekend_vec = tf.keras.layers.Flatten()(weekend_emb)
        
        # Wide part - linear combinations
        wide_features = tf.keras.layers.Concatenate()([
            tf.keras.layers.Reshape((1,))(user_age),
            tf.keras.layers.Reshape((1,))(place_rating),
            tf.keras.layers.Reshape((1,))(distance),
        ])
        
        wide_output = tf.keras.layers.Dense(1, activation=None)(wide_features)
        
        # Deep part - neural network
        deep_features = tf.keras.layers.Concatenate()([
            user_vec, place_vec, category_vec, gender_vec,
            price_vec, hour_vec, dow_vec, weekend_vec,
            tf.keras.layers.Reshape((1,))(user_age),
            tf.keras.layers.Reshape((1,))(place_rating),
            tf.keras.layers.Reshape((1,))(distance),
        ])
        
        deep = tf.keras.layers.Dense(256, activation='relu')(deep_features)
        deep = tf.keras.layers.Dropout(0.3)(deep)
        deep = tf.keras.layers.Dense(128, activation='relu')(deep)
        deep = tf.keras.layers.Dropout(0.3)(deep)
        deep = tf.keras.layers.Dense(64, activation='relu')(deep)
        deep_output = tf.keras.layers.Dense(1, activation=None)(deep)
        
        # Combine wide and deep
        output = tf.keras.layers.Add()([wide_output, deep_output])
        output = tf.keras.layers.Activation('sigmoid')(output)
        
        model = tf.keras.Model(
            inputs=[
                user_id, user_age, user_gender,
                place_id, place_category, place_rating, place_price,
                distance, hour_of_day, day_of_week, is_weekend
            ],
            outputs=output,
            name='ranking_model'
        )
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'auc']
        )
        
        return model
    
    def predict_candidates(self, user_id: int, candidate_place_ids: List[int], k: int = 100) -> List[int]:
        """Generate top-k candidate places for a user"""
        user_ids = np.array([user_id] * len(candidate_place_ids))
        place_ids = np.array(candidate_place_ids)
        
        scores = self.candidate_model.predict([user_ids, place_ids])
        
        # Get top-k candidates
        top_k_indices = np.argsort(scores.flatten())[-k:][::-1]
        return [candidate_place_ids[i] for i in top_k_indices]
    
    def rank_places(self, features: Dict[str, np.ndarray]) -> np.ndarray:
        """Rank candidate places using the ranking model"""
        return self.ranking_model.predict(features)


class GeospatialIndex:
    """Efficient geospatial querying for nearby places"""
    
    def __init__(self):
        # In practice, this would use PostGIS, Elasticsearch, or Redis Geospatial
        self.places_by_location = {}  # Grid-based spatial index
    
    def find_nearby_places(self, lat: float, lng: float, radius_km: float) -> List[int]:
        """
        Find places within radius using geospatial index
        Returns list of place IDs
        """
        # Simplified implementation - in practice use proper geospatial index
        nearby_places = []
        
        # Example: grid-based lookup
        grid_size = 0.01  # ~1km
        lat_grid = int(lat / grid_size)
        lng_grid = int(lng / grid_size)
        
        # Check neighboring grid cells
        for lat_offset in [-1, 0, 1]:
            for lng_offset in [-1, 0, 1]:
                grid_key = (lat_grid + lat_offset, lng_grid + lng_offset)
                if grid_key in self.places_by_location:
                    nearby_places.extend(self.places_by_location[grid_key])
        
        return nearby_places[:1000]  # Limit candidates


class RecommendationService:
    """Main service orchestrating the recommendation pipeline"""
    
    def __init__(self):
        self.ml_model = PlaceRecommendationModel()
        self.geo_index = GeospatialIndex()
        
    def get_recommendations(
        self, 
        user_id: int, 
        lat: float, 
        lng: float, 
        radius_km: float = 5.0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Main recommendation pipeline:
        1. Find nearby places using geospatial index
        2. Generate candidates using collaborative filtering
        3. Rank candidates using deep learning model
        4. Apply business rules and return results
        """
        
        # Step 1: Geographic filtering
        nearby_place_ids = self.geo_index.find_nearby_places(lat, lng, radius_km)
        
        # Step 2: Candidate generation
        candidate_ids = self.ml_model.predict_candidates(user_id, nearby_place_ids, k=200)
        
        # Step 3: Feature preparation for ranking
        features = self._prepare_ranking_features(user_id, candidate_ids, lat, lng)
        
        # Step 4: Ranking
        scores = self.ml_model.rank_places(features)
        
        # Step 5: Post-processing and business rules
        recommendations = self._post_process(candidate_ids, scores, limit)
        
        return recommendations
    
    def _prepare_ranking_features(self, user_id: int, place_ids: List[int], lat: float, lng: float) -> Dict[str, np.ndarray]:
        """Prepare features for ranking model"""
        # This would fetch real features from feature store
        n = len(place_ids)
        
        return {
            'user_id': np.array([user_id] * n),
            'user_age': np.array([25.0] * n),  # From user service
            'user_gender': np.array([1] * n),
            'place_id': np.array(place_ids),
            'place_category': np.array([1] * n),  # From place service
            'place_rating': np.array([4.2] * n),
            'place_price': np.array([2] * n),
            'distance': np.array([1.5] * n),  # Computed from lat/lng
            'hour_of_day': np.array([14] * n),  # Current time
            'day_of_week': np.array([2] * n),
            'is_weekend': np.array([0] * n),
        }
    
    def _post_process(self, place_ids: List[int], scores: np.ndarray, limit: int) -> List[Dict]:
        """Apply business rules and format response"""
        # Sort by score
        ranked_indices = np.argsort(scores.flatten())[::-1]
        
        recommendations = []
        for i in ranked_indices[:limit]:
            recommendations.append({
                'place_id': place_ids[i],
                'score': float(scores[i]),
                'reason': 'Based on your preferences and location'
            })
        
        return recommendations