# ML Pipeline Design

## Pipeline Overview

```
Data Sources → Feature Engineering → Model Training → Model Serving → Feedback Loop
     ↓               ↓                    ↓              ↓             ↓
[User Interactions] → [Feature Store] → [MLflow] → [TF Serving] → [Analytics]
[Place Data]        → [Validation]   → [A/B Test] → [Monitor]   → [Retrain]
[Context Data]      → [Transform]    → [Deploy]   → [Scale]     → [Improve]
```

## 1. Data Pipeline

### Data Sources
```python
# User interaction events from Kafka
{
  "user_id": 12345,
  "place_id": 67890,
  "event_type": "view|click|visit|rate",
  "timestamp": "2024-01-15T10:30:00Z",
  "context": {
    "search_query": "italian restaurant",
    "location": {"lat": 37.7749, "lng": -122.4194},
    "device": "mobile",
    "session_id": "abc123"
  }
}

# Place metadata updates
{
  "place_id": 67890,
  "updates": {
    "rating": 4.3,
    "review_count": 847,
    "business_hours": {...},
    "attributes": {...}
  }
}

# Context data
{
  "timestamp": "2024-01-15T10:30:00Z",
  "weather": {"temp": 22, "condition": "sunny"},
  "events": ["giants_game", "food_festival"],
  "traffic": {"congestion_level": 0.6}
}
```

### Feature Engineering (Apache Spark)
```python
# User features (daily aggregation)
def compute_user_features(interactions_df):
    return interactions_df.groupBy("user_id").agg(
        # Preference features
        F.collect_list("place_category").alias("visited_categories"),
        F.avg("rating").alias("avg_rating_given"),
        F.count("*").alias("total_interactions"),
        
        # Temporal features  
        F.max("timestamp").alias("last_activity"),
        F.countDistinct("date").alias("active_days"),
        
        # Geographic features
        F.avg("place_lat").alias("home_lat"),
        F.avg("place_lng").alias("home_lng"),
        F.stddev("place_lat").alias("exploration_radius")
    )

# Place features (hourly aggregation)
def compute_place_features(interactions_df, places_df):
    recent_interactions = interactions_df.filter(
        F.col("timestamp") > F.current_timestamp() - F.expr("INTERVAL 7 DAYS")
    )
    
    return recent_interactions.groupBy("place_id").agg(
        # Popularity features
        F.count("*").alias("weekly_visits"),
        F.countDistinct("user_id").alias("unique_visitors"),
        F.avg("rating").alias("avg_rating"),
        
        # Temporal patterns
        F.collect_list("hour_of_day").alias("busy_hours"),
        F.collect_list("day_of_week").alias("busy_days"),
        
        # User demographics visiting
        F.collect_list("user_age_group").alias("visitor_demographics")
    ).join(places_df, "place_id")
```

### Feature Validation & Quality
```python
# Feature validation using Great Expectations
def validate_features(df):
    expectations = [
        # Data quality checks
        {"column": "user_id", "expectation": "not_null"},
        {"column": "place_id", "expectation": "not_null"},
        {"column": "rating", "expectation": "between", "min": 1, "max": 5},
        
        # Drift detection
        {"column": "avg_rating_given", "expectation": "mean_between", "min": 3.0, "max": 4.5},
        {"column": "weekly_visits", "expectation": "std_dev_between", "min": 0, "max": 1000},
        
        # Freshness checks
        {"column": "last_activity", "expectation": "recent", "hours": 24}
    ]
    return apply_expectations(df, expectations)
```

## 2. Model Training Pipeline

### Training Data Generation
```python
# Positive samples: actual user-place interactions
positive_samples = interactions_df.filter(
    F.col("event_type").isin(["visit", "rate"]) &
    (F.col("rating") >= 3)  # Only positive ratings
).select("user_id", "place_id", F.lit(1).alias("label"))

# Negative samples: random sampling + hard negatives
def generate_negative_samples(interactions_df, places_df, ratio=4):
    # Random negatives
    random_negatives = sample_random_user_place_pairs(
        interactions_df, places_df, ratio//2
    )
    
    # Hard negatives: nearby places not visited
    hard_negatives = generate_hard_negatives(
        interactions_df, places_df, ratio//2
    )
    
    return random_negatives.union(hard_negatives)

# Combined training dataset
training_data = positive_samples.union(negative_samples)
```

