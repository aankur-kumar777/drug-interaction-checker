"""
Machine Learning Predictor for Drug Interactions
Uses trained models to predict interaction severity and risks
"""
import os
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class InteractionPredictor:
    """
    ML-based interaction predictor
    Uses ensemble of models to predict drug interaction severity
    """
    
    def __init__(self):
        """Initialize predictor with pre-trained models"""
        self.models_loaded = False
        self.feature_extractor = DrugFeatureExtractor()
        
        try:
            self._load_models()
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}")
            logger.info("Using rule-based predictions only")
    
    def _load_models(self):
        """Load pre-trained models"""
        # In production, load actual trained models
        # For demo, we'll use a simulated model
        logger.info("Initializing ML models...")
        
        # Placeholder for actual model loading
        # self.severity_classifier = joblib.load('models/trained/severity_model.pkl')
        # self.risk_regressor = joblib.load('models/trained/risk_model.pkl')
        
        self.models_loaded = True
        logger.info("ML models initialized (demo mode)")
    
    def predict_interaction(self, drug1: str, drug2: str) -> Dict:
        """
        Predict interaction between two drugs
        
        Args:
            drug1: First drug name
            drug2: Second drug name
        
        Returns:
            Dictionary with prediction results
        """
        # Extract features
        features = self.feature_extractor.extract_pair_features(drug1, drug2)
        
        if not features:
            return {
                'severity': 'unknown',
                'confidence': 0.0,
                'risk_score': 0.0
            }
        
        # Make prediction (simulated for demo)
        severity, confidence = self._predict_severity(features)
        risk_score = self._predict_risk_score(features)
        
        return {
            'severity': severity,
            'confidence': float(confidence),
            'risk_score': float(risk_score),
            'features_used': len(features),
            'model_version': '1.0.0'
        }
    
    def _predict_severity(self, features: Dict) -> Tuple[str, float]:
        """Predict interaction severity"""
        # Simulated prediction based on feature patterns
        # In production, this would use actual trained model
        
        # Simple rule-based simulation
        if features.get('same_metabolic_pathway', False):
            if features.get('similar_mechanism', False):
                return 'major', 0.85
            return 'moderate', 0.72
        
        if features.get('opposite_effects', False):
            return 'moderate', 0.68
        
        return 'minor', 0.45
    
    def _predict_risk_score(self, features: Dict) -> float:
        """Predict numerical risk score (0-1)"""
        # Simulated risk score calculation
        score = 0.0
        
        if features.get('same_metabolic_pathway', False):
            score += 0.3
        
        if features.get('similar_mechanism', False):
            score += 0.3
        
        if features.get('both_high_protein_binding', False):
            score += 0.2
        
        if features.get('opposite_effects', False):
            score += 0.2
        
        return min(score, 1.0)
    
    def batch_predict(self, drug_pairs: List[Tuple[str, str]]) -> List[Dict]:
        """Predict interactions for multiple drug pairs"""
        predictions = []
        
        for drug1, drug2 in drug_pairs:
            prediction = self.predict_interaction(drug1, drug2)
            prediction['pair'] = (drug1, drug2)
            predictions.append(prediction)
        
        return predictions
    
    def explain_prediction(self, drug1: str, drug2: str) -> Dict:
        """
        Provide explanation for prediction
        
        Returns:
            Explanation of features that influenced prediction
        """
        features = self.feature_extractor.extract_pair_features(drug1, drug2)
        prediction = self.predict_interaction(drug1, drug2)
        
        # Identify influential features
        influential_features = []
        
        if features.get('same_metabolic_pathway'):
            influential_features.append({
                'feature': 'same_metabolic_pathway',
                'influence': 'high',
                'description': 'Both drugs are metabolized by the same enzyme pathway'
            })
        
        if features.get('similar_mechanism'):
            influential_features.append({
                'feature': 'similar_mechanism',
                'influence': 'high',
                'description': 'Drugs have similar mechanisms of action'
            })
        
        return {
            'prediction': prediction,
            'influential_features': influential_features,
            'feature_count': len(features),
            'model_confidence': prediction.get('confidence', 0)
        }


