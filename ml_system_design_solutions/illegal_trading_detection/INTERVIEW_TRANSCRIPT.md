# Interview Transcript: Illegal Trading Detection System

*This is a comprehensive interview transcript for designing an illegal trading detection system for social media platforms and marketplaces.*

---

## **Interviewer**: "Design a system to detect illegal trading activities on social media platforms - things like weapons, drugs, stolen goods, and other prohibited items."

## **Candidate**: 

Thank you for this important problem. Illegal trading detection is a critical safety system with significant legal, ethical, and technical challenges. Let me start by clarifying the scope and requirements.

### **1. Problem Clarification & Requirements**

**Candidate**: I'd like to understand the context better:

**Platform Scope**: Are we designing for a specific platform (Facebook Marketplace, Instagram, general social media) or a generic solution? I'll assume a large social platform with both social features and marketplace functionality.

**Content Types**: What types of content should we analyze - posts, comments, private messages, marketplace listings, images, videos? I'll design for multi-modal content (text + images).

**Illegal Categories**: What specific types of illegal trading should we detect? I'll focus on:
- Weapons (firearms, ammunition, knives)
- Drugs and controlled substances  
- Stolen goods (electronics, luxury items)
- Counterfeit products
- Human trafficking related content

**Scale**: What's the expected volume? I'll assume 100M posts/day with ~0.1% containing illegal content (100K violations/day).

**Compliance**: What regulatory requirements must we meet? I'll assume US regulations (FOSTA-SESTA) plus international compliance (GDPR).

### **2. Functional Requirements**

Based on this scope, here are the core requirements:

✅ **Real-time Content Screening**: Screen all new posts/listings as they're created
✅ **Multi-modal Detection**: Analyze text, images, and behavioral patterns
✅ **User Risk Assessment**: Identify high-risk users likely to engage in illegal trading
✅ **Human Review Integration**: Route uncertain cases to human moderators
✅ **Automated Actions**: Remove high-confidence violations automatically
✅ **Compliance Reporting**: Generate reports for law enforcement agencies
✅ **Appeal System**: Allow users to contest moderation decisions

### **3. Non-Functional Requirements**

**Performance**:
- Detection latency: <500ms for real-time screening
- Accuracy: >95% precision, >90% recall
- False positive rate: <2% to maintain user trust

**Scale**:
- 100M posts/day (1,200 QPS average, 5K QPS peak)
- 2B global users across 50+ languages
- 1K human moderators globally

**Compliance**:
- 99.9% uptime for critical safety infrastructure
- <1 hour response for high-severity violations
- Complete audit trails for legal proceedings

### **4. Capacity Estimation**

Let me calculate the system requirements:

**Traffic**:
- 100M posts/day = 1,200 QPS average, 5K QPS peak
- ~100K illegal content detections/day (0.1% hit rate)
- 50M images/day requiring computer vision analysis

**Storage**:
- Content metadata: 10TB/day
- Images: 500TB/day  
- Audit logs: 1TB/day
- ML models: 100GB total

**Infrastructure**:
- API servers: 50 instances for content screening
- ML inference: 20 GPU instances (V100/A100)
- Human moderation: Support 1K concurrent moderators

## **Interviewer**: "That's a good foundation. How would you design the high-level architecture?"

## **Candidate**:

### **5. High-Level System Architecture**

I'll use a **multi-stage detection pipeline** with human oversight:

```
[Content Sources] → [Real-time Screening] → [Risk Assessment] → [Action Engine]
        ↓                    ↓                    ↓               ↓
[Posts/Images] → [ML Detection Pipeline] → [Human Review] → [Content Actions]
[User Actions]   [Multi-modal Analysis]    [Moderation]    [User Actions]
[Metadata]       [Behavioral Signals]      [Appeals]       [Reporting]
```

**Core Components**:

**1. Content Ingestion Layer**
- Kafka streams for real-time content
- API gateway for manual submissions
- Event bus for content lifecycle events

**2. Multi-Modal Detection Pipeline**
- **Text Analysis**: BERT-based classifier + rule-based patterns
- **Computer Vision**: CNN models for object detection (weapons, drugs)
- **Behavioral Analysis**: User risk scoring based on patterns
- **Ensemble Model**: Combine signals for final risk score

