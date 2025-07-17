# ML System Design Solutions

A comprehensive collection of machine learning system design solutions for real-world problems commonly asked in FAANG interviews and industry applications.

## 📁 Project Structure

Each system design follows a standardized structure (see `TEMPLATE.md`) covering:

- **Requirements**: Functional, non-functional, and constraints
- **Design**: High-level architecture, detailed components, ML pipeline
- **Implementation**: Code examples and data models
- **Scaling**: Capacity planning and optimization strategies
- **Monitoring**: Metrics, alerts, and observability
- **Alternatives**: Trade-offs and future improvements

## 🏗️ System Design Solutions

### Recommendation Systems
- **[Nearby Places Recommender](./nearby_places_recommender/)** - Local place recommendation system
- **[Restaurant Recommender](./restaurant_recommender/)** - Restaurant recommendation engine  
- **[Places Recommendation System](./places_recommendation_system/)** - Large-scale place recommendations (~100M places)
- **[Facebook Marketplace Recommendation](./facebook_marketplace_recommendation/)** - Marketplace feed recommendations
- **[Gaming Video Recommendation](./gaming_video_recommendation/)** - Gaming content recommendation system

### Content & Media Systems
- **[Instagram Short Video Recommendation](./instagram_short_video_recommendation/)** - Short-form video recommendation system

### Data Processing & Classification
- **[Place Deduplication System](./place_deduplication_system/)** - Scalable batch processing for 1B+ place deduplication
- **[Illegal Trading Detection](./illegal_trading_detection/)** - Binary classifier for detecting illegal posts/users (weapons, etc.)

## 🎯 Key ML System Design Patterns

### Common Architecture Components
- **Data Pipeline**: Batch and streaming data processing
- **Feature Store**: Centralized feature management and serving
- **Model Training**: Distributed training and hyperparameter tuning
- **Model Serving**: Real-time and batch inference
- **Experimentation**: A/B testing and feature flagging
- **Monitoring**: Model drift, data quality, and performance tracking

### ML-Specific Considerations
- **Cold Start Problem**: Handling new users/items with no historical data
- **Real-time vs Batch**: Trade-offs between latency and computational cost
- **Model Lifecycle**: Training, validation, deployment, monitoring, retraining cycles
- **Feature Engineering**: Online vs offline feature computation
- **Scalability**: Handling millions of users and billions of items

## 🚀 Getting Started

1. **Choose a system design**: Browse the directories above
2. **Follow the template**: Each system follows the structure in `TEMPLATE.md`
3. **Study the components**: Focus on requirements → design → implementation → scaling
4. **Practice variations**: Modify constraints and see how the design changes

## 💡 Interview Tips

- **Start with requirements**: Always clarify functional and non-functional requirements first
- **Think about scale**: Consider the data volume, traffic patterns, and latency requirements
- **ML-first mindset**: How does the ML model fit into the broader system architecture?
- **Trade-offs**: Be explicit about design trade-offs and alternative approaches
- **Monitoring**: ML systems require extensive monitoring for model and data drift

## 🔧 Tools & Technologies

Common technologies used across these designs:
- **Data Processing**: Spark, Kafka, Airflow, Flink
- **ML Frameworks**: TensorFlow, PyTorch, Scikit-learn, XGBoost
- **Model Serving**: TensorFlow Serving, Seldon, KServe, SageMaker
- **Feature Stores**: Feast, Tecton, AWS Feature Store
- **Databases**: Redis, Elasticsearch, Cassandra, PostgreSQL
- **Infrastructure**: Kubernetes, Docker, AWS/GCP/Azure