#!/usr/bin/env python3
"""
Load sample drug data into the system
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

print("📊 Loading sample drug interaction data...")

# This is a placeholder script
# In a production system, this would load data from:
# - DrugBank database
# - FDA drug labels
# - Clinical literature

sample_drugs = [
    {
        "name": "Warfarin",
        "drug_class": "anticoagulant",
        "enzymes": ["CYP2C9", "CYP1A2"],
        "protein_binding": 99.0,
        "half_life": 40.0
    },
    {
        "name": "Aspirin",
        "drug_class": "antiplatelet",
        "enzymes": ["CYP2C9"],
        "protein_binding": 90.0,
        "half_life": 0.3
    },
    {
        "name": "Lisinopril",
        "drug_class": "ACE inhibitor",
        "enzymes": [],
        "protein_binding": 25.0,
        "half_life": 12.0
    },
    {
        "name": "Metformin",
        "drug_class": "antidiabetic",
        "enzymes": ["OCT1", "OCT2"],
        "protein_binding": 0.0,
        "half_life": 6.2
    },
    {
        "name": "Simvastatin",
        "drug_class": "statin",
        "enzymes": ["CYP3A4"],
        "protein_binding": 95.0,
        "half_life": 2.0
    },
]

print(f"✅ Sample data includes {len(sample_drugs)} medications")
print("💡 In production, integrate with:")
print("   - DrugBank API")
print("   - FDA Drug Labels")
print("   - PubMed for clinical evidence")
print("\n⚠️  This is sample data for demonstration purposes only")

# The knowledge graph in app/knowledge_graph/graph.py 
# will automatically load this demo data when initialized
