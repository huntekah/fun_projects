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

### **7. Training Data & Model Development**

**Training Data Challenges**:

**Data Sources**:
- **Confirmed violations**: Content removed by human moderators
- **Law enforcement data**: Known illegal content (with permissions)
- **Synthetic data**: Generated examples for rare categories
- **Negative samples**: Legitimate content (carefully sampled)

**Class Imbalance Problem**:
- Only 0.1% of content is illegal (severe imbalance)
- Use stratified sampling and cost-sensitive learning
- Generate hard negative examples near decision boundary

**Data Augmentation**:
```python
class DataAugmenter:
    def augment_text(self, illegal_text):
        # Misspelling simulation
        # Synonym replacement  
        # Code word substitution
        # Character substitution (l33t speak)
        
    def augment_images(self, illegal_images):
        # Rotation, scaling, lighting changes
        # Background substitution
        # Partial occlusion simulation
```

**Training Pipeline**:
```python
class TrainingPipeline:
    def run_training(self):
        # 1. Data collection and labeling
        training_data = self.collect_training_data()
        
        # 2. Data validation and quality checks
        validated_data = self.validate_data_quality(training_data)
        
        # 3. Feature engineering
        features = self.extract_features(validated_data)
        
        # 4. Model training with cross-validation
        models = self.train_ensemble_models(features)
        
        # 5. Bias and fairness evaluation
        fairness_results = self.evaluate_fairness(models)
        
        # 6. A/B testing preparation
        self.deploy_for_testing(models)
```

**Model Evaluation**:
- **Accuracy metrics**: Precision >95%, Recall >90%, F1 >92%
- **Fairness metrics**: Equal performance across demographics
- **Robustness testing**: Adversarial examples and edge cases
- **Human evaluation**: Moderator agreement with model decisions

## **Interviewer**: "How would you handle the operational aspects - scaling, monitoring, compliance?"

## **Candidate**:

### **8. Operational Excellence**

**Scaling Strategy**:

**Real-time Inference**:
- Auto-scaling Kubernetes pods based on queue length
- GPU inference with TensorFlow Serving
- Multi-level caching (Redis + application cache)
- Regional deployment for latency optimization

**Human Moderation Scale**:
- 1K moderators across global time zones
- Intelligent routing: weapons to specialized teams
- Quality assurance: 10% random sampling for accuracy
- Training pipeline: Regular updates on new violation patterns

**Monitoring & Alerting**:

**Business Metrics**:
- Detection rate: >90% (currently 87.3%)
- False positive rate: <2% (currently 1.8%)
- Content removal time: <1 hour (currently 42 min)
- User appeal rate: <5% (currently 3.2%)

**Technical Metrics**:
- API latency: P95 <500ms (currently 385ms)
- Model accuracy: AUC >0.92 (currently 0.94)
- System uptime: >99.9% (currently 99.95%)

**Model Drift Detection**:
- Population Stability Index (PSI) monitoring
- Prediction distribution drift alerts
- Automatic retraining triggers
- A/B testing for model updates

**Compliance & Legal**:

**Regulatory Requirements**:
- NCMEC reporting: <1 hour for CSAM (currently 23 min)
- Law enforcement cooperation: <24 hour response
- Data retention: 90 days user data, 7 years audit logs
- Cross-border compliance: GDPR Article 44 adherence

**Audit & Evidence**:
- Complete audit trails for all moderation decisions
- Evidence preservation for legal proceedings
- Chain of custody for criminal investigations
- Regular compliance audits and assessments

### **9. Edge Cases & Challenges**

**Adversarial Evasion**:
- **Text obfuscation**: "G-U-N" instead of "gun"
- **Visual obfuscation**: Subtle image modifications
- **Code evolution**: Constantly changing slang and euphemisms
- **Cross-platform coordination**: Planning on one platform, executing on another

**Solutions**:
- Continuous model updates with new evasion patterns
- Adversarial training with known evasion techniques
- Human-AI collaboration for novel pattern detection
- Cross-platform intelligence sharing (industry cooperation)

**False Positives Impact**:
- **Legitimate sellers**: Antique dealers, historical items, toys
- **Context matters**: "water gun" vs "gun", movie props
- **Cultural differences**: Legal items in some countries, illegal in others

**Mitigation**:
- Context-aware models with semantic understanding
- Human review for borderline cases
- User education about platform policies
- Rapid appeal resolution process (<24 hours)

