"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Drug Interaction Checker"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/drug_interactions"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # ML Models
    MODEL_PATH: str = "models"
    INTERACTION_MODEL_PATH: str = "models/interaction_predictor.pkl"
    SEVERITY_MODEL_PATH: str = "models/severity_classifier.pkl"
    BERT_MODEL_NAME: str = "dmis-lab/biobert-v1.1"
    
    # Knowledge Graph
    GRAPH_CACHE_PATH: str = "cache/knowledge_graph.pkl"
    
    # Feature Engineering
    FEATURE_CACHE_PATH: str = "cache/features"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    # External APIs
    DRUGBANK_API_KEY: str = os.getenv("DRUGBANK_API_KEY", "")
    PUBMED_API_KEY: str = os.getenv("PUBMED_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
