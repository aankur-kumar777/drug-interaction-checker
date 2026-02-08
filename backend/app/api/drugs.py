"""
API endpoints for drug information
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

from app.schemas.api_schemas import DrugInfo
from app.main import knowledge_graph

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/drugs", response_model=List[DrugInfo])
async def get_all_drugs(
    limit: int = 50,
    offset: int = 0,
    drug_class: Optional[str] = None
):
    """
    Get list of all available drugs
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        drug_class: Filter by drug class
        
    Returns:
        List of DrugInfo objects
    """
    try:
        if knowledge_graph is None:
            raise HTTPException(status_code=503, detail="Knowledge graph not ready")
        
        all_drugs = knowledge_graph.get_all_drugs()
        
        # Filter by drug class if specified
        if drug_class:
            filtered_drugs = []
            for drug_name in all_drugs:
                drug_info = knowledge_graph.get_drug_info(drug_name)
                if drug_info and drug_info.get('drug_class') == drug_class:
                    filtered_drugs.append(drug_name)
            all_drugs = filtered_drugs
        
        # Apply pagination
        paginated_drugs = all_drugs[offset:offset + limit]
        
        # Build response
        results = []
        for drug_name in paginated_drugs:
            drug_info = knowledge_graph.get_drug_info(drug_name)
            if drug_info:
                results.append(DrugInfo(
                    id=hash(drug_name) % 10000,  # Demo ID
                    name=drug_name,
                    generic_name=drug_name,  # Demo
                    drug_class=drug_info.get('drug_class'),
                    mechanism=f"Mechanism of action for {drug_name}",
                    brand_names=[]
                ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drugs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving drugs")


@router.get("/drugs/{drug_name}", response_model=DrugInfo)
async def get_drug_details(drug_name: str):
    """
    Get detailed information about a specific drug
    
    Args:
        drug_name: Name of the drug
        
    Returns:
        DrugInfo object with detailed information
    """
    try:
        if knowledge_graph is None:
            raise HTTPException(status_code=503, detail="Knowledge graph not ready")
        
        drug_info = knowledge_graph.get_drug_info(drug_name)
        
        if not drug_info:
            raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
        
        return DrugInfo(
            id=hash(drug_name) % 10000,
            name=drug_name,
            generic_name=drug_name,
            drug_class=drug_info.get('drug_class'),
            mechanism=f"Mechanism of action for {drug_name}",
            brand_names=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drug details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving drug details")


@router.get("/drugs/{drug_name}/interactions")
async def get_drug_interactions(drug_name: str):
    """
    Get all known interactions for a specific drug
    
    Args:
        drug_name: Name of the drug
        
    Returns:
        List of known interactions
    """
    try:
        if knowledge_graph is None:
            raise HTTPException(status_code=503, detail="Knowledge graph not ready")
        
        drug_info = knowledge_graph.get_drug_info(drug_name)
        
        if not drug_info:
            raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
        
        interactions = drug_info.get('known_interactions', [])
        
        return {
            "drug": drug_name,
            "total_interactions": len(interactions),
            "interactions": interactions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drug interactions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving interactions")
