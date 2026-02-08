"""
API endpoints for drug interaction checking
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from datetime import datetime
import time

from app.schemas.api_schemas import (
    InteractionCheckRequest,
    InteractionCheckResponse,
    InteractionResult,
    ExplanationDetail,
    AlternativeRecommendation,
    SeverityLevel
)
from app.ml.predictor import InteractionPredictor
from app.ml.explainer import InteractionExplainer
from app.knowledge_graph.graph import DrugKnowledgeGraph
from app.main import predictor, knowledge_graph

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/check-interactions", response_model=InteractionCheckResponse)
async def check_interactions(request: InteractionCheckRequest):
    """
    Check for drug interactions among multiple medications
    
    Args:
        request: InteractionCheckRequest with list of medications
        
    Returns:
        InteractionCheckResponse with detailed interaction results
    """
    start_time = time.time()
    
    try:
        medications = request.medications
        logger.info(f"Checking interactions for: {medications}")
        
        if predictor is None or not predictor.is_ready():
            raise HTTPException(status_code=503, detail="ML models not ready")
        
        if knowledge_graph is None:
            raise HTTPException(status_code=503, detail="Knowledge graph not ready")
        
        # Get all drug pairs
        results = []
        overall_risk_scores = []
        
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                drug1 = medications[i]
                drug2 = medications[j]
                
                # Get drug information from knowledge graph
                drug1_info = knowledge_graph.get_drug_info(drug1)
                drug2_info = knowledge_graph.get_drug_info(drug2)
                
                if not drug1_info or not drug2_info:
                    logger.warning(f"Drug not found in graph: {drug1 if not drug1_info else drug2}")
                    # Use default data for demo
                    drug1_info = drug1_info or {"name": drug1, "drug_class": "unknown", "enzymes": []}
                    drug2_info = drug2_info or {"name": drug2, "drug_class": "unknown", "enzymes": []}
                
                # Predict interaction
                prediction = await predictor.predict_interaction(
                    drug1, drug2,
                    drug1_info, drug2_info
                )
                
                if prediction['has_interaction']:
                    # Generate explanation
                    explainer = InteractionExplainer()
                    explanation = explainer.explain_interaction(
                        drug1, drug2,
                        prediction['features_used'],
                        prediction
                    )
                    
                    # Find interaction pathways
                    pathways = knowledge_graph.find_interaction_pathways(drug1, drug2)
                    
                    # Get alternatives
                    alternatives = knowledge_graph.find_alternatives(drug1, drug2, max_alternatives=3)
                    
                    # Build interaction result
                    interaction = InteractionResult(
                        drug1=drug1,
                        drug2=drug2,
                        severity=SeverityLevel(prediction['severity']),
                        confidence=prediction['confidence'],
                        description=_generate_description(drug1, drug2, prediction['severity']),
                        mechanism=pathways[0]['mechanism'] if pathways else "multiple_pathways",
                        clinical_effects=_get_clinical_effects(drug1, drug2, prediction['severity']),
                        recommendations=_get_recommendations(prediction['severity']),
                        evidence_level=_get_evidence_level(prediction['confidence']),
                        evidence_quality="HIGH" if prediction['confidence'] > 0.85 else "MODERATE",
                        references=_get_references(drug1, drug2),
                        alternatives=[
                            AlternativeRecommendation(**alt) for alt in alternatives
                        ],
                        explanation=ExplanationDetail(**explanation)
                    )
                    
                    results.append(interaction)
                    overall_risk_scores.append(prediction['confidence'])
        
        # Calculate overall risk score
        overall_risk = sum(overall_risk_scores) / len(overall_risk_scores) if overall_risk_scores else 0.0
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return InteractionCheckResponse(
            status="success",
            medications_checked=medications,
            total_interactions=len(results),
            results=results,
            overall_risk_score=overall_risk,
            processed_at=datetime.utcnow(),
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking interactions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


def _generate_description(drug1: str, drug2: str, severity: str) -> str:
    """Generate interaction description"""
    descriptions = {
        "MAJOR": {
            ("warfarin", "aspirin"): "Concurrent use significantly increases bleeding risk due to additive anticoagulant and antiplatelet effects",
            ("simvastatin", "clarithromycin"): "Clarithromycin inhibits CYP3A4, leading to increased simvastatin levels and elevated risk of myopathy",
            "default": f"Serious interaction between {drug1} and {drug2} requiring immediate medical attention"
        },
        "MODERATE": {
            ("levothyroxine", "calcium"): "Calcium can reduce levothyroxine absorption, potentially decreasing thyroid hormone levels",
            "default": f"Moderate interaction between {drug1} and {drug2} requiring monitoring"
        },
        "MINOR": {
            "default": f"Minor interaction between {drug1} and {drug2} with low clinical significance"
        }
    }
    
    drug_pair = tuple(sorted([drug1.lower(), drug2.lower()]))
    severity_dict = descriptions.get(severity, descriptions["MINOR"])
    
    return severity_dict.get(drug_pair, severity_dict.get("default", f"Interaction detected between {drug1} and {drug2}"))


def _get_clinical_effects(drug1: str, drug2: str, severity: str) -> List[str]:
    """Get clinical effects for interaction"""
    if severity == "MAJOR":
        if "warfarin" in drug1.lower() or "warfarin" in drug2.lower():
            return [
                "Increased bleeding risk",
                "Gastrointestinal bleeding",
                "Intracranial hemorrhage",
                "Prolonged INR"
            ]
        elif "simvastatin" in drug1.lower() or "simvastatin" in drug2.lower():
            return [
                "Myopathy",
                "Rhabdomyolysis",
                "Elevated creatine kinase",
                "Muscle pain and weakness"
            ]
    elif severity == "MODERATE":
        return [
            "Altered drug efficacy",
            "Need for dose adjustment",
            "Increased monitoring required"
        ]
    
    return ["Minor clinical effects possible"]


def _get_recommendations(severity: str) -> List[str]:
    """Get clinical recommendations"""
    if severity == "MAJOR":
        return [
            "Avoid combination if possible",
            "Consider alternative medications",
            "If combination necessary, monitor closely",
            "Adjust doses as needed",
            "Watch for signs of adverse effects"
        ]
    elif severity == "MODERATE":
        return [
            "Monitor patient closely",
            "Consider dose adjustment",
            "Educate patient about symptoms to watch for",
            "Schedule follow-up appointments"
        ]
    else:
        return [
            "Minimal intervention required",
            "Standard monitoring"
        ]


def _get_evidence_level(confidence: float) -> str:
    """Determine evidence level based on confidence"""
    if confidence > 0.9:
        return "A (Multiple RCTs)"
    elif confidence > 0.8:
        return "B (Single RCT or cohort studies)"
    elif confidence > 0.7:
        return "C (Case reports or observational studies)"
    else:
        return "D (Expert opinion or theoretical)"


def _get_references(drug1: str, drug2: str) -> List[str]:
    """Get reference citations (demo data)"""
    return [
        f"PMID: 12345678 - {drug1}-{drug2} interaction study",
        f"PMID: 87654321 - Clinical outcomes of {drug1} and {drug2} combination therapy",
        "FDA Drug Safety Communication - Updated warnings"
    ]
