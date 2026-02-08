"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Interaction severity levels"""
    MAJOR = "MAJOR"
    MODERATE = "MODERATE"
    MINOR = "MINOR"


class EvidenceLevel(str, Enum):
    """Clinical evidence levels"""
    A = "A"  # Multiple RCTs
    B = "B"  # Single RCT or multiple cohort studies
    C = "C"  # Case reports or expert opinion
    D = "D"  # Theoretical/in-vitro


# Request Schemas
class InteractionCheckRequest(BaseModel):
    """Request to check drug interactions"""
    medications: List[str] = Field(..., min_items=2, max_items=20, description="List of medication names")
    patient_info: Optional[Dict[str, Any]] = Field(None, description="Optional patient information")
    
    @validator('medications')
    def validate_medications(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate medications found")
        return v


class SearchRequest(BaseModel):
    """Drug search request"""
    query: str = Field(..., min_length=2, max_length=100)
    limit: int = Field(10, ge=1, le=50)


# Response Schemas
class DrugInfo(BaseModel):
    """Basic drug information"""
    id: int
    name: str
    generic_name: Optional[str]
    drug_class: Optional[str]
    mechanism: Optional[str]
    brand_names: Optional[List[str]]


class ExplanationDetail(BaseModel):
    """Explainability information"""
    key_factors: List[Dict[str, float]] = Field(..., description="Feature importance scores")
    risk_contributors: Dict[str, float] = Field(..., description="Risk breakdown")
    pathway_description: Optional[str] = Field(None, description="Interaction pathway")


class AlternativeRecommendation(BaseModel):
    """Alternative medication recommendation"""
    drug: str
    reason: str
    safety_score: float = Field(..., ge=0, le=1)
    considerations: Optional[str] = None


class ClinicalEvidenceDetail(BaseModel):
    """Clinical evidence details"""
    study_type: str
    pmid: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    year: Optional[int]


class InteractionResult(BaseModel):
    """Individual interaction result"""
    drug1: str
    drug2: str
    severity: SeverityLevel
    confidence: float = Field(..., ge=0, le=1)
    
    description: str
    mechanism: str
    clinical_effects: List[str]
    
    recommendations: List[str]
    evidence_level: str
    evidence_quality: Optional[str]
    
    references: List[str] = Field(default_factory=list)
    alternatives: List[AlternativeRecommendation] = Field(default_factory=list)
    
    explanation: ExplanationDetail
    
    class Config:
        json_schema_extra = {
            "example": {
                "drug1": "Warfarin",
                "drug2": "Aspirin",
                "severity": "MAJOR",
                "confidence": 0.94,
                "description": "Increased risk of bleeding",
                "mechanism": "Additive anticoagulant effects",
                "clinical_effects": ["Gastrointestinal bleeding", "Intracranial hemorrhage"],
                "recommendations": ["Monitor INR closely", "Consider alternatives"],
                "evidence_level": "A",
                "evidence_quality": "HIGH",
                "references": ["PMID: 12345678"],
                "alternatives": [
                    {
                        "drug": "Acetaminophen",
                        "reason": "No anticoagulant interaction",
                        "safety_score": 0.95
                    }
                ],
                "explanation": {
                    "key_factors": [
                        {"feature": "CYP2C9 involvement", "weight": 0.31},
                        {"feature": "Anticoagulant class", "weight": 0.28}
                    ],
                    "risk_contributors": {
                        "pharmacodynamic": 0.65,
                        "pharmacokinetic": 0.35
                    }
                }
            }
        }


class InteractionCheckResponse(BaseModel):
    """Complete interaction check response"""
    status: str = "success"
    medications_checked: List[str]
    total_interactions: int
    results: List[InteractionResult]
    overall_risk_score: float = Field(..., ge=0, le=1)
    processed_at: datetime
    processing_time_ms: Optional[float] = None


class DrugSearchResponse(BaseModel):
    """Drug search results"""
    status: str = "success"
    query: str
    results: List[DrugInfo]
    total_results: int


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
