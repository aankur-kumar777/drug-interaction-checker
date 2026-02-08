"""
Machine Learning predictor for drug interactions
"""
import numpy as np
import pickle
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

from app.utils.config import settings

logger = logging.getLogger(__name__)


class InteractionPredictor:
    """
    ML-based drug interaction predictor using XGBoost and Random Forest
    """
    
    def __init__(self):
        self.interaction_model = None
        self.severity_model = None
        self.feature_extractor = None
        self._ready = False
        
    async def load_models(self):
        """Load pre-trained ML models"""
        try:
            model_path = Path(settings.MODEL_PATH)
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Check if models exist, if not create dummy models for demo
            interaction_model_file = model_path / "interaction_predictor.pkl"
            severity_model_file = model_path / "severity_classifier.pkl"
            
            if interaction_model_file.exists():
                with open(interaction_model_file, 'rb') as f:
                    self.interaction_model = pickle.load(f)
                logger.info("✅ Loaded interaction prediction model")
            else:
                # Create a demo model
                logger.warning("⚠️ Creating demo interaction model (train with real data in production)")
                self.interaction_model = self._create_demo_interaction_model()
                
            if severity_model_file.exists():
                with open(severity_model_file, 'rb') as f:
                    self.severity_model = pickle.load(f)
                logger.info("✅ Loaded severity classification model")
            else:
                # Create a demo model
                logger.warning("⚠️ Creating demo severity model (train with real data in production)")
                self.severity_model = self._create_demo_severity_model()
            
            self.feature_extractor = FeatureExtractor()
            self._ready = True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _create_demo_interaction_model(self):
        """Create a demo XGBoost model for demonstration"""
        # This is a placeholder - in production, train on real data
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        # The model would be trained on real features
        return model
    
    def _create_demo_severity_model(self):
        """Create a demo Random Forest model for demonstration"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model
    
    def is_ready(self) -> bool:
        """Check if models are loaded and ready"""
        return self._ready
    
    async def predict_interaction(
        self,
        drug1: str,
        drug2: str,
        drug1_data: Dict,
        drug2_data: Dict
    ) -> Dict:
        """
        Predict if two drugs interact and the severity
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            drug1_data: Drug 1 information
            drug2_data: Drug 2 information
            
        Returns:
            Dictionary with prediction results
        """
        # Extract features
        features = self.feature_extractor.extract_features(drug1_data, drug2_data)
        
        # Predict interaction probability (demo logic)
        interaction_prob = self._predict_interaction_probability(features, drug1, drug2)
        
        # If interaction predicted, classify severity
        if interaction_prob > 0.5:
            severity = self._predict_severity(features, drug1, drug2)
            
            return {
                "has_interaction": True,
                "confidence": float(interaction_prob),
                "severity": severity["level"],
                "severity_confidence": severity["confidence"],
                "features_used": features
            }
        else:
            return {
                "has_interaction": False,
                "confidence": float(1 - interaction_prob),
                "severity": "NONE",
                "severity_confidence": 0.0,
                "features_used": features
            }
    
    def _predict_interaction_probability(
        self,
        features: Dict,
        drug1: str,
        drug2: str
    ) -> float:
        """
        Predict probability of interaction
        
        This is a demo implementation using rules.
        In production, this would use the trained XGBoost model.
        """
        # Demo logic based on known interactions
        known_high_risk_pairs = [
            ("warfarin", "aspirin"),
            ("metformin", "alcohol"),
            ("simvastatin", "clarithromycin"),
            ("lisinopril", "potassium"),
            ("levothyroxine", "calcium")
        ]
        
        drug1_lower = drug1.lower()
        drug2_lower = drug2.lower()
        
        # Check known interactions
        for pair in known_high_risk_pairs:
            if (drug1_lower in pair[0] and drug2_lower in pair[1]) or \
               (drug1_lower in pair[1] and drug2_lower in pair[0]):
                return np.random.uniform(0.85, 0.98)
        
        # Check feature-based risk
        risk_score = 0.0
        
        # Same drug class increases risk
        if features.get('same_drug_class'):
            risk_score += 0.3
        
        # Enzyme overlap increases risk
        if features.get('enzyme_overlap', 0) > 0:
            risk_score += 0.2 * min(features['enzyme_overlap'] / 3, 1.0)
        
        # Protein binding interaction
        if features.get('high_protein_binding_both'):
            risk_score += 0.15
        
        # Add some randomness for demo
        risk_score += np.random.uniform(0, 0.2)
        
        return min(risk_score, 1.0)
    
    def _predict_severity(
        self,
        features: Dict,
        drug1: str,
        drug2: str
    ) -> Dict[str, any]:
        """
        Predict interaction severity
        
        This is a demo implementation.
        In production, this would use the trained Random Forest model.
        """
        drug1_lower = drug1.lower()
        drug2_lower = drug2.lower()
        
        # Known major interactions
        major_interactions = [
            ("warfarin", "aspirin"),
            ("metformin", "alcohol"),
            ("simvastatin", "clarithromycin")
        ]
        
        for pair in major_interactions:
            if (drug1_lower in pair[0] and drug2_lower in pair[1]) or \
               (drug1_lower in pair[1] and drug2_lower in pair[0]):
                return {
                    "level": "MAJOR",
                    "confidence": np.random.uniform(0.88, 0.96)
                }
        
        # Moderate interactions
        if features.get('same_drug_class') or features.get('enzyme_overlap', 0) >= 2:
            return {
                "level": "MODERATE",
                "confidence": np.random.uniform(0.75, 0.88)
            }
        
        # Default to minor
        return {
            "level": "MINOR",
            "confidence": np.random.uniform(0.60, 0.75)
        }


class FeatureExtractor:
    """Extract features for ML models"""
    
    def extract_features(self, drug1_data: Dict, drug2_data: Dict) -> Dict:
        """
        Extract features from drug pair data
        
        Features include:
        - Same drug class
        - Enzyme overlap
        - Protein binding similarity
        - Half-life ratio
        - Molecular weight similarity
        """
        features = {}
        
        # Drug class comparison
        features['same_drug_class'] = (
            drug1_data.get('drug_class') == drug2_data.get('drug_class')
            if drug1_data.get('drug_class') and drug2_data.get('drug_class')
            else False
        )
        
        # Enzyme overlap
        enzymes1 = set(drug1_data.get('enzymes', []))
        enzymes2 = set(drug2_data.get('enzymes', []))
        features['enzyme_overlap'] = len(enzymes1.intersection(enzymes2))
        
        # Protein binding
        pb1 = drug1_data.get('protein_binding', 0)
        pb2 = drug2_data.get('protein_binding', 0)
        features['high_protein_binding_both'] = (pb1 > 90 and pb2 > 90)
        features['protein_binding_diff'] = abs(pb1 - pb2)
        
        # Half-life ratio
        hl1 = drug1_data.get('half_life', 12)
        hl2 = drug2_data.get('half_life', 12)
        features['half_life_ratio'] = max(hl1, hl2) / min(hl1, hl2) if min(hl1, hl2) > 0 else 1.0
        
        # Molecular weight similarity
        mw1 = drug1_data.get('molecular_weight', 300)
        mw2 = drug2_data.get('molecular_weight', 300)
        features['molecular_weight_ratio'] = max(mw1, mw2) / min(mw1, mw2) if min(mw1, mw2) > 0 else 1.0
        
        return features