### Model Architecture
```python
# Two-stage training approach

# Stage 1: Candidate Generation (Matrix Factorization)
def train_candidate_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(num_users, embedding_dim),
        tf.keras.layers.Embedding(num_places, embedding_dim),
        tf.keras.layers.Dot(axes=1),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'auc']
    )
    
    return model

# Stage 2: Ranking Model (Wide & Deep)
def train_ranking_model():
    # Wide component (linear model)
    wide_features = ['distance', 'price_difference', 'rating_difference']
    wide_input = tf.keras.Input(shape=(len(wide_features),))
    wide_output = tf.keras.layers.Dense(1)(wide_input)
    
    # Deep component (neural network)
    deep_features = ['user_embedding', 'place_embedding', 'context_features']
    deep_input = tf.keras.Input(shape=(deep_feature_dim,))
    deep_hidden = tf.keras.layers.Dense(256, activation='relu')(deep_input)
    deep_hidden = tf.keras.layers.Dropout(0.3)(deep_hidden)
    deep_hidden = tf.keras.layers.Dense(128, activation='relu')(deep_hidden)
    deep_output = tf.keras.layers.Dense(1)(deep_hidden)
    
    # Combined output
    combined = tf.keras.layers.Add()([wide_output, deep_output])
    output = tf.keras.layers.Activation('sigmoid')(combined)
    
    model = tf.keras.Model(inputs=[wide_input, deep_input], outputs=output)
    return model
```

### Training Configuration (MLflow)
```python
# MLflow experiment configuration
with mlflow.start_run() as run:
    # Log parameters
    mlflow.log_params({
        "embedding_dim": 64,
        "learning_rate": 0.001,
        "batch_size": 1024,
        "epochs": 50,
        "validation_split": 0.2
    })
    
    # Train model
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=50,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=5),
            tf.keras.callbacks.ReduceLROnPlateau(),
            MLflowCallback()  # Log metrics to MLflow
        ]
    )
    
    # Log model
    mlflow.tensorflow.log_model(model, "ranking_model")
    
    # Log artifacts
    mlflow.log_artifacts("feature_importance.png")
    mlflow.log_artifacts("model_evaluation_report.html")
```

## 3. Model Evaluation & Validation

### Offline Evaluation Metrics
```python
def evaluate_model(model, test_data):
    predictions = model.predict(test_data)
    
    metrics = {
        # Classification metrics
        "auc": roc_auc_score(test_data.labels, predictions),
        "accuracy": accuracy_score(test_data.labels, predictions > 0.5),
        "precision": precision_score(test_data.labels, predictions > 0.5),
        "recall": recall_score(test_data.labels, predictions > 0.5),
        
        # Ranking metrics
        "ndcg@5": ndcg_score(test_data.labels, predictions, k=5),
        "ndcg@10": ndcg_score(test_data.labels, predictions, k=10),
        "map@5": mean_average_precision(test_data.labels, predictions, k=5),
        
        # Business metrics
        "diversity": calculate_diversity(predictions),
        "coverage": calculate_coverage(predictions, total_places),
        "novelty": calculate_novelty(predictions, popular_places)
    }
    
    return metrics
```

### A/B Testing Framework
```python
# Gradual model rollout
def deploy_model_with_ab_test():
    deployment_config = {
        "traffic_split": {
            "control_model": 0.9,    # Current production model
            "treatment_model": 0.1   # New model
        },
        "success_metrics": [
            "click_through_rate",
            "conversion_rate", 
            "user_engagement_time"
        ],
        "guardrail_metrics": [
            "error_rate",
            "response_latency",
            "system_load"
        ],
        "test_duration": "7_days",
        "minimum_sample_size": 10000
    }
    
    return deploy_with_config(deployment_config)
```

## 4. Model Serving

