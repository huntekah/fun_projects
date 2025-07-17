# ML Pipeline Design

## Pipeline Overview

```
Data Sources → Feature Engineering → Model Training → Model Serving → Feedback Loop
     ↓               ↓                    ↓              ↓             ↓
[Raw Content] → [Feature Store] → [MLflow Training] → [TF Serving] → [Human Labels]
[User Actions]  [Text/Image/Behavioral] [A/B Testing] [Real-time]   [Model Updates]
[Moderation]    [Real-time/Batch]      [Hyperopt]    [Batch]       [Drift Detection]
```

## 1. Data Collection & Preprocessing

### Data Sources
```python
# Primary data sources for illegal trading detection
data_sources = {
    'content_stream': {
        'posts': 'Real-time user posts and comments',
        'images': 'User-uploaded images and videos', 
        'messages': 'Private messages (with consent)',
        'marketplace_listings': 'Product listings and descriptions'
    },
    'user_behavior': {
        'interaction_patterns': 'Clicks, likes, shares, saves',
        'network_connections': 'Friend/follow relationships',
        'location_data': 'Geographic patterns (anonymized)',
        'temporal_patterns': 'Posting times and frequency'
    },
    'moderation_feedback': {
        'human_labels': 'Moderator decisions and rationale',
        'appeals': 'User appeals and outcomes',
        'false_positives': 'Incorrectly flagged content',
        'missed_violations': 'Human-caught violations missed by AI'
    }
}
```

### Data Preprocessing Pipeline
```python
class ContentPreprocessor:
    """Preprocess content for illegal trading detection"""
    
    def __init__(self):
        self.text_processor = TextPreprocessor()
        self.image_processor = ImagePreprocessor()
        self.behavior_processor = BehaviorPreprocessor()
    
    def process_content(self, content_item):
        """Process mixed content (text + images + metadata)"""
        features = {}
        
        # Text processing
        if content_item.text:
            features['text'] = self.text_processor.process(content_item.text)
        
        # Image processing
        if content_item.images:
            features['images'] = [
                self.image_processor.process(img) 
                for img in content_item.images
            ]
        
        # Behavioral features
        features['behavior'] = self.behavior_processor.process(
            content_item.user_id, 
            content_item.timestamp
        )
        
        return features

class TextPreprocessor:
    """Text preprocessing for illegal content detection"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.normalizer = TextNormalizer()
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual')
    
    def process(self, text):
        """Extract features from text content"""
        # Language detection
        language = self.language_detector.detect(text)
        
        # Text normalization
        normalized_text = self.normalizer.normalize(text, language)
        
        # Feature extraction
        features = {
            'language': language,
            'length': len(text),
            'word_count': len(text.split()),
            'contains_urls': bool(re.search(r'http[s]?://', text)),
            'contains_contact': self._extract_contact_info(text),
            'price_mentions': self._extract_prices(text),
            'location_mentions': self._extract_locations(text),
            'suspicious_phrases': self._detect_suspicious_phrases(text),
            'encoded_text': self.tokenizer(normalized_text, max_length=512, truncation=True)
        }
        
        return features
    
    def _detect_suspicious_phrases(self, text):
        """Detect coded language and euphemisms"""
        suspicious_patterns = [
            r'\b(discreet|discrete)\b',  # Common in illegal trading
            r'\bmeet\s+in\s+person\b',   # Offline coordination
            r'\bcash\s+only\b',          # Avoid payment tracking
            r'\bno\s+questions\b',       # Avoid scrutiny
            r'\bfast\s+delivery\b',      # Suspicious for certain items
        ]
        
        matches = []
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        
        return matches
```

### Image Preprocessing Pipeline
```python
class ImagePreprocessor:
    """Image preprocessing for contraband detection"""
    
    def __init__(self):
        self.object_detector = ObjectDetector()
        self.ocr_engine = OCREngine()
        self.feature_extractor = ImageFeatureExtractor()
    
    def process(self, image_data):
        """Extract features from image content"""
        image = self._load_image(image_data)
        
        features = {
            'dimensions': image.shape,
            'file_size': len(image_data),
            'objects': self.object_detector.detect(image),
            'text_content': self.ocr_engine.extract_text(image),
            'visual_features': self.feature_extractor.extract(image),
            'metadata': self._extract_metadata(image_data)
        }
        
        # Check for suspicious objects
        features['weapon_detected'] = self._check_weapons(features['objects'])
        features['drug_paraphernalia'] = self._check_drug_items(features['objects'])
        features['suspicious_text'] = self._analyze_image_text(features['text_content'])
        
        return features
    
    def _check_weapons(self, detected_objects):
        """Check for weapon-related objects"""
        weapon_classes = [
            'rifle', 'pistol', 'gun', 'ammunition', 'bullet',
            'knife', 'blade', 'tactical_gear', 'body_armor'
        ]
        
        for obj in detected_objects:
            if obj['class'] in weapon_classes and obj['confidence'] > 0.7:
                return True
        
        return False
```