class DrugFeatureExtractor:
    """Extract features from drugs for ML models"""
    
    def __init__(self):
        """Initialize feature extractor"""
        self.drug_properties = self._load_drug_properties()
    
    def _load_drug_properties(self) -> Dict:
        """Load drug properties database"""
        # Simulated drug properties for demo
        return {
            'warfarin': {
                'metabolic_pathway': 'CYP2C9',
                'mechanism': 'vitamin_k_antagonist',
                'protein_binding': 'high',
                'half_life': 40,
                'therapeutic_class': 'anticoagulant'
            },
            'aspirin': {
                'metabolic_pathway': 'hydrolysis',
                'mechanism': 'cox_inhibitor',
                'protein_binding': 'high',
                'half_life': 0.5,
                'therapeutic_class': 'antiplatelet'
            },
            'ibuprofen': {
                'metabolic_pathway': 'CYP2C9',
                'mechanism': 'cox_inhibitor',
                'protein_binding': 'high',
                'half_life': 2,
                'therapeutic_class': 'nsaid'
            },
            'lisinopril': {
                'metabolic_pathway': 'minimal',
                'mechanism': 'ace_inhibitor',
                'protein_binding': 'low',
                'half_life': 12,
                'therapeutic_class': 'antihypertensive'
            },
            'metformin': {
                'metabolic_pathway': 'minimal',
                'mechanism': 'biguanide',
                'protein_binding': 'negligible',
                'half_life': 6.5,
                'therapeutic_class': 'antidiabetic'
            }
        }
    
    def extract_pair_features(self, drug1: str, drug2: str) -> Dict:
        """Extract features for a drug pair"""
        drug1 = drug1.lower()
        drug2 = drug2.lower()
        
        props1 = self.drug_properties.get(drug1, {})
        props2 = self.drug_properties.get(drug2, {})
        
        if not props1 or not props2:
            return {}
        
        features = {
            # Metabolic pathway features
            'same_metabolic_pathway': props1.get('metabolic_pathway') == props2.get('metabolic_pathway'),
            'metabolic_pathway_overlap': self._check_pathway_overlap(props1, props2),
            
            # Mechanism features
            'similar_mechanism': props1.get('mechanism') == props2.get('mechanism'),
            'opposite_effects': self._check_opposite_effects(props1, props2),
            
            # Pharmacokinetic features
            'both_high_protein_binding': (
                props1.get('protein_binding') == 'high' and 
                props2.get('protein_binding') == 'high'
            ),
            'half_life_ratio': self._calculate_half_life_ratio(props1, props2),
            
            # Therapeutic class features
            'same_therapeutic_class': props1.get('therapeutic_class') == props2.get('therapeutic_class'),
            'related_classes': self._check_related_classes(props1, props2)
        }
        
        return features
    
    def _check_pathway_overlap(self, props1: Dict, props2: Dict) -> bool:
        """Check if drugs have overlapping metabolic pathways"""
        pathway1 = props1.get('metabolic_pathway', '')
        pathway2 = props2.get('metabolic_pathway', '')
        
        # Check for CYP450 overlap
        if 'CYP' in pathway1 and 'CYP' in pathway2:
            return True
        
        return False
    
    def _check_opposite_effects(self, props1: Dict, props2: Dict) -> bool:
        """Check if drugs have opposite pharmacological effects"""
        # Simplified check - in production, use comprehensive database
        opposite_pairs = [
            ('anticoagulant', 'procoagulant'),
            ('antihypertensive', 'vasoconstrictor'),
        ]
        
        class1 = props1.get('therapeutic_class', '')
        class2 = props2.get('therapeutic_class', '')
        
        for pair in opposite_pairs:
            if (class1 in pair and class2 in pair) and class1 != class2:
                return True
        
        return False
    
    def _calculate_half_life_ratio(self, props1: Dict, props2: Dict) -> float:
        """Calculate ratio of half-lives"""
        hl1 = props1.get('half_life', 1)
        hl2 = props2.get('half_life', 1)
        
        if hl1 == 0 or hl2 == 0:
            return 1.0
        
        ratio = max(hl1, hl2) / min(hl1, hl2)
        return float(ratio)
    
    def _check_related_classes(self, props1: Dict, props2: Dict) -> bool:
        """Check if therapeutic classes are related"""
        related_groups = [
            {'anticoagulant', 'antiplatelet', 'nsaid'},
            {'antihypertensive', 'diuretic', 'ace_inhibitor'},
        ]
        
        class1 = props1.get('therapeutic_class', '')
        class2 = props2.get('therapeutic_class', '')
        
        for group in related_groups:
            if class1 in group and class2 in group:
                return True
        
        return False


class ModelTrainer:
    """Train ML models for interaction prediction"""
    
    def __init__(self):
        """Initialize trainer"""
        self.feature_extractor = DrugFeatureExtractor()
    
    def prepare_training_data(self, interactions_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from interaction database
        
        Args:
            interactions_data: List of interaction records
        
        Returns:
            X (features), y (labels)
        """
        X = []
        y = []
        
        for interaction in interactions_data:
            drug1 = interaction['drug1']
            drug2 = interaction['drug2']
            
            features = self.feature_extractor.extract_pair_features(drug1, drug2)
            if features:
                feature_vector = self._features_to_vector(features)
                X.append(feature_vector)
                y.append(self._severity_to_numeric(interaction['severity']))
        
        return np.array(X), np.array(y)
    
    def _features_to_vector(self, features: Dict) -> List[float]:
        """Convert feature dict to numerical vector"""
        return [
            float(features.get('same_metabolic_pathway', False)),
            float(features.get('metabolic_pathway_overlap', False)),
            float(features.get('similar_mechanism', False)),
            float(features.get('opposite_effects', False)),
            float(features.get('both_high_protein_binding', False)),
            features.get('half_life_ratio', 1.0),
            float(features.get('same_therapeutic_class', False)),
            float(features.get('related_classes', False))
        ]
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Convert severity label to numeric value"""
        severity_map = {
            'minor': 0,
            'moderate': 1,
            'major': 2,
            'contraindicated': 3
        }
        return severity_map.get(severity.lower(), 0)
    
    def train_models(self, X: np.ndarray, y: np.ndarray):
        """
        Train ML models
        
        In production, this would train actual sklearn/xgboost models
        """
        logger.info(f"Training on {len(X)} samples...")
        
        # Placeholder for actual model training
        # from sklearn.ensemble import RandomForestClassifier
        # model = RandomForestClassifier(n_estimators=100)
        # model.fit(X, y)
        # joblib.dump(model, 'models/trained/severity_model.pkl')
        
        logger.info("Model training complete (demo mode)")