### TensorFlow Serving Configuration
```yaml
# serving_config.yml
model_config_list {
  config {
    name: "candidate_generation"
    base_path: "/models/candidate_generation"
    model_platform: "tensorflow"
    model_version_policy {
      specific {
        versions: 1
      }
    }
  }
  config {
    name: "ranking_model"
    base_path: "/models/ranking_model"  
    model_platform: "tensorflow"
    model_version_policy {
      latest {
        num_versions: 2  # Keep 2 versions for rollback
      }
    }
  }
}
```

### Real-time Inference Pipeline
```python
class RecommendationInference:
    def __init__(self):
        self.candidate_model = load_model("candidate_generation:latest")
        self.ranking_model = load_model("ranking_model:latest")
        self.feature_store = FeatureStore()
        
    async def get_recommendations(self, user_id, lat, lng, limit=20):
        # Step 1: Get nearby places (geographic filtering)
        nearby_places = await self.get_nearby_places(lat, lng, radius=5000)
        
        # Step 2: Candidate generation (collaborative filtering)
        candidates = await self.generate_candidates(user_id, nearby_places, k=200)
        
        # Step 3: Feature enrichment
        features = await self.enrich_features(user_id, candidates, lat, lng)
        
        # Step 4: Ranking
        scores = await self.ranking_model.predict(features)
        
        # Step 5: Post-processing
        recommendations = self.post_process(candidates, scores, limit)
        
        return recommendations
```

## 5. Model Monitoring & Feedback Loop

### Model Performance Monitoring
```python
# Real-time monitoring metrics
monitoring_metrics = {
    # Model performance
    "prediction_latency": "p95 < 50ms",
    "model_accuracy": "accuracy > 0.85",
    "feature_freshness": "lag < 5 minutes",
    
    # Data drift detection
    "feature_drift": "psi_score < 0.1",  # Population Stability Index
    "target_drift": "ks_test_pvalue > 0.05",
    "covariate_shift": "mmd_score < threshold",
    
    # Business metrics
    "click_through_rate": "ctr > baseline * 0.95",
    "conversion_rate": "cvr > baseline * 0.95",
    "user_satisfaction": "rating > 4.0"
}
```

### Automated Retraining Pipeline
```python
# Triggered retraining conditions
retraining_triggers = {
    "scheduled": "weekly",  # Regular scheduled retraining
    "data_drift": "psi_score > 0.2",  # Significant drift detected
    "performance_drop": "accuracy < 0.80",  # Model performance degraded
    "new_data_volume": "interactions > 1M_new_samples"  # Sufficient new data
}

def retrain_pipeline():
    # 1. Data validation
    validate_new_data()
    
    # 2. Feature engineering
    features = compute_features(new_interactions_data)
    
    # 3. Model training
    new_model = train_model(features)
    
    # 4. Model validation
    if validate_model(new_model):
        # 5. A/B testing
        deploy_for_testing(new_model, traffic_percentage=0.1)
    else:
        alert_ml_team("Model validation failed")
```

## 6. Pipeline Orchestration (Apache Airflow)

### DAG Definitions
```python
# Daily feature engineering DAG
daily_feature_dag = DAG(
    'daily_feature_engineering',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1)
)

extract_interactions = SparkSubmitOperator(
    task_id='extract_interactions',
    application='feature_engineering/extract_interactions.py',
    dag=daily_feature_dag
)

compute_user_features = SparkSubmitOperator(
    task_id='compute_user_features',
    application='feature_engineering/user_features.py',
    dag=daily_feature_dag
)

update_feature_store = PythonOperator(
    task_id='update_feature_store',
    python_callable=update_online_features,
    dag=daily_feature_dag
)

extract_interactions >> compute_user_features >> update_feature_store

# Weekly model training DAG
weekly_training_dag = DAG(
    'weekly_model_training',
    schedule_interval='@weekly',
    start_date=datetime(2024, 1, 1)
)

# Training tasks...
```

This ML pipeline design ensures:
- **Scalable feature engineering** with Spark
- **Reproducible model training** with MLflow
- **Safe model deployment** with A/B testing
- **Continuous monitoring** and automated retraining
- **Production-ready serving** with TensorFlow Serving