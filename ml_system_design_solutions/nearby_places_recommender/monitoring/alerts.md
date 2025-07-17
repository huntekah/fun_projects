# Alert Definitions

## Critical Alerts (Page immediately)

### System Availability
```yaml
# Service down alert
- alert: ServiceDown
  expr: up{job="recommendation-service"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Recommendation service is down"
    description: "Recommendation service has been down for more than 1 minute"

# High error rate
- alert: HighErrorRate  
  expr: rate(http_requests_total{code=~"5.."}[5m]) > 0.005
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }}% over the last 5 minutes"
```

### Performance Degradation
```yaml
# High latency alert
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.15
  for: 3m
  labels:
    severity: critical
  annotations:
    summary: "High latency detected"
    description: "95th percentile latency is {{ $value }}s"

# ML model inference timeout
- alert: ModelInferenceTimeout
  expr: rate(model_inference_timeouts_total[5m]) > 0.01
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "ML model inference timeouts"
    description: "Model inference timeout rate: {{ $value }}/second"
```

## Warning Alerts (Notify team)

### Resource Utilization
```yaml
# High CPU usage
- alert: HighCPUUsage
  expr: avg(cpu_usage_percent) > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High CPU usage"
    description: "CPU usage is {{ $value }}%"

# High memory usage
- alert: HighMemoryUsage
  expr: avg(memory_usage_percent) > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage" 
    description: "Memory usage is {{ $value }}%"

# Low cache hit rate
- alert: LowCacheHitRate
  expr: cache_hit_rate < 0.6
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Low cache hit rate"
    description: "Cache hit rate is {{ $value }}%"
```

### Business Metrics
```yaml
# Low CTR
- alert: LowClickThroughRate
  expr: recommendation_ctr < 0.10
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Low recommendation CTR"
    description: "CTR dropped to {{ $value }}%"

# Model drift detected
- alert: ModelDrift
  expr: model_drift_psi_score > 0.15
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Model drift detected"
    description: "PSI score: {{ $value }}"
```

## Information Alerts (Log only)

### Deployment and Scaling
```yaml
# New deployment
- alert: NewDeployment
  expr: changes(deployment_version[1h]) > 0
  labels:
    severity: info
  annotations:
    summary: "New deployment detected"
    description: "Service version changed to {{ $labels.version }}"

# Auto-scaling event
- alert: AutoScaling
  expr: changes(replica_count[5m]) > 0
  labels:
    severity: info
  annotations:
    summary: "Auto-scaling event"
    description: "Replica count changed to {{ $value }}"
```

## Alert Routing

### PagerDuty Integration
```yaml
# Route critical alerts to PagerDuty
global:
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: pagerduty-critical
  - match:
      severity: warning  
    receiver: slack-warnings
  - match:
      severity: info
    receiver: slack-info

receivers:
- name: 'pagerduty-critical'
  pagerduty_configs:
  - routing_key: '<pagerduty-key>'
    description: 'Critical alert: {{ .GroupLabels.alertname }}'
    
- name: 'slack-warnings'
  slack_configs:
  - api_url: '<slack-webhook>'
    channel: '#alerts-warnings'
    title: 'Warning: {{ .GroupLabels.alertname }}'
    
- name: 'slack-info'
  slack_configs:
  - api_url: '<slack-webhook>'
    channel: '#alerts-info'
    title: 'Info: {{ .GroupLabels.alertname }}'
```

## Escalation Policies

### Response Times
- **Critical**: 5 minutes
- **Warning**: 30 minutes  
- **Info**: Best effort

### Escalation Chain
1. **On-call engineer** (0-15 minutes)
2. **Team lead** (15-30 minutes)
3. **Engineering manager** (30-60 minutes)
4. **Director of Engineering** (60+ minutes)

### Runbooks
Each alert includes link to runbook with:
- Symptoms and impact
- Investigation steps
- Common causes and solutions
- Escalation procedures