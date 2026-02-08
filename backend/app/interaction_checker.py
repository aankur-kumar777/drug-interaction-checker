"""
Core Drug Interaction Checker
Analyzes drug combinations and provides safety recommendations
"""
import json
import os
from itertools import combinations
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class InteractionChecker:
    """Main class for drug interaction analysis"""
    
    def __init__(self):
        """Initialize the interaction checker with drug and interaction databases"""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.drugs_db = self._load_drugs_database()
        self.interactions_db = self._load_interactions_database()
        
        # Load ML predictor if available
        try:
            from models.predictor import InteractionPredictor
            self.ml_predictor = InteractionPredictor()
            logger.info("ML predictor loaded successfully")
        except Exception as e:
            logger.warning(f"ML predictor not available: {e}")
            self.ml_predictor = None
    
    def _load_drugs_database(self) -> Dict:
        """Load drug information database"""
        try:
            db_path = os.path.join(self.data_dir, 'drugs.json')
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("Drug database not found, using default data")
                return self._get_default_drugs()
        except Exception as e:
            logger.error(f"Error loading drug database: {e}")
            return self._get_default_drugs()
    
    def _load_interactions_database(self) -> Dict:
        """Load drug interactions database"""
        try:
            db_path = os.path.join(self.data_dir, 'interactions.json')
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("Interactions database not found, using default data")
                return self._get_default_interactions()
        except Exception as e:
            logger.error(f"Error loading interactions database: {e}")
            return self._get_default_interactions()
    
    def check_interactions(self, drugs: List[str], patient_factors: Optional[Dict] = None) -> Dict:
        """
        Check interactions between multiple drugs
        
        Args:
            drugs: List of drug names
            patient_factors: Optional patient information (age, conditions, etc.)
        
        Returns:
            Dictionary containing interaction analysis
        """
        # Normalize drug names
        drugs = [drug.lower().strip() for drug in drugs]
        
        # Validate all drugs exist
        unknown_drugs = [d for d in drugs if d not in self.drugs_db]
        if unknown_drugs:
            return {
                'error': f'Unknown drugs: {", ".join(unknown_drugs)}',
                'suggestions': self._find_similar_drugs(unknown_drugs[0])
            }
        
        # Find all interactions
        interactions = []
        drug_pairs = list(combinations(drugs, 2))
        
        for drug1, drug2 in drug_pairs:
            interaction = self._get_interaction(drug1, drug2)
            if interaction:
                # Enhance with ML prediction if available
                if self.ml_predictor:
                    ml_prediction = self.ml_predictor.predict_interaction(drug1, drug2)
                    interaction['ml_confidence'] = ml_prediction.get('confidence', 0)
                    interaction['predicted_severity'] = ml_prediction.get('severity', 'unknown')
                
                interactions.append(interaction)
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(interactions)
        
        # Get recommendations
        recommendations = self._generate_recommendations(drugs, interactions, patient_factors)
        
        # Find safer alternatives
        alternatives = self._find_safer_alternatives(drugs, interactions)
        
        return {
            'drug_count': len(drugs),
            'drugs': drugs,
            'interactions_found': len(interactions),
            'interactions': interactions,
            'overall_risk': overall_risk,
            'recommendations': recommendations,
            'safer_alternatives': alternatives,
            'patient_considerations': self._check_patient_factors(drugs, patient_factors)
        }
    
    def _get_interaction(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Get interaction between two drugs"""
        # Create a consistent key (alphabetically sorted)
        key = tuple(sorted([drug1, drug2]))
        
        if key in self.interactions_db:
            interaction = self.interactions_db[key].copy()
            interaction['drug_pair'] = [drug1, drug2]
            interaction['explanation'] = self._generate_explanation(drug1, drug2, interaction)
            return interaction
        
        return None
    
    def _generate_explanation(self, drug1: str, drug2: str, interaction: Dict) -> str:
        """Generate human-readable explanation of interaction"""
        severity = interaction.get('severity', 'unknown')
        mechanism = interaction.get('mechanism', 'unknown mechanism')
        
        drug1_info = self.drugs_db.get(drug1, {})
        drug2_info = self.drugs_db.get(drug2, {})
        
        explanation = f"{drug1.title()} and {drug2.title()} have a {severity} interaction. "
        explanation += f"Mechanism: {mechanism}. "
        
        if 'clinical_effects' in interaction:
            explanation += f"Clinical effects: {interaction['clinical_effects']}."
        
        return explanation
    
    def _calculate_overall_risk(self, interactions: List[Dict]) -> str:
        """Calculate overall risk level from all interactions"""
        if not interactions:
            return 'low'
        
        severity_scores = {
            'contraindicated': 4,
            'major': 3,
            'moderate': 2,
            'minor': 1
        }
        
        max_severity = max(
            severity_scores.get(i.get('severity', 'minor'), 1)
            for i in interactions
        )
        
        if max_severity >= 4:
            return 'critical'
        elif max_severity >= 3:
            return 'high'
        elif max_severity >= 2:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_recommendations(self, drugs: List[str], interactions: List[Dict], 
                                  patient_factors: Optional[Dict]) -> List[str]:
        """Generate clinical recommendations based on interactions"""
        recommendations = []
        
        for interaction in interactions:
            severity = interaction.get('severity')
            
            if severity == 'contraindicated':
                recommendations.append(
                    f"❌ Avoid combining {' and '.join(interaction['drug_pair'])} - contraindicated"
                )
            elif severity == 'major':
                recommendations.append(
                    f"⚠️ {' and '.join(interaction['drug_pair'])}: Requires close monitoring and possible dose adjustment"
                )
            elif severity == 'moderate':
                recommendations.append(
                    f"⚡ {' and '.join(interaction['drug_pair'])}: Monitor for {interaction.get('clinical_effects', 'adverse effects')}"
                )
            
            # Add specific clinical recommendations
            if 'recommendations' in interaction:
                for rec in interaction['recommendations']:
                    if rec not in recommendations:
                        recommendations.append(f"💡 {rec}")
        
        # Add patient-specific recommendations
        if patient_factors:
            age = patient_factors.get('age')
            if age and age >= 65:
                recommendations.append("👴 Elderly patient: Consider reduced doses and increased monitoring")
        
        if not recommendations:
            recommendations.append("✅ No significant interactions detected. Continue current regimen.")
        
        return recommendations
    
    def _find_safer_alternatives(self, drugs: List[str], interactions: List[Dict]) -> List[Dict]:
        """Find safer alternative drugs"""
        alternatives = []
        
        # Identify problematic drugs (those with major/contraindicated interactions)
        problematic_drugs = set()
        for interaction in interactions:
            if interaction.get('severity') in ['major', 'contraindicated']:
                problematic_drugs.update(interaction['drug_pair'])
        
        # Find alternatives for problematic drugs
        for drug in problematic_drugs:
            drug_info = self.drugs_db.get(drug, {})
            drug_class = drug_info.get('class')
            
            if drug_class:
                # Find drugs in same class
                alternatives_for_drug = []
                for alt_name, alt_info in self.drugs_db.items():
                    if (alt_info.get('class') == drug_class and 
                        alt_name != drug and 
                        alt_name not in drugs):
                        
                        # Check if alternative has fewer interactions
                        has_interactions = False
                        for other_drug in drugs:
                            if other_drug != drug:
                                if self._get_interaction(alt_name, other_drug):
                                    has_interactions = True
                                    break
                        
                        if not has_interactions:
                            alternatives_for_drug.append({
                                'name': alt_name,
                                'reason': f'Same therapeutic class as {drug}, fewer interactions'
                            })
                
                if alternatives_for_drug:
                    alternatives.append({
                        'replace': drug,
                        'with': alternatives_for_drug[:3]  # Top 3 alternatives
                    })
        
        return alternatives
    
    def _check_patient_factors(self, drugs: List[str], patient_factors: Optional[Dict]) -> List[str]:
        """Check for patient-specific considerations"""
        if not patient_factors:
            return []
        
        considerations = []
        
        # Check age
        age = patient_factors.get('age')
        if age:
            for drug in drugs:
                drug_info = self.drugs_db.get(drug, {})
                if age >= 65 and drug_info.get('elderly_caution'):
                    considerations.append(
                        f"{drug.title()}: Use with caution in elderly patients"
                    )
                if age < 18 and drug_info.get('pediatric_caution'):
                    considerations.append(
                        f"{drug.title()}: Pediatric dosing required"
                    )
        
        # Check conditions
        conditions = patient_factors.get('conditions', [])
        for condition in conditions:
            for drug in drugs:
                drug_info = self.drugs_db.get(drug, {})
                contraindications = drug_info.get('contraindications', [])
                if condition.lower() in [c.lower() for c in contraindications]:
                    considerations.append(
                        f"{drug.title()}: Contraindicated in {condition}"
                    )
        
        return considerations
    
    def get_drug_info(self, drug_name: str) -> Optional[Dict]:
        """Get detailed information about a drug"""
        drug_name = drug_name.lower().strip()
        return self.drugs_db.get(drug_name)
    
    def get_alternatives(self, drug_name: str, context_drugs: List[str] = None) -> List[Dict]:
        """Get alternative medications for a drug"""
        drug_name = drug_name.lower().strip()
        drug_info = self.drugs_db.get(drug_name)
        
        if not drug_info:
            return []
        
        drug_class = drug_info.get('class')
        alternatives = []
        
        for alt_name, alt_info in self.drugs_db.items():
            if alt_name != drug_name and alt_info.get('class') == drug_class:
                alt_data = {
                    'name': alt_name,
                    'class': drug_class,
                    'description': alt_info.get('description', '')
                }
                
                # Check interactions with context drugs
                if context_drugs:
                    interactions_count = sum(
                        1 for ctx_drug in context_drugs
                        if self._get_interaction(alt_name, ctx_drug.lower())
                    )
                    alt_data['interaction_count'] = interactions_count
                
                alternatives.append(alt_data)
        
        # Sort by fewest interactions
        if context_drugs:
            alternatives.sort(key=lambda x: x.get('interaction_count', 0))
        
        return alternatives[:10]
    
    def search_drugs(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for drugs by name"""
        query = query.lower()
        results = []
        
        for drug_name, drug_info in self.drugs_db.items():
            if query in drug_name:
                results.append({
                    'name': drug_name,
                    'class': drug_info.get('class', 'Unknown'),
                    'description': drug_info.get('description', '')
                })
        
        return results[:limit]
    
    def get_interaction_severity(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Get severity information for two drugs"""
        drug1 = drug1.lower().strip()
        drug2 = drug2.lower().strip()
        
        interaction = self._get_interaction(drug1, drug2)
        
        if not interaction:
            return None
        
        return {
            'interaction': True,
            'drug1': drug1,
            'drug2': drug2,
            'severity': interaction.get('severity'),
            'description': interaction.get('description'),
            'mechanism': interaction.get('mechanism'),
            'clinical_effects': interaction.get('clinical_effects'),
            'recommendations': interaction.get('recommendations', []),
            'references': interaction.get('references', [])
        }
    
    def _find_similar_drugs(self, drug_name: str, limit: int = 5) -> List[str]:
        """Find similar drug names (for typo suggestions)"""
        from difflib import get_close_matches
        return get_close_matches(drug_name, self.drugs_db.keys(), n=limit, cutoff=0.6)
    
    def _get_default_drugs(self) -> Dict:
        """Return default drug database for demo purposes"""
        return {
            'warfarin': {
                'class': 'anticoagulant',
                'description': 'Anticoagulant used to prevent blood clots',
                'mechanism': 'Vitamin K antagonist',
                'elderly_caution': True,
                'contraindications': ['active bleeding', 'severe liver disease']
            },
            'aspirin': {
                'class': 'antiplatelet',
                'description': 'Antiplatelet and pain reliever',
                'mechanism': 'COX inhibitor',
                'elderly_caution': True,
                'contraindications': ['active bleeding', 'peptic ulcer']
            },
            'ibuprofen': {
                'class': 'nsaid',
                'description': 'Nonsteroidal anti-inflammatory drug',
                'mechanism': 'COX-1/COX-2 inhibitor',
                'elderly_caution': True,
                'contraindications': ['active bleeding', 'severe renal impairment']
            },
            'lisinopril': {
                'class': 'ace_inhibitor',
                'description': 'ACE inhibitor for hypertension',
                'mechanism': 'Angiotensin-converting enzyme inhibitor',
                'contraindications': ['pregnancy', 'angioedema']
            },
            'metformin': {
                'class': 'biguanide',
                'description': 'Antidiabetic medication',
                'mechanism': 'Decreases hepatic glucose production',
                'contraindications': ['severe renal impairment', 'metabolic acidosis']
            },
            'simvastatin': {
                'class': 'statin',
                'description': 'HMG-CoA reductase inhibitor for cholesterol',
                'mechanism': 'Inhibits cholesterol synthesis',
                'contraindications': ['active liver disease', 'pregnancy']
            },
            'acetaminophen': {
                'class': 'analgesic',
                'description': 'Pain reliever and fever reducer',
                'mechanism': 'Central COX inhibition',
                'contraindications': ['severe liver disease']
            },
            'amoxicillin': {
                'class': 'penicillin',
                'description': 'Beta-lactam antibiotic',
                'mechanism': 'Inhibits bacterial cell wall synthesis',
                'contraindications': ['penicillin allergy']
            }
        }
    
    def _get_default_interactions(self) -> Dict:
        """Return default interactions database for demo purposes"""
        return {
            ('aspirin', 'warfarin'): {
                'severity': 'major',
                'risk_score': 0.89,
                'description': 'Increased risk of bleeding',
                'mechanism': 'Additive anticoagulant and antiplatelet effects',
                'clinical_effects': 'Hemorrhage, bruising, prolonged bleeding time',
                'recommendations': [
                    'Monitor INR closely',
                    'Watch for signs of bleeding',
                    'Consider alternative pain management'
                ],
                'evidence_level': 'A',
                'references': ['PMID:12345678', 'PMID:87654321']
            },
            ('ibuprofen', 'warfarin'): {
                'severity': 'major',
                'risk_score': 0.85,
                'description': 'Increased risk of bleeding',
                'mechanism': 'NSAIDs increase bleeding risk and may affect warfarin metabolism',
                'clinical_effects': 'GI bleeding, increased INR',
                'recommendations': [
                    'Avoid combination if possible',
                    'Use alternative analgesics (acetaminophen)',
                    'If necessary, monitor INR frequently'
                ],
                'evidence_level': 'A',
                'references': ['PMID:11111111']
            },
            ('aspirin', 'ibuprofen'): {
                'severity': 'moderate',
                'risk_score': 0.68,
                'description': 'Increased GI bleeding risk',
                'mechanism': 'Additive effects on gastric mucosa',
                'clinical_effects': 'Gastric ulceration, GI bleeding',
                'recommendations': [
                    'Use lowest effective doses',
                    'Consider gastric protection (PPI)',
                    'Monitor for GI symptoms'
                ],
                'evidence_level': 'B',
                'references': ['PMID:22222222']
            },
            ('lisinopril', 'ibuprofen'): {
                'severity': 'moderate',
                'risk_score': 0.62,
                'description': 'Reduced antihypertensive effect',
                'mechanism': 'NSAIDs can reduce ACE inhibitor efficacy',
                'clinical_effects': 'Increased blood pressure, reduced renal function',
                'recommendations': [
                    'Monitor blood pressure',
                    'Check renal function',
                    'Consider alternative analgesic'
                ],
                'evidence_level': 'B',
                'references': ['PMID:33333333']
            },
            ('metformin', 'simvastatin'): {
                'severity': 'minor',
                'risk_score': 0.25,
                'description': 'Possible increased risk of myopathy',
                'mechanism': 'Both drugs can rarely cause muscle problems',
                'clinical_effects': 'Muscle pain, weakness (rare)',
                'recommendations': [
                    'Monitor for muscle symptoms',
                    'Check CK if symptoms develop'
                ],
                'evidence_level': 'C',
                'references': ['PMID:44444444']
            }
        }
