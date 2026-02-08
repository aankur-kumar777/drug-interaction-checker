"""
Explainable AI module using SHAP for model interpretability
"""
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class InteractionExplainer:
    """
    Provides explanations for ML predictions using SHAP-like methodology
    """
    
    def __init__(self):
        self.feature_importance = {
            'enzyme_overlap': 0.31,
            'same_drug_class': 0.28,
            'protein_binding_both': 0.22,
            'half_life_ratio': 0.12,
            'molecular_weight_ratio': 0.07
        }
    
    def explain_interaction(
        self,
        drug1: str,
        drug2: str,
        features: Dict,
        prediction: Dict
    ) -> Dict:
        """
        Generate explanation for an interaction prediction
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            features: Extracted features
            prediction: Model prediction
            
        Returns:
            Explanation dictionary with feature contributions
        """
        explanation = {
            "key_factors": [],
            "risk_contributors": {
                "pharmacodynamic": 0.0,
                "pharmacokinetic": 0.0
            },
            "pathway_description": ""
        }
        
        # Calculate feature contributions
        total_contribution = 0.0
        
        # Enzyme overlap (pharmacokinetic)
        if features.get('enzyme_overlap', 0) > 0:
            contribution = self.feature_importance['enzyme_overlap'] * min(features['enzyme_overlap'] / 3, 1.0)
            explanation['key_factors'].append({
                "feature": f"Enzyme overlap ({features['enzyme_overlap']} shared enzymes)",
                "weight": round(contribution, 3)
            })
            explanation['risk_contributors']['pharmacokinetic'] += contribution
            total_contribution += contribution
        
        # Same drug class (pharmacodynamic)
        if features.get('same_drug_class'):
            contribution = self.feature_importance['same_drug_class']
            explanation['key_factors'].append({
                "feature": "Same drug class (additive effects)",
                "weight": round(contribution, 3)
            })
            explanation['risk_contributors']['pharmacodynamic'] += contribution
            total_contribution += contribution
        
        # High protein binding (pharmacokinetic)
        if features.get('high_protein_binding_both'):
            contribution = self.feature_importance['protein_binding_both']
            explanation['key_factors'].append({
                "feature": "High protein binding (>90% both drugs)",
                "weight": round(contribution, 3)
            })
            explanation['risk_contributors']['pharmacokinetic'] += contribution
            total_contribution += contribution
        
        # Half-life considerations (pharmacokinetic)
        if features.get('half_life_ratio', 1.0) > 2.0:
            contribution = self.feature_importance['half_life_ratio'] * min((features['half_life_ratio'] - 1) / 4, 1.0)
            explanation['key_factors'].append({
                "feature": f"Half-life disparity (ratio: {features['half_life_ratio']:.1f})",
                "weight": round(contribution, 3)
            })
            explanation['risk_contributors']['pharmacokinetic'] += contribution
            total_contribution += contribution
        
        # Normalize risk contributors
        if total_contribution > 0:
            explanation['risk_contributors']['pharmacodynamic'] /= total_contribution
            explanation['risk_contributors']['pharmacokinetic'] /= total_contribution
        
        # Generate pathway description
        explanation['pathway_description'] = self._generate_pathway_description(
            drug1, drug2, features, prediction
        )
        
        # Sort key factors by weight
        explanation['key_factors'] = sorted(
            explanation['key_factors'],
            key=lambda x: x['weight'],
            reverse=True
        )
        
        return explanation
    
    def _generate_pathway_description(
        self,
        drug1: str,
        drug2: str,
        features: Dict,
        prediction: Dict
    ) -> str:
        """Generate human-readable pathway description"""
        pathways = []
        
        if features.get('enzyme_overlap', 0) > 0:
            pathways.append(
                f"{drug1} and {drug2} are both metabolized by shared enzymes, "
                f"potentially leading to competitive inhibition"
            )
        
        if features.get('same_drug_class'):
            pathways.append(
                f"Both medications belong to the same therapeutic class, "
                f"which may result in additive pharmacological effects"
            )
        
        if features.get('high_protein_binding_both'):
            pathways.append(
                f"Both drugs have high protein binding (>90%), which can lead to "
                f"displacement interactions and increased free drug concentrations"
            )
        
        if not pathways:
            pathways.append(
                f"The interaction between {drug1} and {drug2} may occur through "
                f"multiple pharmacological pathways"
            )
        
        return ". ".join(pathways) + "."
    
    def get_confidence_breakdown(self, prediction: Dict) -> Dict[str, float]:
        """
        Break down confidence score into components
        
        Returns:
            Dictionary with confidence components
        """
        return {
            "model_certainty": prediction.get('confidence', 0.0),
            "evidence_strength": np.random.uniform(0.7, 0.95),  # Demo value
            "clinical_validation": np.random.uniform(0.6, 0.9),  # Demo value
        }
    
    def generate_shap_values(self, features: Dict) -> List[Tuple[str, float]]:
        """
        Generate SHAP-like values for feature contributions
        
        This is a simplified version. In production, use actual SHAP library.
        """
        shap_values = []
        
        for feature_name, importance in self.feature_importance.items():
            if feature_name in features:
                feature_value = features[feature_name]
                
                # Calculate contribution based on feature value and importance
                if isinstance(feature_value, bool):
                    contribution = importance if feature_value else 0
                else:
                    # Normalize numeric features
                    normalized_value = min(float(feature_value), 1.0)
                    contribution = importance * normalized_value
                
                shap_values.append((feature_name, contribution))
        
        return sorted(shap_values, key=lambda x: abs(x[1]), reverse=True)
