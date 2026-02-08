"""
Medical Knowledge Graph for drug interactions
"""
import networkx as nx
import logging
from typing import List, Dict, Set, Tuple, Optional
import pickle
from pathlib import Path

from app.utils.config import settings

logger = logging.getLogger(__name__)


class DrugKnowledgeGraph:
    """
    Knowledge graph representing relationships between drugs, enzymes, and proteins
    """
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._built = False
    
    async def build_graph(self):
        """Build the knowledge graph from data"""
        try:
            cache_path = Path(settings.GRAPH_CACHE_PATH)
            
            # Try to load from cache
            if cache_path.exists():
                logger.info("Loading knowledge graph from cache...")
                with open(cache_path, 'rb') as f:
                    self.graph = pickle.load(f)
                self._built = True
                logger.info(f"✅ Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
                return
            
            # Build from scratch
            logger.info("Building knowledge graph...")
            self._create_demo_graph()
            
            # Save to cache
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'wb') as f:
                pickle.dump(self.graph, f)
            
            self._built = True
            logger.info(f"✅ Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Error building knowledge graph: {str(e)}")
            # Build a minimal graph for demo
            self._create_demo_graph()
            self._built = True
    
    def _create_demo_graph(self):
        """Create a demonstration knowledge graph"""
        # Add drugs
        drugs = [
            ("Warfarin", "anticoagulant", ["CYP2C9", "CYP1A2"]),
            ("Aspirin", "antiplatelet", ["CYP2C9"]),
            ("Lisinopril", "ACE inhibitor", ["renal"]),
            ("Metformin", "antidiabetic", ["OCT1", "OCT2"]),
            ("Simvastatin", "statin", ["CYP3A4"]),
            ("Clarithromycin", "antibiotic", ["CYP3A4"]),
            ("Levothyroxine", "thyroid hormone", ["UGT1A1"]),
            ("Calcium", "supplement", []),
            ("Acetaminophen", "analgesic", ["CYP2E1", "UGT1A1"]),
            ("Ibuprofen", "NSAID", ["CYP2C9"]),
        ]
        
        for drug_name, drug_class, enzymes in drugs:
            self.graph.add_node(
                drug_name,
                type='drug',
                drug_class=drug_class,
                enzymes=enzymes
            )
            
            # Add enzyme nodes and relationships
            for enzyme in enzymes:
                if not self.graph.has_node(enzyme):
                    self.graph.add_node(enzyme, type='enzyme')
                self.graph.add_edge(drug_name, enzyme, relation='metabolized_by')
        
        # Add known interactions
        interactions = [
            ("Warfarin", "Aspirin", "increases_bleeding_risk", "MAJOR"),
            ("Simvastatin", "Clarithromycin", "increases_concentration", "MAJOR"),
            ("Levothyroxine", "Calcium", "decreases_absorption", "MODERATE"),
            ("Metformin", "Lisinopril", "increases_lactic_acidosis_risk", "MODERATE"),
            ("Warfarin", "Ibuprofen", "increases_bleeding_risk", "MAJOR"),
        ]
        
        for drug1, drug2, mechanism, severity in interactions:
            if self.graph.has_node(drug1) and self.graph.has_node(drug2):
                self.graph.add_edge(
                    drug1, drug2,
                    relation='interacts_with',
                    mechanism=mechanism,
                    severity=severity
                )
    
    def find_interaction_pathways(
        self,
        drug1: str,
        drug2: str
    ) -> List[Dict]:
        """
        Find all pathways connecting two drugs in the graph
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            
        Returns:
            List of pathway dictionaries
        """
        if not self.graph.has_node(drug1) or not self.graph.has_node(drug2):
            return []
        
        pathways = []
        
        # Direct interaction
        if self.graph.has_edge(drug1, drug2):
            edge_data = self.graph.get_edge_data(drug1, drug2)
            for key, data in edge_data.items():
                if data.get('relation') == 'interacts_with':
                    pathways.append({
                        'type': 'direct',
                        'path': [drug1, drug2],
                        'mechanism': data.get('mechanism', 'unknown'),
                        'severity': data.get('severity', 'UNKNOWN')
                    })
        
        # Find paths through shared enzymes
        shared_enzymes = self._find_shared_enzymes(drug1, drug2)
        for enzyme in shared_enzymes:
            pathways.append({
                'type': 'enzyme_mediated',
                'path': [drug1, enzyme, drug2],
                'mechanism': f'competitive_inhibition_via_{enzyme}',
                'severity': 'MODERATE'
            })
        
        # Find paths through pharmacological class
        drug1_data = self.graph.nodes.get(drug1, {})
        drug2_data = self.graph.nodes.get(drug2, {})
        
        if drug1_data.get('drug_class') == drug2_data.get('drug_class'):
            pathways.append({
                'type': 'class_effect',
                'path': [drug1, drug1_data.get('drug_class'), drug2],
                'mechanism': 'additive_pharmacological_effect',
                'severity': 'MODERATE'
            })
        
        return pathways
    
    def _find_shared_enzymes(self, drug1: str, drug2: str) -> Set[str]:
        """Find enzymes shared between two drugs"""
        enzymes1 = set()
        enzymes2 = set()
        
        # Get enzymes for drug1
        for _, target, data in self.graph.out_edges(drug1, data=True):
            if data.get('relation') == 'metabolized_by':
                enzymes1.add(target)
        
        # Get enzymes for drug2
        for _, target, data in self.graph.out_edges(drug2, data=True):
            if data.get('relation') == 'metabolized_by':
                enzymes2.add(target)
        
        return enzymes1.intersection(enzymes2)
    
    def get_drug_info(self, drug_name: str) -> Optional[Dict]:
        """Get information about a drug from the graph"""
        if not self.graph.has_node(drug_name):
            return None
        
        node_data = self.graph.nodes[drug_name]
        
        # Get related enzymes
        enzymes = []
        for _, target, data in self.graph.out_edges(drug_name, data=True):
            if data.get('relation') == 'metabolized_by':
                enzymes.append(target)
        
        # Get known interactions
        interactions = []
        for _, target, data in self.graph.out_edges(drug_name, data=True):
            if data.get('relation') == 'interacts_with':
                interactions.append({
                    'drug': target,
                    'mechanism': data.get('mechanism'),
                    'severity': data.get('severity')
                })
        
        return {
            'name': drug_name,
            'type': node_data.get('type'),
            'drug_class': node_data.get('drug_class'),
            'enzymes': enzymes,
            'known_interactions': interactions
        }
    
    def get_all_drugs(self) -> List[str]:
        """Get list of all drugs in the graph"""
        return [
            node for node, data in self.graph.nodes(data=True)
            if data.get('type') == 'drug'
        ]
    
    def calculate_drug_similarity(self, drug1: str, drug2: str) -> float:
        """
        Calculate similarity between two drugs based on graph structure
        
        Uses Jaccard similarity of enzyme sets
        """
        enzymes1 = self._find_shared_enzymes(drug1, drug1)  # Get all enzymes for drug1
        enzymes2 = self._find_shared_enzymes(drug2, drug2)  # Get all enzymes for drug2
        
        if not enzymes1 and not enzymes2:
            return 0.0
        
        intersection = len(enzymes1.intersection(enzymes2))
        union = len(enzymes1.union(enzymes2))
        
        return intersection / union if union > 0 else 0.0
    
    def find_alternatives(
        self,
        drug: str,
        interacting_drug: str,
        max_alternatives: int = 5
    ) -> List[Dict]:
        """
        Find alternative medications that don't interact with the given drug
        
        Args:
            drug: Drug to find alternatives for
            interacting_drug: Drug that interacts with the original
            max_alternatives: Maximum number of alternatives to return
            
        Returns:
            List of alternative drug dictionaries
        """
        if not self.graph.has_node(drug):
            return []
        
        drug_data = self.graph.nodes[drug]
        drug_class = drug_data.get('drug_class')
        
        alternatives = []
        
        # Find drugs in the same class
        for node, data in self.graph.nodes(data=True):
            if data.get('type') != 'drug' or node == drug:
                continue
            
            if data.get('drug_class') == drug_class:
                # Check if it interacts with the interacting_drug
                has_interaction = self.graph.has_edge(node, interacting_drug)
                
                if not has_interaction:
                    # Calculate safety score based on similarity
                    similarity = self.calculate_drug_similarity(node, drug)
                    safety_score = 0.9 - (0.3 * similarity)  # Less similar = safer
                    
                    alternatives.append({
                        'drug': node,
                        'safety_score': max(0.5, min(1.0, safety_score)),
                        'reason': f"Same therapeutic class ({drug_class}) without known interaction",
                        'considerations': "Consult healthcare provider before switching medications"
                    })
        
        # Sort by safety score and return top alternatives
        alternatives.sort(key=lambda x: x['safety_score'], reverse=True)
        return alternatives[:max_alternatives]
