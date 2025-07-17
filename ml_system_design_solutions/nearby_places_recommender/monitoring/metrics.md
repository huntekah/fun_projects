# Key Metrics and KPIs

## Business Metrics

### User Engagement
- **Click-Through Rate (CTR)**: % of recommendations clicked
  - Target: >15%
  - Current: 12.8%
  - Alert: <10%

- **Conversion Rate**: % of clicks resulting in visits/bookings  
  - Target: >8%
  - Current: 6.2%
  - Alert: <5%

- **User Retention**: % of users returning within 7 days
  - Target: >40%
  - Current: 38.5%
  - Alert: <30%

### Recommendation Quality
- **Diversity Score**: Category diversity in recommendations
  - Target: >0.7 (Shannon entropy)
  - Current: 0.65
  - Alert: <0.5

- **Novelty Score**: % of recommendations for new places
  - Target: >20%
  - Current: 18.3%
  - Alert: <15%

- **Coverage**: % of places that get recommended
  - Target: >60%
  - Current: 58.7%
  - Alert: <50%

## Technical Metrics

### Performance
- **API Response Time (P95)**: 95th percentile latency
  - Target: <100ms
  - Current: 85ms
  - Alert: >150ms

- **Throughput**: Requests per second
  - Current: 3,200 QPS average, 10,500 QPS peak
  - Alert: <2,000 QPS during business hours

- **Cache Hit Rate**: % of requests served from cache
  - Target: >75%
  - Current: 72.3%
  - Alert: <60%

### Availability
- **System Uptime**: Service availability
  - Target: 99.9% (8.77 hours downtime/year)
  - Current: 99.95%
  - Alert: <99.5%

- **Error Rate**: % of failed requests
  - Target: <0.1%
  - Current: 0.03%
  - Alert: >0.5%

## ML Model Metrics

### Model Performance
- **Offline AUC**: Model accuracy on test set
  - Target: >0.85
  - Current: 0.87
  - Alert: <0.80

- **Online CTR**: Real-world click-through rate
  - Target: >15%
  - Current: 12.8%
  - Alert: <10%

- **Model Drift**: Distribution shift in features
  - PSI Score Target: <0.1
  - Current: 0.08
  - Alert: >0.2

### Inference Metrics
- **Model Latency (P95)**: Inference time
  - Target: <50ms
  - Current: 42ms
  - Alert: >75ms

- **Feature Freshness**: Age of features used
  - Target: <5 minutes
  - Current: 3.2 minutes
  - Alert: >10 minutes

## Infrastructure Metrics

### Resource Utilization
- **CPU Usage**: Average CPU utilization
  - Target: 60-80%
  - Current: 68%
  - Alert: >90%

- **Memory Usage**: Average memory utilization
  - Target: 60-80%
  - Current: 72%
  - Alert: >90%

- **GPU Utilization**: ML inference GPU usage
  - Target: 70-90%
  - Current: 78%
  - Alert: >95%

### Database Performance
- **Query Response Time (P95)**: Database query latency
  - Target: <50ms
  - Current: 32ms
  - Alert: >100ms

- **Connection Pool Usage**: % of connections used
  - Target: <80%
  - Current: 65%
  - Alert: >90%

- **Disk I/O**: Database disk utilization
  - Target: <80%
  - Current: 45%
  - Alert: >90%