**3. Action Decision Engine**
- **Auto-remove**: >95% confidence violations
- **Human review**: 50-95% confidence (uncertain cases)
- **Monitor**: 30-50% confidence (increased surveillance)
- **Allow**: <30% confidence

**4. Human Moderation System**
- Priority routing by violation type and severity
- Moderator tools with AI-provided evidence
- Quality assurance and accuracy tracking
- Escalation paths for serious violations

**5. Compliance & Reporting**
- Law enforcement integration (NCMEC, FBI)
- Regulatory reporting (transparency reports)
- Audit trail management
- Appeal processing system

## **Interviewer**: "How would you approach the ML models for this detection?"

## **Candidate**:

### **6. ML Architecture & Models**

**Multi-Modal Ensemble Approach**:

**Text Classification Model**:
```python
# BERT-based classifier for illegal content
class TextClassifier:
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'bert-base-multilingual-cased', num_labels=2
        )
        # Weapon keywords, drug terms, euphemisms
        self.illegal_patterns = self._load_violation_patterns()
    
    def classify(self, text):
        # Rule-based detection
        rule_score = self._detect_patterns(text)
        
        # BERT classification  
        bert_prediction = self.model(text)
        
        # Weighted combination
        final_score = bert_prediction * 0.7 + rule_score * 0.3
        
        return {
            'probability': final_score,
            'evidence': self._extract_evidence(text)
        }
```

**Computer Vision Model**:
```python
# Multi-object detection for contraband
class ImageClassifier:
    def __init__(self):
        self.weapon_detector = WeaponDetectionCNN()
        self.drug_detector = DrugParaphernaliaCNN()
        self.ocr_engine = OCREngine()
    
    def classify(self, image):
        # Object detection
        objects = self.weapon_detector.detect(image)
        drug_items = self.drug_detector.detect(image)
        
        # OCR text analysis
        text_in_image = self.ocr_engine.extract_text(image)
        text_score = self.text_classifier.classify(text_in_image)
        
        # Combine visual and text evidence
        visual_score = max(objects.confidence, drug_items.confidence)
        final_score = max(visual_score, text_score * 0.7)
        
        return final_score
```

**Behavioral Risk Model**:
```python
# User behavior analysis
class BehaviorAnalyzer:
    def __init__(self):
        self.risk_model = LGBMClassifier()  # Gradient boosting
        self.anomaly_detector = IsolationForest()
    
    def analyze_user(self, user_id):
        features = self._extract_behavioral_features(user_id)
        
        risk_score = self.risk_model.predict_proba(features)
        anomaly_score = self.anomaly_detector.decision_function(features)
        
        return {
            'risk_probability': risk_score,
            'anomaly_score': anomaly_score,
            'risk_factors': self._identify_risk_factors(features)
        }
```

**Ensemble Model**:
```python
# Combine all signals
class IllegalTradingDetector:
    def detect(self, content, user_id):
        # Individual model predictions
        text_result = self.text_classifier.classify(content.text)
        image_result = self.image_classifier.classify(content.images)
        behavior_result = self.behavior_analyzer.analyze_user(user_id)
        
        # Weighted ensemble
        final_probability = (
            text_result['probability'] * 0.4 +
            image_result['probability'] * 0.4 +
            behavior_result['risk_probability'] * 0.2
        )
        
        return {
            'probability': final_probability,
            'confidence': self._calculate_confidence(...),
            'category': self._determine_category(...),
            'evidence': self._compile_evidence(...)
        }
```

**Key Features**:

**Text Features**:
- Weapon/drug keyword detection
- Euphemisms and coded language ("white girl" = cocaine)
- Price mentions + contact information
- Suspicious phrases ("discreet", "cash only")

**Image Features**:
- Object detection (guns, knives, pills, paraphernalia)
- OCR text extraction from images
- Visual similarity to known contraband

**Behavioral Features**:
- Posting frequency and timing patterns
- Network connections to known violators
- Private messaging patterns
- Geographic patterns

## **Interviewer**: "How would you handle the training data and model development?"

## **Candidate**:

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