### **10. Ethical Considerations**

**Bias and Fairness**:
- **Demographic bias**: Equal detection across age, gender, race
- **Geographic bias**: Consistent enforcement globally
- **Economic bias**: Not targeting lower-income users disproportionately

**Privacy vs Safety**:
- **Data minimization**: Collect only necessary data for detection
- **Encryption**: End-to-end encryption vs content scanning tension
- **Transparency**: Explain moderation decisions while protecting detection methods

**Human Rights**:
- **Freedom of expression**: Balance safety with legitimate speech
- **Due process**: Fair appeal process and human review
- **Proportional response**: Graduated penalties, not just bans

## **Interviewer**: "What would be your deployment and testing strategy?"

## **Candidate**:

### **11. Deployment & Testing Strategy**

**Phased Rollout**:

**Phase 1: Shadow Mode (2 weeks)**
- Deploy models to score content without taking action
- Compare AI decisions with human moderator decisions
- Measure false positive/negative rates
- Calibrate thresholds for production

**Phase 2: Limited Deployment (4 weeks)**
- 5% traffic to new system
- Focus on high-confidence cases (>90% probability)
- Human oversight for all automated actions
- Monitor business metrics and user feedback

**Phase 3: Gradual Expansion (8 weeks)**
- Increase to 25%, 50%, 75%, 100% traffic
- Lower confidence thresholds as confidence builds
- Regional rollout: Start with English-speaking markets
- Expand to additional violation categories

**A/B Testing Framework**:
- **Control group**: Current human-only moderation
- **Treatment group**: AI + human hybrid system
- **Metrics**: Detection rate, false positives, response time
- **Statistical significance**: 95% confidence level

**Rollback Strategy**:
- **Automated rollback**: If error rate >5% or latency >2x baseline
- **Manual rollback**: Operations team can instantly revert
- **Gradual rollback**: Reduce traffic to problematic models
- **Emergency mode**: Fall back to human-only moderation

### **12. Success Metrics & Business Impact**

**Platform Safety**:
- 90%+ reduction in illegal content reaching users
- 50%+ reduction in time illegal content remains live
- 95%+ user satisfaction with platform safety

**Operational Efficiency**:
- 3x increase in content reviewed per moderator
- 60% reduction in moderator review queue backlog
- 80% of violations caught automatically

**Legal & Compliance**:
- Zero regulatory fines for non-compliance
- 100% of legal requests fulfilled within SLA
- Positive law enforcement cooperation feedback

**Business Impact**:
- Reduced legal liability and regulatory risk
- Improved advertiser confidence and brand safety
- Enhanced user trust and platform reputation

## **Interviewer**: "Excellent. Any final thoughts on this design?"

## **Candidate**:

### **13. Summary & Key Design Principles**

This illegal trading detection system balances several critical principles:

**Safety First**: Prioritize user safety and legal compliance over false positive concerns
**Human Oversight**: Maintain human judgment for complex ethical decisions
**Transparency**: Provide clear explanations for moderation decisions
**Scalability**: Handle platform-scale content (100M posts/day) with low latency
**Adaptability**: Continuously evolve to counter new evasion techniques

**Key Technical Decisions**:
1. **Multi-modal ensemble**: Text + image + behavior for comprehensive detection
2. **Human-in-the-loop**: AI efficiency with human oversight for accuracy
3. **Tiered automation**: Confidence-based routing to optimize resources
4. **Real-time + batch**: Immediate protection with continuous improvement
5. **Global compliance**: Regional deployment for data residency requirements

**Success Factors**:
- **Model accuracy**: >95% precision to maintain user trust
- **Response speed**: <500ms detection for real-time protection
- **Human expertise**: Well-trained moderators for complex decisions
- **Continuous learning**: Rapid adaptation to new violation patterns
- **Legal compliance**: Proactive regulatory adherence

**Future Evolution**:
- Advanced NLP for better context understanding
- Computer vision improvements for novel contraband detection
- Behavioral analysis for organized illegal trading rings
- Cross-platform intelligence sharing for comprehensive protection

This system provides a robust foundation for platform safety while respecting user rights and maintaining operational efficiency at scale.

---

*This completes a comprehensive system design interview for an illegal trading detection system, covering all major aspects from requirements gathering to implementation details, operational considerations, and ethical implications.*