## 2. Feature Engineering

### Feature Store Architecture
```python
class IllegalTradingFeatureStore:
    """Centralized feature store for illegal trading detection"""
    
    def __init__(self):
        self.online_store = Redis()  # Real-time features
        self.offline_store = PostgreSQL()  # Historical features
        self.feature_registry = FeatureRegistry()
    
    def get_user_features(self, user_id, timestamp):
        """Get user behavioral features"""
        features = {
            # Historical features (offline store)
            'violation_count_30d': self._get_historical_violations(user_id, days=30),
            'avg_posting_frequency': self._get_posting_frequency(user_id),
            'network_risk_score': self._get_network_risk(user_id),
            'account_age_days': self._get_account_age(user_id),
            
            # Real-time features (online store)
            'recent_activity_score': self._get_recent_activity(user_id),
            'current_location_risk': self._get_location_risk(user_id, timestamp),
            'device_fingerprint_risk': self._get_device_risk(user_id),
        }
        
        return features
    
    def get_content_features(self, content_id):
        """Get content-specific features"""
        features = {
            'text_features': self._get_text_features(content_id),
            'image_features': self._get_image_features(content_id),
            'engagement_features': self._get_engagement_features(content_id),
            'temporal_features': self._get_temporal_features(content_id)
        }
        
        return features

class BehavioralFeatureExtractor:
    """Extract behavioral features for user risk assessment"""
    
    def extract_user_patterns(self, user_id, lookback_days=30):
        """Extract user behavioral patterns"""
        user_actions = self._get_user_actions(user_id, lookback_days)
        
        features = {
            # Posting patterns
            'posting_frequency': len(user_actions) / lookback_days,
            'posts_per_hour_distribution': self._get_hourly_distribution(user_actions),
            'weekend_posting_ratio': self._get_weekend_ratio(user_actions),
            
            # Content patterns
            'avg_text_length': np.mean([len(a.text) for a in user_actions if a.text]),
            'image_posting_ratio': sum(1 for a in user_actions if a.images) / len(user_actions),
            'url_sharing_frequency': sum(1 for a in user_actions if 'http' in a.text) / len(user_actions),
            
            # Interaction patterns
            'private_message_ratio': sum(1 for a in user_actions if a.type == 'private') / len(user_actions),
            'cross_platform_activity': self._check_cross_platform_patterns(user_id),
            'rapid_deletion_pattern': self._check_deletion_patterns(user_actions),
            
            # Network features
            'new_connections_rate': self._get_new_connections_rate(user_id),
            'connection_risk_score': self._get_connection_risk_score(user_id),
            'geographic_spread': self._get_geographic_spread(user_actions)
        }
        
        return features
```

## 3. Model Architecture

