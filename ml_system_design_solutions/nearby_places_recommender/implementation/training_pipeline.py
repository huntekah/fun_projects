"""
Training Pipeline for Nearby Places Recommendation System

This module implements the complete ML training pipeline including:
- Data preprocessing and feature engineering
- Model training with hyperparameter tuning
- Model validation and evaluation
- Model versioning and deployment
"""

import os
import logging
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score
import mlflow
import mlflow.tensorflow
from feast import FeatureStore
import optuna

from data_models import UserFeatures, PlaceFeatures, ContextFeatures
from ml_models import PlaceRecommendationModel


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for training pipeline"""
    # Data parameters
    training_window_days: int = 30
    validation_split: float = 0.2
    test_split: float = 0.1
    negative_sampling_ratio: int = 4
    
    # Model parameters
    embedding_dim: int = 64
    learning_rate: float = 0.001
    batch_size: int = 1024
    epochs: int = 50
    early_stopping_patience: int = 5
    
    # Feature parameters
    max_sequence_length: int = 50
    min_interactions_per_user: int = 5
    min_interactions_per_place: int = 10
    
    # Hyperparameter tuning
    n_trials: int = 100
    optimization_metric: str = "val_auc"
    
    # Storage
    model_registry_uri: str = "s3://ml-models/recommendation-system"
    feature_store_config: str = "feast_config.yaml"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "training_window_days": self.training_window_days,
            "validation_split": self.validation_split,
            "test_split": self.test_split,
            "negative_sampling_ratio": self.negative_sampling_ratio,
            "embedding_dim": self.embedding_dim,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "epochs": self.epochs,
            "early_stopping_patience": self.early_stopping_patience
        }


class DataPreprocessor:
    """Handles data preprocessing and feature engineering"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.user_encoder = LabelEncoder()
        self.place_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.feature_scaler = StandardScaler()
        
    def load_training_data(self) -> pd.DataFrame:
        """Load training data from feature store and databases"""
        logger.info("Loading training data...")
        
        # Load from feature store (Feast)
        fs = FeatureStore(repo_path=self.config.feature_store_config)
        
        # Define time range for training data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.training_window_days)
        
        # Get user interaction events
        interactions_df = self._load_interactions(start_date, end_date)
        
        # Get user features
        user_features_df = self._load_user_features(fs, interactions_df['user_id'].unique())
        
        # Get place features
        place_features_df = self._load_place_features(fs, interactions_df['place_id'].unique())
        
        # Join all features
        training_df = self._join_features(interactions_df, user_features_df, place_features_df)
        
        logger.info(f"Loaded {len(training_df)} training samples")
        return training_df
    
    def _load_interactions(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Load user interaction data"""
        # This would typically query from your data warehouse
        # Simulated data loading
        query = f"""
        SELECT 
            user_id,
            place_id,
            interaction_type,
            rating,
            timestamp,
            latitude,
            longitude,
            session_id,
            device_type
        FROM user_interactions 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
            AND interaction_type IN ('visit', 'rating', 'click')
        """
        
        # Mock data for example
        np.random.seed(42)
        n_interactions = 100000
        
        interactions_data = {
            'user_id': np.random.randint(1, 10000, n_interactions),
            'place_id': np.random.randint(1, 5000, n_interactions),
            'interaction_type': np.random.choice(['visit', 'rating', 'click'], n_interactions),
            'rating': np.random.choice([1, 2, 3, 4, 5], n_interactions),
            'timestamp': pd.date_range(start_date, end_date, periods=n_interactions),
            'latitude': np.random.uniform(37.7, 37.8, n_interactions),
            'longitude': np.random.uniform(-122.5, -122.4, n_interactions),
            'session_id': [f"session_{i}" for i in range(n_interactions)],
            'device_type': np.random.choice(['mobile', 'web'], n_interactions)
        }
        
        return pd.DataFrame(interactions_data)
    
    def _load_user_features(self, fs: FeatureStore, user_ids: List[int]) -> pd.DataFrame:
        """Load user features from feature store"""
        # Mock user features
        np.random.seed(42)
        n_users = len(user_ids)
        
        user_data = {
            'user_id': user_ids,
            'age_group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+'], n_users),
            'gender': np.random.choice(['M', 'F', 'O'], n_users),
            'total_interactions': np.random.poisson(50, n_users),
            'avg_rating_given': np.random.normal(3.8, 0.5, n_users),
            'home_lat': np.random.uniform(37.7, 37.8, n_users),
            'home_lng': np.random.uniform(-122.5, -122.4, n_users),
            'exploration_radius': np.random.gamma(2, 2, n_users),
            'active_days_last_month': np.random.poisson(15, n_users)
        }
        
        return pd.DataFrame(user_data)
    
    def _load_place_features(self, fs: FeatureStore, place_ids: List[int]) -> pd.DataFrame:
        """Load place features from feature store"""
        # Mock place features
        np.random.seed(42)
        n_places = len(place_ids)
        
        place_data = {
            'place_id': place_ids,
            'category': np.random.choice(['restaurant', 'cafe', 'shopping', 'entertainment'], n_places),
            'latitude': np.random.uniform(37.7, 37.8, n_places),
            'longitude': np.random.uniform(-122.5, -122.4, n_places),
            'rating': np.random.normal(4.0, 0.8, n_places),
            'review_count': np.random.poisson(100, n_places),
            'price_level': np.random.choice([1, 2, 3, 4], n_places),
            'popularity_score': np.random.beta(2, 2, n_places),
            'weekly_visits': np.random.poisson(200, n_places)
        }
        
        return pd.DataFrame(place_data)
    
    def _join_features(self, interactions_df: pd.DataFrame, 
                      user_features_df: pd.DataFrame, 
                      place_features_df: pd.DataFrame) -> pd.DataFrame:
        """Join interaction events with user and place features"""
        # Join user features
        joined_df = interactions_df.merge(user_features_df, on='user_id', how='left')
        
        # Join place features
        joined_df = joined_df.merge(place_features_df, on='place_id', how='left')
        
        # Add context features
        joined_df['hour_of_day'] = joined_df['timestamp'].dt.hour
        joined_df['day_of_week'] = joined_df['timestamp'].dt.dayofweek
        joined_df['is_weekend'] = joined_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate distance between user location and place
        joined_df['distance_km'] = self._calculate_distance(
            joined_df['latitude'], joined_df['longitude'],
            joined_df['home_lat'], joined_df['home_lng']
        )
        
        return joined_df
    
    def _calculate_distance(self, lat1: pd.Series, lon1: pd.Series, 
                          lat2: pd.Series, lon2: pd.Series) -> pd.Series:
        """Calculate haversine distance between two points"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def generate_training_samples(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate positive and negative training samples"""
        logger.info("Generating training samples...")
        
        # Positive samples: actual interactions with good ratings
        positive_samples = df[
            (df['interaction_type'].isin(['visit', 'rating'])) &
            (df['rating'] >= 3)
        ].copy()
        positive_samples['label'] = 1
        
        # Generate negative samples
        negative_samples = self._generate_negative_samples(
            df, len(positive_samples) * self.config.negative_sampling_ratio
        )
        negative_samples['label'] = 0
        
        # Combine positive and negative samples
        training_samples = pd.concat([positive_samples, negative_samples], ignore_index=True)
        
        # Shuffle the dataset
        training_samples = training_samples.sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info(f"Generated {len(positive_samples)} positive and {len(negative_samples)} negative samples")
        return training_samples
    
    def _generate_negative_samples(self, df: pd.DataFrame, n_samples: int) -> pd.DataFrame:
        """Generate negative samples using random and hard negative sampling"""
        logger.info(f"Generating {n_samples} negative samples...")
        
        # Get all unique users and places
        users = df['user_id'].unique()
        places = df['place_id'].unique()
        
        # Create set of positive user-place pairs
        positive_pairs = set(zip(df['user_id'], df['place_id']))
        
        negative_samples = []
        attempts = 0
        max_attempts = n_samples * 10
        
        while len(negative_samples) < n_samples and attempts < max_attempts:
            # Random sampling
            user_id = np.random.choice(users)
            place_id = np.random.choice(places)
            
            # Skip if this is a positive pair
            if (user_id, place_id) in positive_pairs:
                attempts += 1
                continue
            
            # Get user and place features for this negative sample
            user_features = df[df['user_id'] == user_id].iloc[0]
            place_features = df[df['place_id'] == place_id].iloc[0]
            
            # Create negative sample
            negative_sample = {
                'user_id': user_id,
                'place_id': place_id,
                'interaction_type': 'generated_negative',
                'rating': None,
                'timestamp': user_features['timestamp'],
                'latitude': place_features['latitude'],
                'longitude': place_features['longitude']
            }
            
            # Add user features
            for col in ['age_group', 'gender', 'total_interactions', 'avg_rating_given', 
                       'home_lat', 'home_lng', 'exploration_radius', 'active_days_last_month']:
                negative_sample[col] = user_features[col]
            
            # Add place features  
            for col in ['category', 'rating', 'review_count', 'price_level', 
                       'popularity_score', 'weekly_visits']:
                negative_sample[col] = place_features[col]
            
            negative_samples.append(negative_sample)
            attempts += 1
        
        return pd.DataFrame(negative_samples)
    
    def preprocess_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess features for model training"""
        logger.info("Preprocessing features...")
        
        # Encode categorical features
        df['user_id_encoded'] = self.user_encoder.fit_transform(df['user_id'])
        df['place_id_encoded'] = self.place_encoder.fit_transform(df['place_id'])
        df['category_encoded'] = self.category_encoder.fit_transform(df['category'])
        
        # Create age group encoding
        age_group_mapping = {'18-25': 0, '26-35': 1, '36-45': 2, '46-55': 3, '55+': 4}
        df['age_group_encoded'] = df['age_group'].map(age_group_mapping)
        
        # Create gender encoding
        gender_mapping = {'M': 0, 'F': 1, 'O': 2}
        df['gender_encoded'] = df['gender'].map(gender_mapping)
        
        # Select features for training
        feature_columns = [
            'user_id_encoded', 'age_group_encoded', 'gender_encoded',
            'place_id_encoded', 'category_encoded', 'rating', 'price_level',
            'distance_km', 'hour_of_day', 'day_of_week', 'is_weekend'
        ]
        
        X = df[feature_columns].fillna(0)
        y = df['label'].values
        
        # Scale features
        X_scaled = self.feature_scaler.fit_transform(X)
        
        return X_scaled, y


class ModelTrainer:
    """Handles model training and evaluation"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
    def train_model(self, X: np.ndarray, y: np.ndarray) -> tf.keras.Model:
        """Train the recommendation model"""
        logger.info("Starting model training...")
        
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=self.config.test_split, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=self.config.validation_split/(1-self.config.test_split),
            random_state=42, stratify=y_temp
        )
        
        # Create model
        model = self._create_model(X.shape[1])
        
        # Set up callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_auc',
                patience=self.config.early_stopping_patience,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7
            ),
            tf.keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                monitor='val_auc',
                save_best_only=True
            )
        ]
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate on test set
        test_predictions = model.predict(X_test)
        test_metrics = self._evaluate_model(y_test, test_predictions)
        
        logger.info(f"Test metrics: {test_metrics}")
        
        return model, history, test_metrics
    
    def _create_model(self, input_dim: int) -> tf.keras.Model:
        """Create the neural network model"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        return model
    
    def _evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        return {
            'accuracy': accuracy_score(y_true, y_pred_binary),
            'precision': precision_score(y_true, y_pred_binary),
            'recall': recall_score(y_true, y_pred_binary),
            'auc': roc_auc_score(y_true, y_pred)
        }


class HyperparameterTuner:
    """Handles hyperparameter optimization using Optuna"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize hyperparameters using Optuna"""
        logger.info("Starting hyperparameter optimization...")
        
        def objective(trial):
            # Suggest hyperparameters
            embedding_dim = trial.suggest_categorical('embedding_dim', [32, 64, 128])
            learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)
            batch_size = trial.suggest_categorical('batch_size', [512, 1024, 2048])
            dropout_rate = trial.suggest_uniform('dropout_rate', 0.1, 0.5)
            
            # Create model with suggested hyperparameters
            model = self._create_tuning_model(
                X.shape[1], embedding_dim, learning_rate, dropout_rate
            )
            
            # Split data for validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=20,  # Reduced epochs for tuning
                batch_size=batch_size,
                verbose=0
            )
            
            # Return validation AUC
            return max(history.history['val_auc'])
        
        # Run optimization
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=self.config.n_trials)
        
        logger.info(f"Best hyperparameters: {study.best_params}")
        logger.info(f"Best score: {study.best_value}")
        
        return study.best_params
    
    def _create_tuning_model(self, input_dim: int, embedding_dim: int, 
                           learning_rate: float, dropout_rate: float) -> tf.keras.Model:
        """Create model for hyperparameter tuning"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(embedding_dim * 4, activation='relu', input_shape=(input_dim,)),
            tf.keras.layers.Dropout(dropout_rate),
            tf.keras.layers.Dense(embedding_dim * 2, activation='relu'),
            tf.keras.layers.Dropout(dropout_rate),
            tf.keras.layers.Dense(embedding_dim, activation='relu'),
            tf.keras.layers.Dropout(dropout_rate / 2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        return model


class TrainingPipeline:
    """Main training pipeline orchestrator"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.preprocessor = DataPreprocessor(config)
        self.trainer = ModelTrainer(config)
        self.tuner = HyperparameterTuner(config)
        
    def run_training_pipeline(self, tune_hyperparameters: bool = False) -> Dict[str, Any]:
        """Run the complete training pipeline"""
        logger.info("Starting training pipeline...")
        
        # Set up MLflow experiment
        mlflow.set_experiment("nearby-places-recommendation")
        
        with mlflow.start_run() as run:
            # Log configuration
            mlflow.log_params(self.config.to_dict())
            
            # Load and preprocess data
            raw_data = self.preprocessor.load_training_data()
            training_data = self.preprocessor.generate_training_samples(raw_data)
            X, y = self.preprocessor.preprocess_features(training_data)
            
            # Log data statistics
            mlflow.log_metrics({
                "total_samples": len(X),
                "positive_samples": int(np.sum(y)),
                "negative_samples": int(len(y) - np.sum(y)),
                "feature_dim": X.shape[1]
            })
            
            # Optimize hyperparameters if requested
            if tune_hyperparameters:
                best_params = self.tuner.optimize_hyperparameters(X, y)
                mlflow.log_params(best_params)
                
                # Update config with best parameters
                for key, value in best_params.items():
                    setattr(self.config, key, value)
            
            # Train model
            model, history, test_metrics = self.trainer.train_model(X, y)
            
            # Log metrics
            mlflow.log_metrics(test_metrics)
            
            # Log model
            mlflow.tensorflow.log_model(
                model, 
                "model",
                registered_model_name="nearby-places-recommendation"
            )
            
            # Save preprocessing artifacts
            self._save_preprocessing_artifacts()
            
            # Log artifacts
            mlflow.log_artifacts("preprocessing_artifacts/")
            
            logger.info("Training pipeline completed successfully")
            
            return {
                "run_id": run.info.run_id,
                "model": model,
                "metrics": test_metrics,
                "config": self.config
            }
    
    def _save_preprocessing_artifacts(self):
        """Save preprocessing artifacts for inference"""
        os.makedirs("preprocessing_artifacts", exist_ok=True)
        
        # Save encoders and scalers
        with open("preprocessing_artifacts/user_encoder.pkl", "wb") as f:
            pickle.dump(self.preprocessor.user_encoder, f)
            
        with open("preprocessing_artifacts/place_encoder.pkl", "wb") as f:
            pickle.dump(self.preprocessor.place_encoder, f)
            
        with open("preprocessing_artifacts/category_encoder.pkl", "wb") as f:
            pickle.dump(self.preprocessor.category_encoder, f)
            
        with open("preprocessing_artifacts/feature_scaler.pkl", "wb") as f:
            pickle.dump(self.preprocessor.feature_scaler, f)


def main():
    """Main training script"""
    # Configuration
    config = TrainingConfig(
        training_window_days=30,
        embedding_dim=64,
        learning_rate=0.001,
        batch_size=1024,
        epochs=50
    )
    
    # Run training pipeline
    pipeline = TrainingPipeline(config)
    results = pipeline.run_training_pipeline(tune_hyperparameters=False)
    
    print(f"Training completed. Run ID: {results['run_id']}")
    print(f"Test metrics: {results['metrics']}")


if __name__ == "__main__":
    main()