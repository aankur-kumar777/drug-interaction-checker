"""
API endpoints for drug search
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from app.schemas.api_schemas import SearchRequest, DrugSearchResponse, DrugInfo
from app.main import knowledge_graph

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search", response_model=DrugSearchResponse)
async def search_drugs(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search for drugs by name
    
    Args:
        q: Search query string
        limit: Maximum number of results to return
        
    Returns:
        DrugSearchResponse with matching drugs
    """
    try:
        if knowledge_graph is None:
            raise HTTPException(status_code=503, detail="Knowledge graph not ready")
        
        logger.info(f"Searching for drugs: '{q}'")
        
        # Get all drugs from knowledge graph
        all_drugs = knowledge_graph.get_all_drugs()
        
        # Simple search - case-insensitive substring match
        query_lower = q.lower()
        matching_drugs = [
            drug for drug in all_drugs
            if query_lower in drug.lower()
        ]
        
        # Limit results
        matching_drugs = matching_drugs[:limit]
        
        # Build response
        results = []
        for drug_name in matching_drugs:
            drug_info = knowledge_graph.get_drug_info(drug_name)
            if drug_info:
                results.append(DrugInfo(
                    id=hash(drug_name) % 10000,
                    name=drug_name,
                    generic_name=drug_name,
                    drug_class=drug_info.get('drug_class'),
                    mechanism=None,
                    brand_names=None
                ))
        
        return DrugSearchResponse(
            status="success",
            query=q,
            results=results,
            total_results=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching drugs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error performing search")
