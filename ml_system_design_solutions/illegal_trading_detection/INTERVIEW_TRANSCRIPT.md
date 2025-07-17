# ML System Design Interview: Illegal Trading Detection

**Problem Statement**: Design a machine learning system to detect illegal trading activities on social media platforms, including weapons, drugs, stolen goods, and other prohibited items.

---

## **Section 1: Problem Scoping & Clarifying Questions**

**Interviewer**: "Design a system to detect illegal trading activities on social media platforms - things like weapons, drugs, stolen goods, and other prohibited items."

**Candidate**: Thank you for this critical safety problem. Before diving into the design, I need to clarify the scope and requirements to ensure I build the right solution.

### **Clarifying Questions**:

**Platform Scope**: Are we designing for a specific platform like Facebook Marketplace, or a generic solution that works across multiple social platforms?

**Content Types**: What types of content should we analyze - text posts, images, videos, private messages, marketplace listings, or all of the above?

**Scale**: What's the expected content volume - posts per day, concurrent users, geographic distribution?

**Illegal Categories**: Which specific illegal trading categories should we prioritize - weapons, drugs, stolen goods, counterfeit items, or others?

**Regulatory Requirements**: What compliance standards must we meet - FOSTA-SESTA, GDPR, regional regulations?

**Performance Expectations**: What are the latency, accuracy, and throughput requirements?

### **Assumptions Based on Clarification**:

Based on our discussion, I'll assume:
- **Platform**: Large social media platform (Facebook-scale) with marketplace functionality
- **Content**: Multi-modal content (text + images) from posts, comments, and marketplace listings
- **Scale**: 100M posts/day, 2B global users, 50+ languages
- **Categories**: Weapons, drugs, stolen goods, counterfeit items, human trafficking
- **Compliance**: US regulations (FOSTA-SESTA), international (GDPR), law enforcement cooperation
- **Performance**: <500ms detection latency, >95% precision, >90% recall

---

## **Section 2: System Goals & Metrics**

### **Primary Goals**:
1. **Safety**: Prevent illegal trading activity on the platform
2. **Compliance**: Meet regulatory requirements and law enforcement cooperation
3. **User Experience**: Minimize false positives to maintain user trust
4. **Scalability**: Handle platform-scale content volume (100M+ posts/day)

### **Success Metrics**:

**Business Metrics**:
- Detection Rate: >90% of illegal content identified
- False Positive Rate: <2% of legitimate content flagged
- Response Time: <1 hour from detection to action
- User Appeals: <5% of removed content appealed

**Technical Metrics**:
- System Latency: P95 <500ms for real-time screening
- Throughput: Handle 5K+ QPS during peak traffic
- Uptime: 99.9% availability for critical safety infrastructure
- Model Performance: >0.92 AUC, >95% precision, >90% recall

**Compliance Metrics**:
- Regulatory Response: <1 hour for CSAM reporting to NCMEC
- Law Enforcement: <24 hour response to legal requests
- Data Retention: 100% compliance with regional data laws
- Audit Coverage: Complete audit trails for all moderation decisions

---

## **Section 3: High-Level System Architecture**

**Interviewer**: "Great! Now walk me through your high-level system architecture."

**Candidate**: I'll design a **multi-stage detection pipeline** with human oversight to balance accuracy and scalability.

### **Architecture Overview**:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Content        │    │  Real-time       │    │  Risk           │    │  Action         │
│  Ingestion      │───▶│  ML Detection    │───▶│  Assessment     │───▶│  Engine         │
│                 │    │  Pipeline        │    │                 │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
   ┌──────────┐          ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
   │  Kafka   │          │ Multi-modal  │       │ Human Review │       │ Automated    │
   │ Streams  │          │ Models       │       │ Queue        │       │ Actions      │
   └──────────┘          │ • Text NLP   │       │              │       │ • Remove     │
                         │ • Image CNN  │       │              │       │ • Flag       │
                         │ • Behavior   │       │              │       │ • Monitor    │
                         └──────────────┘       └──────────────┘       └──────────────┘