### Multi-Modal Ensemble Model
```python
class IllegalTradingDetector:
    """Multi-modal ensemble for illegal trading detection"""
    
    def __init__(self):
        self.text_classifier = TextClassifier()
        self.image_classifier = ImageClassifier() 
        self.behavior_classifier = BehaviorClassifier()
        self.ensemble_model = EnsembleModel()
    
    def predict(self, content_features, user_features):
        """Predict illegal trading probability"""
        
        # Individual model predictions
        text_pred = self.text_classifier.predict(content_features['text'])
        image_pred = self.image_classifier.predict(content_features['images'])
        behavior_pred = self.behavior_classifier.predict(user_features)
        
        # Ensemble prediction
        ensemble_features = {
            'text_prob': text_pred['probability'],
            'image_prob': image_pred['probability'],
            'behavior_prob': behavior_pred['probability'],
            'text_confidence': text_pred['confidence'],
            'image_confidence': image_pred['confidence'],
            'behavior_confidence': behavior_pred['confidence']
        }
        
        final_prediction = self.ensemble_model.predict(ensemble_features)
        
        return {
            'probability': final_prediction['probability'],
            'confidence': final_prediction['confidence'],
            'category': self._determine_category(text_pred, image_pred),
            'evidence': self._compile_evidence(text_pred, image_pred, behavior_pred)
        }

class TextClassifier:
    """BERT-based text classifier for illegal content"""
    
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'bert-base-multilingual-cased',
            num_labels=2  # Binary: legal vs illegal
        )
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        
    def predict(self, text_features):
        """Classify text content as legal/illegal"""
        
        # Prepare input
        inputs = self.tokenizer(
            text_features['normalized_text'],
            max_length=512,
            truncation=True,
            padding=True,
            return_tensors='pt'
        )
        
        # Model inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            
        illegal_prob = probabilities[0][1].item()
        confidence = max(probabilities[0]).item()
        
        # Extract evidence
        evidence = {
            'suspicious_phrases': text_features['suspicious_phrases'],
            'price_mentions': text_features['price_mentions'],
            'contact_info': text_features['contains_contact']
        }
        
        return {
            'probability': illegal_prob,
            'confidence': confidence,
            'evidence': evidence
        }

class ImageClassifier:
    """CNN-based image classifier for contraband detection"""
    
    def __init__(self):
        self.weapon_detector = WeaponDetector()
        self.drug_detector = DrugDetector()
        self.general_classifier = GeneralIllegalItemClassifier()
    
    def predict(self, image_features):
        """Classify images for illegal items"""
        
        predictions = []
        
        for image_feature in image_features:
            # Specialized detectors
            weapon_result = self.weapon_detector.detect(image_feature)
            drug_result = self.drug_detector.detect(image_feature)
            general_result = self.general_classifier.classify(image_feature)
            
            # Combine results
            max_prob = max(
                weapon_result['probability'],
                drug_result['probability'], 
                general_result['probability']
            )
            
            category = self._determine_category(weapon_result, drug_result, general_result)
            
            predictions.append({
                'probability': max_prob,
                'category': category,
                'objects_detected': image_feature['objects'],
                'ocr_text': image_feature['text_content']
            })
        
        # Aggregate multiple images
        if predictions:
            max_prediction = max(predictions, key=lambda x: x['probability'])
            return {
                'probability': max_prediction['probability'],
                'confidence': max_prediction['probability'],  # Simplified
                'evidence': {
                    'detected_objects': max_prediction['objects_detected'],
                    'image_text': max_prediction['ocr_text'],
                    'category': max_prediction['category']
                }
            }
        else:
            return {'probability': 0.0, 'confidence': 0.0, 'evidence': {}}
```

### Behavior Analysis Model
```python
class BehaviorClassifier:
    """Gradient boosting model for user behavior analysis"""
    
    def __init__(self):
        self.model = LGBMClassifier(
            objective='binary',
            metric='auc',
            num_leaves=100,
            learning_rate=0.1,
            feature_fraction=0.8,
            bagging_fraction=0.8,
            bagging_freq=5,
            verbose=-1
        )
        self.feature_names = self._define_feature_names()
    
    def predict(self, user_features):
        """Predict user risk based on behavioral patterns"""
        
        # Convert features to model input format
        feature_vector = self._encode_features(user_features)
        
        # Model prediction
        probability = self.model.predict_proba([feature_vector])[0][1]
        confidence = abs(probability - 0.5) * 2  # Distance from uncertainty
        
        # Feature importance for explanation
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        return {
            'probability': probability,
            'confidence': confidence,
            'evidence': {
                'top_risk_factors': self._get_top_risk_factors(
                    feature_vector, feature_importance
                ),
                'risk_score_breakdown': self._breakdown_risk_score(feature_vector)
            }
        }
    
    def _encode_features(self, user_features):
        """Encode user features for model input"""
        encoded = []
        
        # Temporal features
        encoded.append(user_features['posting_frequency'])
        encoded.append(user_features['weekend_posting_ratio'])
        
        # Content features  
        encoded.append(user_features['avg_text_length'])
        encoded.append(user_features['image_posting_ratio'])
        encoded.append(user_features['url_sharing_frequency'])
        
        # Network features
        encoded.append(user_features['new_connections_rate'])
        encoded.append(user_features['connection_risk_score'])
        
        # Historical features
        encoded.append(user_features['violation_count_30d'])
        encoded.append(user_features['account_age_days'])
        
        return encoded
```

## 4. Training Pipeline

