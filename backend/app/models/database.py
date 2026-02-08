"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationships
drug_enzyme_association = Table(
    'drug_enzyme_association',
    Base.metadata,
    Column('drug_id', Integer, ForeignKey('drugs.id')),
    Column('enzyme_id', Integer, ForeignKey('enzymes.id'))
)


class Drug(Base):
    """Drug information model"""
    __tablename__ = 'drugs'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    generic_name = Column(String(255), index=True)
    brand_names = Column(JSON)  # List of brand names
    drug_class = Column(String(100), index=True)
    mechanism = Column(Text)
    indication = Column(Text)
    
    # Pharmacological properties
    protein_binding = Column(Float)  # Percentage
    half_life = Column(Float)  # Hours
    bioavailability = Column(Float)  # Percentage
    
    # Chemical properties
    molecular_weight = Column(Float)
    smiles = Column(Text)  # Chemical structure
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enzymes = relationship("Enzyme", secondary=drug_enzyme_association, back_populates="drugs")
    interactions_as_drug1 = relationship("Interaction", foreign_keys="Interaction.drug1_id", back_populates="drug1")
    interactions_as_drug2 = relationship("Interaction", foreign_keys="Interaction.drug2_id", back_populates="drug2")


class Enzyme(Base):
    """Enzyme/Protein model"""
    __tablename__ = 'enzymes'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    gene_name = Column(String(50))
    function = Column(Text)
    
    drugs = relationship("Drug", secondary=drug_enzyme_association, back_populates="enzymes")


class Interaction(Base):
    """Drug interaction model"""
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    drug1_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    drug2_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    
    severity = Column(String(20), index=True)  # MAJOR, MODERATE, MINOR
    confidence = Column(Float)  # ML model confidence
    
    description = Column(Text)
    mechanism = Column(Text)
    clinical_effects = Column(JSON)  # List of effects
    
    # Evidence
    evidence_level = Column(String(50))  # A, B, C, D
    evidence_quality = Column(String(20))  # HIGH, MODERATE, LOW
    
    # Recommendations
    recommendations = Column(JSON)  # List of recommendations
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drug1 = relationship("Drug", foreign_keys=[drug1_id], back_populates="interactions_as_drug1")
    drug2 = relationship("Drug", foreign_keys=[drug2_id], back_populates="interactions_as_drug2")
    evidence = relationship("ClinicalEvidence", back_populates="interaction")
    alternatives = relationship("Alternative", back_populates="interaction")


class ClinicalEvidence(Base):
    """Clinical evidence for interactions"""
    __tablename__ = 'clinical_evidence'
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    
    study_type = Column(String(50))  # RCT, Case Report, Meta-analysis, etc.
    pmid = Column(String(20))  # PubMed ID
    title = Column(Text)
    summary = Column(Text)
    
    sample_size = Column(Integer)
    year = Column(Integer)
    
    interaction = relationship("Interaction", back_populates="evidence")


class Alternative(Base):
    """Alternative medication recommendations"""
    __tablename__ = 'alternatives'
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    original_drug_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    alternative_drug_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    
    safety_score = Column(Float)  # 0-1
    reason = Column(Text)
    considerations = Column(Text)
    
    interaction = relationship("Interaction", back_populates="alternatives")
    original_drug = relationship("Drug", foreign_keys=[original_drug_id])
    alternative_drug = relationship("Drug", foreign_keys=[alternative_drug_id])


class PredictionLog(Base):
    """Log of predictions for monitoring and improvement"""
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    medications = Column(JSON)  # List of drug names
    predictions = Column(JSON)  # Full prediction results
    confidence_scores = Column(JSON)
    
    processing_time = Column(Float)  # Milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Optional user feedback
    user_feedback = Column(JSON)