```

### **Key Components**:

**1. Content Ingestion Layer**
- Kafka streams for real-time content processing
- API gateway for manual content submissions
- Event-driven architecture for content lifecycle management

**2. ML Detection Pipeline** 
- **Text Classifier**: BERT-based model for illegal content text
- **Image Classifier**: CNN for contraband object detection
- **Behavioral Analyzer**: Gradient boosting for user risk scoring
- **Ensemble Model**: Meta-learner combining all signals

**3. Action Decision System**
- **Confidence-based routing**:
  - >95% confidence → Auto-remove
  - 50-95% confidence → Human review
  - 30-50% confidence → Monitor/shadow ban
  - <30% confidence → Allow

**4. Human-in-the-Loop System**
- Priority-based moderation queue
- AI-assisted review tools with evidence highlighting
- Quality assurance and inter-annotator agreement tracking
- Appeal processing with escalation workflows

### **Technology Stack**:
- **Streaming**: Kafka + Flink for real-time processing
- **ML Serving**: TensorFlow Serving + Kubernetes for auto-scaling
- **Storage**: PostgreSQL (transactional), Redis (caching), Elasticsearch (search)
- **Infrastructure**: AWS multi-region for compliance and latency

---

## **Section 4: Data & Feature Engineering**

**Interviewer**: "Let's dive deeper into the data and features. What data would you collect and how would you engineer features?"

**Candidate**: The success of this system heavily depends on comprehensive data collection and smart feature engineering across multiple modalities.

### **Data Sources**:

**Primary Data**:
- **Content Data**: Posts, comments, marketplace listings, images, videos
- **User Behavior**: Interaction patterns, posting frequency, network connections
- **Moderation Data**: Human moderator decisions, appeals, false positives
- **External Data**: Law enforcement databases (with permissions), known violator lists

**Data Challenges**:
- **Extreme Class Imbalance**: Only ~0.1% of content is illegal
- **Adversarial Behavior**: Bad actors constantly evolving evasion techniques
- **Privacy Constraints**: GDPR/CCPA limitations on data collection
- **Multilingual Content**: 50+ languages with cultural context differences

### **Feature Engineering Strategy**:

**Text Features**:
- **Semantic Features**: BERT embeddings for contextual understanding
- **Lexical Features**: Keyword detection, euphemism mapping, code words
- **Linguistic Features**: Grammar patterns, writing style, urgency indicators
- **Meta Features**: Price mentions, contact info, geographic references

**Image Features**:
- **Object Detection**: YOLO-based detection of weapons, drugs, paraphernalia
- **OCR Text**: Extract and analyze text within images
- **Visual Similarity**: Embedding-based similarity to known contraband
- **Image Metadata**: EXIF data, device info, upload patterns

**Behavioral Features**:
- **Temporal Patterns**: Posting frequency, time-of-day distributions
- **Network Features**: Connection velocity, clustering coefficients, centrality
- **Engagement Patterns**: Like/share ratios, comment patterns, viral signals
- **Historical Features**: Past violations, appeal history, account age

**Feature Store Architecture**:
```python
class FeatureStore:
    def get_features(self, user_id, content_id, timestamp):
        return {
            'real_time': self._get_real_time_features(user_id, timestamp),
            'batch': self._get_batch_features(user_id, lookback_window=30),
            'content': self._get_content_features(content_id),
            'contextual': self._get_contextual_features(user_id, timestamp)
        }
```

---

## **Section 5: Modeling**

**Interviewer**: "Now let's talk about your modeling approach. How would you design the ML models?"

**Candidate**: I'll use a **multi-modal ensemble approach** where specialized models handle different data types, then combine their outputs for final predictions.

### **Model Architecture**:

#### **1. Text Classification Model**

**Approach**: Hybrid BERT + Rule-based system

**Architecture**:
- **Base Model**: BERT-multilingual-cased fine-tuned on illegal content
- **Rule Engine**: Pattern matching for weapons/drugs keywords + euphemisms
- **Ensemble**: Weighted combination (70% BERT, 30% rules)

**Training Strategy**:
- **Data Augmentation**: Synonym replacement, misspelling simulation, code word substitution
- **Hard Negative Mining**: Focus on borderline legal content (antique weapons, toy guns)
- **Multi-task Learning**: Joint training on violation type classification

```python
class TextClassifier:
    def predict(self, text):
        # BERT inference
        bert_logits = self.bert_model(text)
        bert_prob = torch.softmax(bert_logits, dim=-1)[1]  # Illegal class
        
        # Rule-based score
        rule_score = self._calculate_rule_score(text)
        
        # Weighted ensemble
        final_prob = 0.7 * bert_prob + 0.3 * rule_score
        
        return {
            'probability': final_prob,
            'evidence': self._extract_evidence(text),
            'confidence': self._calculate_confidence(bert_prob, rule_score)
        }