### Training Data Generation
```python
class TrainingDataGenerator:
    """Generate training data for illegal trading detection"""
    
    def __init__(self):
        self.positive_sources = PositiveExampleSources()
        self.negative_sources = NegativeExampleSources()
        self.data_augmenter = DataAugmenter()
    
    def generate_training_data(self, start_date, end_date):
        """Generate balanced training dataset"""
        
        # Positive examples (illegal content)
        positive_examples = []
        positive_examples.extend(self.positive_sources.get_confirmed_violations(start_date, end_date))
        positive_examples.extend(self.positive_sources.get_law_enforcement_data())
        positive_examples.extend(self.positive_sources.get_synthetic_examples())
        
        # Negative examples (legal content)
        negative_examples = []
        negative_examples.extend(self.negative_sources.get_random_legitimate_content(start_date, end_date))
        negative_examples.extend(self.negative_sources.get_marketplace_listings())
        negative_examples.extend(self.negative_sources.get_social_posts())
        
        # Balance dataset
        positive_count = len(positive_examples)
        negative_examples = random.sample(negative_examples, positive_count * 3)  # 1:3 ratio
        
        # Data augmentation
        augmented_positives = self.data_augmenter.augment_positive_examples(positive_examples)
        
        # Combine and shuffle
        all_examples = positive_examples + augmented_positives + negative_examples
        random.shuffle(all_examples)
        
        return all_examples
    
    def create_hard_negatives(self, model, negative_examples):
        """Create hard negative examples for improved training"""
        
        hard_negatives = []
        
        for example in negative_examples:
            prediction = model.predict(example.features)
            
            # Keep examples that model incorrectly classifies as positive
            if prediction['probability'] > 0.3:  # False positive threshold
                hard_negatives.append(example)
        
        return hard_negatives

class DataAugmenter:
    """Augment training data to improve model robustness"""
    
    def augment_positive_examples(self, positive_examples):
        """Create variations of positive examples"""
        
        augmented = []
        
        for example in positive_examples:
            # Text augmentation
            if example.text:
                augmented.extend(self._augment_text(example))
            
            # Image augmentation
            if example.images:
                augmented.extend(self._augment_images(example))
        
        return augmented
    
    def _augment_text(self, example):
        """Augment text examples with variations"""
        augmentations = []
        
        # Synonym replacement
        augmentations.append(self._replace_synonyms(example))
        
        # Misspelling simulation
        augmentations.append(self._add_misspellings(example))
        
        # Code word substitution
        augmentations.append(self._substitute_code_words(example))
        
        # Character substitution (l33t speak)
        augmentations.append(self._character_substitution(example))
        
        return augmentations
```

### Model Training Pipeline
```python
class TrainingPipeline:
    """ML training pipeline for illegal trading detection"""
    
    def __init__(self):
        self.data_generator = TrainingDataGenerator()
        self.feature_processor = FeatureProcessor()
        self.model_trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()
    
    def run_training_pipeline(self, config):
        """Execute complete training pipeline"""
        
        # Generate training data
        logger.info("Generating training data...")
        training_data = self.data_generator.generate_training_data(
            config.start_date, config.end_date
        )
        
        # Feature processing
        logger.info("Processing features...")
        features, labels = self.feature_processor.process_dataset(training_data)
        
        # Train/validation split
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=0.2, stratify=labels, random_state=42
        )
        
        # Model training
        logger.info("Training models...")
        models = {}
        
        # Train individual models
        models['text'] = self.model_trainer.train_text_model(X_train, y_train)
        models['image'] = self.model_trainer.train_image_model(X_train, y_train)
        models['behavior'] = self.model_trainer.train_behavior_model(X_train, y_train)
        
        # Train ensemble model
        ensemble_features = self._generate_ensemble_features(models, X_train)
        models['ensemble'] = self.model_trainer.train_ensemble_model(
            ensemble_features, y_train
        )
        
        # Model evaluation
        logger.info("Evaluating models...")
        validation_results = self.evaluator.evaluate_models(models, X_val, y_val)
        
        # Hyperparameter tuning
        if config.tune_hyperparameters:
            logger.info("Tuning hyperparameters...")
            models = self._tune_hyperparameters(models, X_train, y_train, X_val, y_val)
        
        # Final evaluation
        final_results = self.evaluator.evaluate_models(models, X_val, y_val)
        
        # Model deployment
        if final_results['ensemble']['f1_score'] > config.deployment_threshold:
            logger.info("Deploying models...")
            self._deploy_models(models, final_results)
        
        return models, final_results

class ModelEvaluator:
    """Evaluate model performance with focus on fairness and bias"""
    
    def evaluate_models(self, models, X_test, y_test):
        """Comprehensive model evaluation"""
        
        results = {}
        
        for model_name, model in models.items():
            predictions = model.predict(X_test)
            probabilities = model.predict_proba(X_test)[:, 1]
            
            # Standard metrics
            results[model_name] = {
                'accuracy': accuracy_score(y_test, predictions),
                'precision': precision_score(y_test, predictions),
                'recall': recall_score(y_test, predictions),
                'f1_score': f1_score(y_test, predictions),
                'auc_score': roc_auc_score(y_test, probabilities),
                'false_positive_rate': self._calculate_fpr(y_test, predictions),
                'false_negative_rate': self._calculate_fnr(y_test, predictions)
            }
            
            # Fairness evaluation
            results[model_name]['fairness'] = self._evaluate_fairness(
                model, X_test, y_test, predictions
            )
            
            # Robustness testing
            results[model_name]['robustness'] = self._evaluate_robustness(
                model, X_test, y_test
            )
        
        return results
    
    def _evaluate_fairness(self, model, X_test, y_test, predictions):
        """Evaluate model fairness across different groups"""
        
        fairness_metrics = {}
        
        # Evaluate by user demographics (if available)
        for demographic in ['age_group', 'gender', 'location']:
            if demographic in X_test.columns:
                fairness_metrics[demographic] = self._demographic_parity(
                    X_test[demographic], predictions
                )
        
        # Evaluate by content language
        if 'language' in X_test.columns:
            fairness_metrics['language'] = self._language_fairness(
                X_test['language'], predictions
            )
        
        return fairness_metrics
```

