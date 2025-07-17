"""
Detection Models for Illegal Trading System

This module implements the core ML models for detecting illegal trading activities
including text classification, image analysis, and behavioral pattern recognition.
"""

import torch
import torch.nn as nn
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.ensemble import IsolationForest
import lightgbm as lgb
import tensorflow as tf
from PIL import Image
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result from illegal trading detection"""
    probability: float
    confidence: float
    category: str
    evidence: Dict[str, Any]
    processing_time_ms: float


@dataclass
class ContentFeatures:
    """Features extracted from content"""
    text_features: Optional[Dict[str, Any]] = None
    image_features: Optional[List[Dict[str, Any]]] = None
    behavioral_features: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class IllegalTradingDetector:
    """Main detector orchestrating multiple specialized models"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config
        self.text_classifier = TextClassifier(model_config.get('text_model'))
        self.image_classifier = ImageClassifier(model_config.get('image_model'))
        self.behavior_analyzer = BehaviorAnalyzer(model_config.get('behavior_model'))
        self.ensemble_model = EnsembleModel(model_config.get('ensemble_model'))
        
        # Illegal content categories
        self.categories = [
            'weapons', 'drugs', 'stolen_goods', 'counterfeit', 
            'human_trafficking', 'wildlife', 'other_illegal'
        ]
        
    def detect(self, content_features: ContentFeatures) -> DetectionResult:
        """Main detection pipeline"""
        start_time = time.time()
        
        try:
            # Individual model predictions
            text_result = None
            if content_features.text_features:
                text_result = self.text_classifier.classify(content_features.text_features)
            
            image_result = None
            if content_features.image_features:
                image_result = self.image_classifier.classify(content_features.image_features)
            
            behavior_result = None
            if content_features.behavioral_features:
                behavior_result = self.behavior_analyzer.analyze(content_features.behavioral_features)
            
            # Ensemble prediction
            ensemble_result = self.ensemble_model.predict(
                text_result, image_result, behavior_result
            )
            
            # Determine final category
            category = self._determine_category(text_result, image_result, ensemble_result)
            
            # Compile evidence
            evidence = self._compile_evidence(text_result, image_result, behavior_result)
            
            processing_time = (time.time() - start_time) * 1000
            
            return DetectionResult(
                probability=ensemble_result['probability'],
                confidence=ensemble_result['confidence'],
                category=category,
                evidence=evidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return DetectionResult(
                probability=0.0,
                confidence=0.0,
                category='error',
                evidence={'error': str(e)},
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    def _determine_category(self, text_result, image_result, ensemble_result):
        """Determine the most likely illegal trading category"""
        category_scores = {}
        
        # Aggregate category scores from different models
        if text_result and 'categories' in text_result:
            for cat, score in text_result['categories'].items():
                category_scores[cat] = category_scores.get(cat, 0) + score * 0.4
        
        if image_result and 'categories' in image_result:
            for cat, score in image_result['categories'].items():
                category_scores[cat] = category_scores.get(cat, 0) + score * 0.6
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'unknown'
    
    def _compile_evidence(self, text_result, image_result, behavior_result):
        """Compile evidence from all detection models"""
        evidence = {}
        
        if text_result:
            evidence['text'] = {
                'suspicious_phrases': text_result.get('suspicious_phrases', []),
                'price_mentions': text_result.get('price_mentions', []),
                'contact_methods': text_result.get('contact_methods', [])
            }
        
        if image_result:
            evidence['images'] = {
                'detected_objects': image_result.get('detected_objects', []),
                'ocr_text': image_result.get('ocr_text', ''),
                'visual_similarity': image_result.get('visual_similarity', [])
            }
        
        if behavior_result:
            evidence['behavior'] = {
                'risk_factors': behavior_result.get('risk_factors', []),
                'anomaly_score': behavior_result.get('anomaly_score', 0.0),
                'network_flags': behavior_result.get('network_flags', [])
            }
        
        return evidence


class TextClassifier:
    """BERT-based text classifier for illegal content detection"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config or {}
        self.model_name = self.config.get('model_name', 'bert-base-multilingual-cased')
        
        # Load pre-trained model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2  # Binary classification
        )
        
        # Load fine-tuned weights if available
        if 'checkpoint_path' in self.config:
            self.model.load_state_dict(torch.load(self.config['checkpoint_path']))
        
        self.model.eval()
        
        # Illegal content patterns
        self.weapon_keywords = [
            'gun', 'rifle', 'pistol', 'firearm', 'ammunition', 'ammo',
            'AK-47', 'AR-15', 'glock', 'bullet', 'rounds', 'tactical'
        ]
        
        self.drug_keywords = [
            'cocaine', 'heroin', 'meth', 'fentanyl', 'mdma', 'lsd',
            'weed', 'cannabis', 'pills', 'oxy', 'adderall', 'xanax'
        ]
        
        self.euphemisms = {
            'white girl': 'cocaine',
            'snow': 'cocaine', 
            'blow': 'cocaine',
            'molly': 'mdma',
            'ice': 'methamphetamine',
            'grass': 'marijuana',
            'trees': 'marijuana'
        }
        
    def classify(self, text_features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify text content for illegal trading"""
        
        text = text_features.get('normalized_text', '')
        if not text:
            return {'probability': 0.0, 'confidence': 0.0}
        
        # Extract explicit indicators
        weapon_matches = self._find_keyword_matches(text, self.weapon_keywords)
        drug_matches = self._find_keyword_matches(text, self.drug_keywords)
        euphemism_matches = self._find_euphemisms(text)
        
        # Price and contact pattern analysis
        price_mentions = self._extract_price_mentions(text)
        contact_methods = self._extract_contact_methods(text)
        suspicious_phrases = self._detect_suspicious_phrases(text)
        
        # BERT classification
        bert_prediction = self._bert_classify(text)
        
        # Combine rule-based and ML predictions
        rule_score = self._calculate_rule_score(
            weapon_matches, drug_matches, euphemism_matches,
            price_mentions, contact_methods, suspicious_phrases
        )
        
        # Weighted combination
        final_probability = (bert_prediction['probability'] * 0.7 + rule_score * 0.3)
        
        # Determine categories
        categories = {}
        if weapon_matches:
            categories['weapons'] = min(1.0, len(weapon_matches) * 0.3)
        if drug_matches or euphemism_matches:
            categories['drugs'] = min(1.0, (len(drug_matches) + len(euphemism_matches)) * 0.3)
        
        return {
            'probability': final_probability,
            'confidence': bert_prediction['confidence'],
            'categories': categories,
            'suspicious_phrases': suspicious_phrases,
            'price_mentions': price_mentions,
            'contact_methods': contact_methods,
            'weapon_keywords': weapon_matches,
            'drug_keywords': drug_matches + euphemism_matches
        }
    
    def _bert_classify(self, text: str) -> Dict[str, float]:
        """Use BERT model for text classification"""
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
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
        
        return {
            'probability': illegal_prob,
            'confidence': confidence
        }
    
    def _find_keyword_matches(self, text: str, keywords: List[str]) -> List[str]:
        """Find keyword matches in text"""
        matches = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword.lower())}\b', text_lower):
                matches.append(keyword)
        
        return matches
    
    def _find_euphemisms(self, text: str) -> List[str]:
        """Find euphemisms and coded language"""
        matches = []
        text_lower = text.lower()
        
        for euphemism, actual in self.euphemisms.items():
            if re.search(rf'\b{re.escape(euphemism)}\b', text_lower):
                matches.append(f"{euphemism} ({actual})")
        
        return matches
    
    def _extract_price_mentions(self, text: str) -> List[Dict[str, Any]]:
        """Extract price mentions from text"""
        price_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00
            r'(\d+)\s*(?:dollars?|bucks?|USD)',  # 100 dollars
            r'(\d+)k\b',  # 5k
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                prices.append({
                    'text': match.group(),
                    'amount': match.group(1),
                    'position': match.span()
                })
        
        return prices
    
    def _extract_contact_methods(self, text: str) -> List[str]:
        """Extract contact methods (phone, email, social media)"""
        contact_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'(?:kik|telegram|whatsapp|snapchat):\s*(\w+)',  # Social apps
            r'DM\s+me',  # Direct message requests
        ]
        
        contacts = []
        for pattern in contact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            contacts.extend(matches)
        
        return contacts
    
    def _detect_suspicious_phrases(self, text: str) -> List[str]:
        """Detect suspicious phrases common in illegal trading"""
        suspicious_patterns = [
            r'\bdiscreet\b',
            r'\bno\s+questions\s+asked\b',
            r'\bcash\s+only\b',
            r'\bfast\s+delivery\b',
            r'\bmeet\s+in\s+person\b',
            r'\buntraceable\b',
            r'\boff\s+the\s+books\b',
            r'\bunder\s+the\s+table\b'
        ]
        
        matches = []
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern.replace(r'\b', '').replace(r'\s+', ' '))
        
        return matches
    
    def _calculate_rule_score(self, weapon_matches, drug_matches, euphemism_matches,
                            price_mentions, contact_methods, suspicious_phrases) -> float:
        """Calculate rule-based score"""
        score = 0.0
        
        # Weight different types of matches
        score += len(weapon_matches) * 0.4
        score += len(drug_matches) * 0.4
        score += len(euphemism_matches) * 0.3
        score += len(suspicious_phrases) * 0.2
        
        # Presence of price + contact methods is suspicious
        if price_mentions and contact_methods:
            score += 0.3
        
        return min(1.0, score)