```

#### **2. Computer Vision Model**

**Approach**: Multi-stage object detection + OCR analysis

**Architecture**:
- **Object Detection**: YOLOv8 fine-tuned on weapons/drugs/contraband
- **Classification Head**: ResNet-50 for general illegal item classification
- **OCR Pipeline**: Tesseract + text classifier for image text
- **Similarity Matching**: Vector similarity to known contraband database

**Training Considerations**:
- **Synthetic Data**: 3D rendered weapons/drugs for data augmentation
- **Transfer Learning**: Pre-trained on COCO, fine-tuned on contraband dataset
- **Data Privacy**: On-device inference for sensitive content when possible

```python
class ImageClassifier:
    def predict(self, image):
        # Multi-stage detection
        objects = self.object_detector.detect(image)  # YOLO
        classification = self.classifier.predict(image)  # ResNet
        ocr_text = self.ocr_engine.extract_text(image)
        
        # Combine signals
        visual_score = max(
            self._weapon_score(objects),
            self._drug_score(objects),
            classification['illegal_prob']
        )
        
        text_score = self.text_classifier.predict(ocr_text)['probability']
        
        return {
            'probability': max(visual_score, text_score * 0.8),
            'evidence': {
                'objects': objects,
                'ocr_text': ocr_text,
                'visual_similarity': self._find_similar_items(image)
            }
        }
```

#### **3. Behavioral Analysis Model**

**Approach**: Gradient Boosting + Anomaly Detection

**Architecture**:
- **Primary Model**: LightGBM for user risk classification
- **Anomaly Detection**: Isolation Forest for unusual behavior patterns
- **Graph Neural Network**: For network-level suspicious activity detection
- **Time Series**: LSTM for temporal pattern analysis

**Key Features**:
- **Posting Patterns**: Frequency, timing, deletion patterns
- **Network Features**: Connection velocity, clustering, geographic spread
- **Content Patterns**: Text length, image ratio, private messaging
- **Historical Context**: Past violations, appeals, account age

```python
class BehaviorAnalyzer:
    def predict(self, user_id, lookback_days=30):
        # Extract feature vector
        features = self._extract_features(user_id, lookback_days)
        
        # Model predictions
        risk_prob = self.lgb_model.predict_proba([features])[0][1]
        anomaly_score = self.isolation_forest.decision_function([features])[0]
        network_risk = self.gnn_model.predict_user_risk(user_id)
        
        # Combine scores
        final_risk = self._ensemble_behavior_scores(
            risk_prob, anomaly_score, network_risk
        )
        
        return {
            'probability': final_risk,
            'risk_factors': self._identify_risk_factors(features),
            'anomaly_score': anomaly_score,
            'network_flags': self._check_network_indicators(user_id)
        }
```

#### **4. Ensemble Model**

**Approach**: Meta-learning with confidence weighting

**Architecture**:
- **Stage 1**: Individual model predictions (text, image, behavior)
- **Stage 2**: Meta-learner (Logistic Regression) trained on prediction outputs
- **Confidence Weighting**: Higher weight for high-confidence predictions
- **Fallback**: Simple weighted average when meta-learner unavailable

```python
class EnsembleModel:
    def predict(self, content, user_id):
        # Stage 1: Individual predictions
        text_pred = self.text_classifier.predict(content.text)
        image_pred = self.image_classifier.predict(content.images) 
        behavior_pred = self.behavior_analyzer.predict(user_id)
        
        # Stage 2: Meta-learning
        meta_features = [
            text_pred['probability'], text_pred['confidence'],
            image_pred['probability'], image_pred['confidence'],
            behavior_pred['probability'], behavior_pred['confidence'],
            # Cross-modal agreement features
            abs(text_pred['probability'] - image_pred['probability']),
            self._content_user_consistency(content, user_id)
        ]
        
        # Meta-learner prediction
        final_prob = self.meta_learner.predict_proba([meta_features])[0][1]
        
        return {
            'probability': final_prob,
            'confidence': self._ensemble_confidence(text_pred, image_pred, behavior_pred),
            'category': self._determine_violation_category(text_pred, image_pred),
            'evidence': self._compile_evidence(text_pred, image_pred, behavior_pred)
        }