## 5. Model Serving & Inference

### Real-time Inference Pipeline
```python
class RealTimeInferenceService:
    """Real-time inference service for content screening"""
    
    def __init__(self):
        self.model_ensemble = self._load_models()
        self.feature_store = FeatureStore()
        self.cache = Redis()
        
    async def screen_content(self, content_request):
        """Screen content for illegal trading activity"""
        
        start_time = time.time()
        
        try:
            # Extract features
            content_features = await self._extract_content_features(content_request)
            user_features = await self._get_user_features(content_request.user_id)
            
            # Model inference
            prediction = self.model_ensemble.predict(content_features, user_features)
            
            # Generate response
            response = {
                'screening_id': str(uuid.uuid4()),
                'risk_score': prediction['probability'],
                'confidence': prediction['confidence'],
                'categories': prediction.get('categories', []),
                'action': self._determine_action(prediction),
                'evidence': prediction.get('evidence', {}),
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
            
            # Log for monitoring
            await self._log_screening_result(content_request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Screening error: {e}")
            # Fail safely - allow content through with warning
            return {
                'screening_id': str(uuid.uuid4()),
                'risk_score': 0.0,
                'confidence': 0.0,
                'action': 'allow_with_monitoring',
                'error': 'screening_service_error'
            }
    
    def _determine_action(self, prediction):
        """Determine action based on prediction"""
        
        probability = prediction['probability']
        confidence = prediction['confidence']
        
        if probability > 0.9 and confidence > 0.8:
            return 'auto_remove'
        elif probability > 0.7 and confidence > 0.6:
            return 'human_review'
        elif probability > 0.3:
            return 'monitor'
        else:
            return 'allow'

class BatchInferenceService:
    """Batch inference for historical content rescanning"""
    
    def __init__(self):
        self.model_ensemble = self._load_models()
        self.batch_processor = BatchProcessor()
    
    def rescan_historical_content(self, date_range, batch_size=10000):
        """Rescan historical content with updated models"""
        
        content_batches = self.batch_processor.get_content_batches(
            date_range, batch_size
        )
        
        results = []
        
        for batch in content_batches:
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Update moderation queue with new violations
            self._update_moderation_queue(batch_results)
        
        return results
    
    def _process_batch(self, content_batch):
        """Process a batch of content"""
        
        batch_results = []
        
        for content_item in content_batch:
            try:
                # Feature extraction
                features = self._extract_features(content_item)
                
                # Model prediction
                prediction = self.model_ensemble.predict(features)
                
                # Store result
                batch_results.append({
                    'content_id': content_item.id,
                    'risk_score': prediction['probability'],
                    'categories': prediction.get('categories', []),
                    'requires_review': prediction['probability'] > 0.5
                })
                
            except Exception as e:
                logger.error(f"Batch processing error for {content_item.id}: {e}")
                continue
        
        return batch_results
```

This ML pipeline design provides a comprehensive approach to detecting illegal trading activities with multiple safeguards, human oversight, and continuous improvement mechanisms. The system balances automation with human judgment while maintaining high accuracy and minimizing false positives.