class ImageClassifier:
    """Computer vision models for detecting illegal items in images"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config or {}
        
        # Load object detection model
        self.object_detector = self._load_object_detector()
        
        # Load specialized classifiers
        self.weapon_classifier = WeaponClassifier()
        self.drug_classifier = DrugParaphernaliaClassifier()
        
        # OCR for text in images
        self.ocr_engine = OCREngine()
        
    def classify(self, image_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify images for illegal content"""
        
        if not image_features:
            return {'probability': 0.0, 'confidence': 0.0}
        
        max_probability = 0.0
        all_detected_objects = []
        all_ocr_text = []
        categories = {}
        
        for image_feature in image_features:
            # Object detection
            objects = self._detect_objects(image_feature['image_data'])
            all_detected_objects.extend(objects)
            
            # OCR text extraction
            ocr_text = self.ocr_engine.extract_text(image_feature['image_data'])
            all_ocr_text.append(ocr_text)
            
            # Specialized classification
            weapon_score = self.weapon_classifier.classify(image_feature['image_data'])
            drug_score = self.drug_classifier.classify(image_feature['image_data'])
            
            # Update category scores
            if weapon_score > 0.5:
                categories['weapons'] = max(categories.get('weapons', 0), weapon_score)
            if drug_score > 0.5:
                categories['drugs'] = max(categories.get('drugs', 0), drug_score)
            
            # Calculate image probability
            image_probability = max(weapon_score, drug_score)
            max_probability = max(max_probability, image_probability)
        
        # Analyze OCR text for illegal content keywords
        combined_ocr_text = ' '.join(all_ocr_text)
        text_classifier = TextClassifier({})
        ocr_result = text_classifier.classify({'normalized_text': combined_ocr_text})
        
        # Combine visual and text evidence
        final_probability = max(max_probability, ocr_result['probability'] * 0.7)
        
        return {
            'probability': final_probability,
            'confidence': max_probability,  # Simplified confidence
            'categories': categories,
            'detected_objects': all_detected_objects,
            'ocr_text': combined_ocr_text,
            'visual_similarity': []  # Placeholder for similarity matching
        }
    
    def _load_object_detector(self):
        """Load YOLO object detection model"""
        # Placeholder - would load actual YOLO model
        return MockObjectDetector()
    
    def _detect_objects(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        return self.object_detector.detect(image_data)


class WeaponClassifier:
    """Specialized classifier for weapons detection"""
    
    def __init__(self):
        # Load pre-trained weapon detection model
        self.model = self._load_weapon_model()
        
    def classify(self, image_data: bytes) -> float:
        """Classify image for weapon content"""
        # Placeholder implementation
        # Would use actual CNN model trained on weapon images
        return 0.0
    
    def _load_weapon_model(self):
        """Load weapon detection model"""
        # Placeholder - would load actual model
        return None


class DrugParaphernaliaClassifier:
    """Specialized classifier for drug paraphernalia"""
    
    def __init__(self):
        self.model = self._load_drug_model()
        
    def classify(self, image_data: bytes) -> float:
        """Classify image for drug paraphernalia"""
        # Placeholder implementation
        return 0.0
    
    def _load_drug_model(self):
        """Load drug paraphernalia detection model"""
        return None


class BehaviorAnalyzer:
    """Analyze user behavior patterns for illegal trading indicators"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config or {}
        
        # Load behavior analysis models
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.risk_classifier = lgb.LGBMClassifier(
            objective='binary',
            metric='auc',
            num_leaves=100,
            learning_rate=0.1
        )
        
        # Load pre-trained models if available
        if 'model_path' in self.config:
            self._load_pretrained_models()
    
    def analyze(self, behavioral_features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user behavioral patterns"""
        
        # Extract feature vector
        feature_vector = self._extract_feature_vector(behavioral_features)
        
        # Anomaly detection
        anomaly_score = self.anomaly_detector.decision_function([feature_vector])[0]
        is_anomaly = self.anomaly_detector.predict([feature_vector])[0] == -1
        
        # Risk classification
        risk_probability = 0.5  # Placeholder - would use actual model
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(behavioral_features)
        
        # Network analysis
        network_flags = self._analyze_network_behavior(behavioral_features)
        
        return {
            'probability': risk_probability,
            'confidence': abs(risk_probability - 0.5) * 2,
            'anomaly_score': anomaly_score,
            'is_anomaly': is_anomaly,
            'risk_factors': risk_factors,
            'network_flags': network_flags
        }
    
    def _extract_feature_vector(self, behavioral_features: Dict[str, Any]) -> List[float]:
        """Extract numerical feature vector from behavioral data"""
        features = []
        
        # Temporal features
        features.append(behavioral_features.get('posting_frequency', 0.0))
        features.append(behavioral_features.get('night_posting_ratio', 0.0))
        features.append(behavioral_features.get('weekend_posting_ratio', 0.0))
        
        # Content features
        features.append(behavioral_features.get('avg_text_length', 0.0))
        features.append(behavioral_features.get('image_posting_ratio', 0.0))
        features.append(behavioral_features.get('private_message_ratio', 0.0))
        
        # Network features
        features.append(behavioral_features.get('new_connections_rate', 0.0))
        features.append(behavioral_features.get('connection_diversity', 0.0))
        
        # Historical features
        features.append(behavioral_features.get('violation_history_score', 0.0))
        features.append(behavioral_features.get('account_age_days', 0.0))
        
        return features
    
    def _identify_risk_factors(self, behavioral_features: Dict[str, Any]) -> List[str]:
        """Identify specific behavioral risk factors"""
        risk_factors = []
        
        # High-frequency posting
        if behavioral_features.get('posting_frequency', 0) > 10:  # >10 posts/day
            risk_factors.append('high_posting_frequency')
        
        # Unusual timing patterns
        if behavioral_features.get('night_posting_ratio', 0) > 0.5:
            risk_factors.append('unusual_posting_hours')
        
        # Rapid account connections
        if behavioral_features.get('new_connections_rate', 0) > 20:  # >20 new connections/day
            risk_factors.append('rapid_network_expansion')
        
        # Short text posts (possible coded communication)
        if behavioral_features.get('avg_text_length', 100) < 20:
            risk_factors.append('suspicious_short_messages')
        
        # High private messaging activity
        if behavioral_features.get('private_message_ratio', 0) > 0.8:
            risk_factors.append('high_private_messaging')
        
        # Violation history
        if behavioral_features.get('violation_history_score', 0) > 0.3:
            risk_factors.append('previous_violations')
        
        return risk_factors
    
    def _analyze_network_behavior(self, behavioral_features: Dict[str, Any]) -> List[str]:
        """Analyze network-level suspicious behavior"""
        flags = []
        
        # Coordinated posting patterns
        if behavioral_features.get('coordinated_posting_score', 0) > 0.7:
            flags.append('coordinated_activity')
        
        # Connections to known violators
        if behavioral_features.get('risky_connections_count', 0) > 3:
            flags.append('risky_network_connections')
        
        # Geographic clustering
        if behavioral_features.get('geographic_clustering_score', 0) > 0.8:
            flags.append('suspicious_geographic_patterns')
        
        return flags
    
    def _load_pretrained_models(self):
        """Load pre-trained behavior analysis models"""
        # Placeholder for loading actual models
        pass


class EnsembleModel:
    """Ensemble model combining text, image, and behavioral predictions"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.config = model_config or {}
        
        # Simple weighted ensemble (can be replaced with meta-learner)
        self.weights = {
            'text': 0.4,
            'image': 0.4, 
            'behavior': 0.2
        }
    
    def predict(self, text_result, image_result, behavior_result) -> Dict[str, Any]:
        """Combine predictions from individual models"""
        
        predictions = []
        confidences = []
        
        # Collect predictions and confidences
        if text_result:
            predictions.append(text_result['probability'])
            confidences.append(text_result['confidence'])
        
        if image_result:
            predictions.append(image_result['probability'])
            confidences.append(image_result['confidence'])
        
        if behavior_result:
            predictions.append(behavior_result['probability'])
            confidences.append(behavior_result['confidence'])
        
        if not predictions:
            return {'probability': 0.0, 'confidence': 0.0}
        
        # Weighted average based on confidence
        if len(predictions) == 3:
            # All three models available
            weighted_prob = (
                text_result['probability'] * self.weights['text'] +
                image_result['probability'] * self.weights['image'] +
                behavior_result['probability'] * self.weights['behavior']
            )
        else:
            # Some models missing - simple average
            weighted_prob = np.mean(predictions)
        
        # Combined confidence
        combined_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            'probability': weighted_prob,
            'confidence': combined_confidence
        }


# Mock classes for placeholder functionality
class MockObjectDetector:
    """Mock object detector for testing"""
    
    def detect(self, image_data: bytes) -> List[Dict[str, Any]]:
        return []


class OCREngine:
    """OCR engine for extracting text from images"""
    
    def extract_text(self, image_data: bytes) -> str:
        """Extract text from image using OCR"""
        # Placeholder - would use actual OCR like Tesseract
        return ""


# Example usage
def example_usage():
    """Example usage of the illegal trading detector"""
    
    # Initialize detector
    config = {
        'text_model': {'model_name': 'bert-base-multilingual-cased'},
        'image_model': {},
        'behavior_model': {},
        'ensemble_model': {}
    }
    
    detector = IllegalTradingDetector(config)
    
    # Example content features
    content_features = ContentFeatures(
        text_features={
            'normalized_text': 'Selling AK-47 rifle, cash only, discreet transaction'
        },
        image_features=[
            {'image_data': b'fake_image_data'}
        ],
        behavioral_features={
            'posting_frequency': 15.0,
            'night_posting_ratio': 0.8,
            'violation_history_score': 0.6
        }
    )
    
    # Detect illegal trading
    result = detector.detect(content_features)
    
    print(f"Detection Result:")
    print(f"  Probability: {result.probability:.3f}")
    print(f"  Confidence: {result.confidence:.3f}")
    print(f"  Category: {result.category}")
    print(f"  Processing Time: {result.processing_time_ms:.1f}ms")
    print(f"  Evidence: {result.evidence}")


if __name__ == "__main__":
    example_usage()