```

### **Model Selection Rationale**:

**Why This Multi-Modal Approach?**
1. **Evasion Robustness**: Hard to fool all modalities simultaneously
2. **Evidence Quality**: Rich evidence for human moderators
3. **Adaptability**: Can weight models based on content type
4. **Accuracy**: Ensemble typically outperforms individual models

**Trade-offs Considered**:
- **Complexity vs Performance**: Accept higher complexity for safety-critical accuracy
- **Latency vs Thoroughness**: Multi-modal analysis worth the 400-500ms latency
- **False Positives vs Misses**: Prioritize recall (catch violations) over precision

---

## **Section 6: Evaluation & Deployment**

**Interviewer**: "How would you evaluate these models and deploy them safely in production?"

**Candidate**: Given the safety-critical nature, I'd implement a comprehensive evaluation and phased deployment strategy.

### **Training Data Strategy**:

**Data Sources & Challenges**:
- **Positive Examples**: Confirmed violations from human moderators, law enforcement data
- **Negative Examples**: Careful sampling from legitimate content
- **Class Imbalance**: 0.1% positive rate requires strategic sampling and cost-sensitive learning
- **Adversarial Examples**: Continuously updated as evasion techniques evolve

**Data Quality Assurance**:
- **Inter-annotator Agreement**: >85% agreement required for training labels
- **Regular Audits**: Monthly review of 10% random samples
- **Bias Detection**: Regular fairness audits across demographics and geographies

### **Evaluation Framework**:

**Offline Evaluation**:
```python
evaluation_metrics = {
    # Performance Metrics
    'precision': 0.96,  # Target: >95% 
    'recall': 0.91,     # Target: >90%
    'f1_score': 0.93,   # Target: >92%
    'auc_roc': 0.94,    # Target: >92%
    
    # Business Metrics  
    'false_positive_rate': 0.018,  # Target: <2%
    'detection_latency_p95': 385,  # Target: <500ms
    
    # Fairness Metrics
    'demographic_parity': 0.07,    # Target: <10% difference
    'equal_opportunity': 0.05,     # Target: <8% difference
    
    # Robustness Metrics
    'adversarial_accuracy': 0.89,  # Target: >85%
    'distribution_shift_auc': 0.91 # Target: >88%
}
```

**Online A/B Testing**:
- **Shadow Mode**: Run new models alongside production without taking actions
- **Canary Deployment**: 5% traffic → 25% → 50% → 100%
- **Champion-Challenger**: Compare against current production model
- **Guardrails**: Automatic rollback if FPR > 3% or detection rate < 85%

### **Deployment Strategy**:

**Phase 1: Shadow Mode (2 weeks)**
- Deploy models to score content without taking actions
- Compare AI decisions with human moderator decisions  
- Calibrate thresholds and measure baseline performance
- **Success Criteria**: >90% agreement with human moderators

**Phase 2: Limited Deployment (4 weeks)**
- 5% traffic to new system
- High-confidence cases only (>90% probability)
- Human oversight for all automated actions
- **Success Criteria**: <2% false positive rate, >85% detection rate

**Phase 3: Gradual Expansion (8 weeks)**
- Scale to 25% → 50% → 75% → 100% traffic
- Lower confidence thresholds progressively
- Regional rollout: English markets first, then multilingual
- **Success Criteria**: Meet all production SLAs

**Monitoring & Alerting**:
```python
monitoring_dashboard = {
    # Real-time Alerts (< 5 min response)
    'model_error_rate': {'threshold': 5, 'current': 1.2},
    'detection_latency_p99': {'threshold': 1000, 'current': 520},
    'false_positive_spike': {'threshold': 3, 'current': 1.8},
    
    # Business Alerts (< 30 min response)
    'detection_rate_drop': {'threshold': 85, 'current': 87.3},
    'user_appeal_spike': {'threshold': 8, 'current': 3.2},
    
    # Model Drift Alerts (< 2 hours response)
    'feature_drift_psi': {'threshold': 0.2, 'current': 0.08},
    'prediction_distribution_shift': {'threshold': 10, 'current': 2.3}
}
```

---

## **Section 7: Follow-ups & Edge Cases**

**Interviewer**: "Great! Let's discuss some challenging scenarios. How would you handle adversarial attacks and evolving evasion techniques?"

**Candidate**: This is one of the most critical aspects - bad actors constantly evolve their techniques, so our system must be adaptive and resilient.

### **Adversarial Robustness**:

**Common Evasion Techniques**:
1. **Text Obfuscation**: "G-U-N" instead of "gun", l33t speak, misspellings
2. **Visual Obfuscation**: Subtle image modifications, partial occlusion, lighting changes
3. **Code Evolution**: Constantly changing slang and euphemisms
4. **Cross-platform Coordination**: Planning on one platform, executing on another
5. **Timing Attacks**: Posting during low-moderation periods

**Defensive Strategies**:
```python
class AdversarialDefense:
    def __init__(self):
        self.evasion_detector = EvasionPatternDetector()
        self.adaptive_threshold = AdaptiveThresholdManager()
        self.continuous_learner = ContinuousLearningPipeline()
    
    def detect_and_adapt(self, content, prediction):
        # Detect potential evasion attempts
        evasion_signals = self.evasion_detector.analyze(content)
        
        # Adjust thresholds dynamically
        if evasion_signals['confidence'] > 0.7:
            self.adaptive_threshold.lower_threshold(content.category)
        
        # Trigger rapid retraining if new patterns detected
        if evasion_signals['novel_pattern']:
            self.continuous_learner.add_sample(content, label='suspicious')
```

### **Challenging Edge Cases**:

**1. Context-Dependent Content**
- **Challenge**: "Water gun for kids" vs "gun for sale"
- **Solution**: Context embeddings, user intent classification, marketplace vs social context

**2. Cultural and Geographic Variations**
- **Challenge**: Legal items in some countries, illegal in others
- **Solution**: Region-specific models, cultural context features, local legal databases

**3. Borderline Legitimate Content**
- **Challenge**: Antique dealers, movie props, educational content
- **Solution**: User verification systems, business account classification, intent signals

**4. Multi-step Coordination**
- **Challenge**: Initial contact on platform, completion off-platform
- **Solution**: Conversation analysis, exit intent detection, cross-platform intelligence sharing

### **Scale Challenges**:

**Real-time Processing at Scale**:
```python
scaling_architecture = {
    'content_volume': '100M posts/day = 1,200 QPS avg, 5K QPS peak',
    'infrastructure': {
        'api_servers': '50 auto-scaling instances',
        'ml_inference': '20 GPU instances (V100/A100)',
        'feature_store': 'Redis cluster with 100K ops/sec',
        'database': 'Sharded PostgreSQL with read replicas'
    },
    'cost_optimization': {
        'model_caching': 'Cache predictions for 1 hour',
        'batch_processing': 'Non-urgent content in daily batches',
        'regional_deployment': 'Edge inference for latency'
    }
}
```

### **Compliance & Ethical Considerations**:

**Privacy vs Safety Balance**:
- **Data Minimization**: Collect only necessary data for detection
- **Encryption**: Balance end-to-end encryption with content scanning
- **Transparency**: Explain decisions while protecting detection methods
- **User Control**: Clear policies and appeal processes

**Bias and Fairness**:
```python
fairness_monitoring = {
    'demographic_parity': {
        'metric': 'Equal detection rates across user groups',
        'target': '<10% difference between groups',
        'current': '7.2% max difference'
    },
    'geographic_fairness': {
        'metric': 'Consistent enforcement globally', 
        'monitoring': 'Regional false positive rate tracking'
    },
    'language_bias': {
        'metric': 'Equal performance across languages',
        'mitigation': 'Language-specific model fine-tuning'
    }
}
```

**Regulatory Compliance**:
- **Real-time Reporting**: NCMEC integration for CSAM (<1 hour SLA)
- **Law Enforcement**: Structured APIs for legal requests
- **Data Residency**: Regional data storage for GDPR compliance
- **Audit Trail**: Immutable logs for all moderation decisions

### **Future Improvements**:

**Short-term (3-6 months)**:
- **Multi-language Support**: Expand beyond English to top 10 languages
- **Video Analysis**: Extend to video content with temporal modeling
- **Federated Learning**: Cross-platform intelligence sharing

**Long-term (6-12 months)**:
- **Advanced NLP**: GPT-based models for better context understanding
- **Graph Neural Networks**: Network-level organized crime detection
- **Multimodal Transformers**: Joint text-image understanding
- **Real-time Learning**: Online learning for rapid adaptation

---

## **Summary & Key Design Decisions**

**Architecture Highlights**:
✓ **Multi-modal Ensemble**: Text + Image + Behavior for comprehensive detection
✓ **Human-in-the-Loop**: AI efficiency with human oversight for accuracy
✓ **Tiered Automation**: Confidence-based routing to optimize resources
✓ **Real-time + Batch**: Immediate protection with continuous improvement
✓ **Global Compliance**: Regional deployment for data residency

**Success Criteria**:
- **Safety**: >90% detection rate, <2% false positive rate
- **Performance**: <500ms latency, 99.9% uptime
- **Compliance**: 100% regulatory adherence, <1 hour response times
- **Fairness**: <10% performance difference across demographics

**This design provides a robust, scalable, and compliant solution for detecting illegal trading activities while balancing automation with human oversight and maintaining user trust through transparency and fairness.**

