"""
Knowledge Graph for Drug Interactions
Manages graph-based drug relationships and visualizations
"""
import json
import os
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Knowledge graph for drug relationships
    Manages nodes (drugs) and edges (interactions, shared properties)
    """
    
    def __init__(self):
        """Initialize knowledge graph"""
        self.nodes = {}
        self.edges = []
        self.build_graph()
    
    def build_graph(self):
        """Build knowledge graph from data"""
        from interaction_checker import InteractionChecker
        
        checker = InteractionChecker()
        
        # Add drug nodes
        for drug_name, drug_info in checker.drugs_db.items():
            self.nodes[drug_name] = {
                'id': drug_name,
                'label': drug_name.title(),
                'type': 'drug',
                'class': drug_info.get('class', 'unknown'),
                'properties': drug_info
            }
        
        # Add interaction edges
        for key, interaction in checker.interactions_db.items():
            drug1, drug2 = key
            self.edges.append({
                'source': drug1,
                'target': drug2,
                'type': 'interacts_with',
                'severity': interaction.get('severity'),
                'risk_score': interaction.get('risk_score', 0),
                'properties': interaction
            })
        
        # Add class relationship edges
        self._add_class_relationships()
        
        logger.info(f"Knowledge graph built: {len(self.nodes)} nodes, {len(self.edges)} edges")
    
    def _add_class_relationships(self):
        """Add edges between drugs in the same class"""
        from collections import defaultdict
        
        # Group drugs by class
        class_groups = defaultdict(list)
        for drug_name, node in self.nodes.items():
            drug_class = node.get('class')
            if drug_class and drug_class != 'unknown':
                class_groups[drug_class].append(drug_name)
        
        # Add same-class edges
        for drug_class, drugs in class_groups.items():
            for i, drug1 in enumerate(drugs):
                for drug2 in drugs[i+1:]:
                    self.edges.append({
                        'source': drug1,
                        'target': drug2,
                        'type': 'same_class',
                        'class': drug_class,
                        'properties': {}
                    })
    
    def generate_visualization(self, drugs: List[str]) -> Dict:
        """
        Generate visualization data for specified drugs
        
        Args:
            drugs: List of drug names to visualize
        
        Returns:
            Graph data in D3.js-compatible format
        """
        drugs = [d.lower() for d in drugs]
        
        # Filter nodes
        vis_nodes = []
        for drug in drugs:
            if drug in self.nodes:
                node = self.nodes[drug].copy()
                node['color'] = self._get_node_color(drug)
                node['size'] = 20
                vis_nodes.append(node)
        
        # Filter edges (only between selected drugs)
        vis_edges = []
        drug_set = set(drugs)
        
        for edge in self.edges:
            if edge['source'] in drug_set and edge['target'] in drug_set:
                edge_data = edge.copy()
                edge_data['color'] = self._get_edge_color(edge['type'], edge.get('severity'))
                edge_data['width'] = self._get_edge_width(edge.get('risk_score', 0))
                vis_edges.append(edge_data)
        
        # Calculate statistics
        interaction_edges = [e for e in vis_edges if e['type'] == 'interacts_with']
        severity_counts = self._count_severities(interaction_edges)
        
        return {
            'nodes': vis_nodes,
            'edges': vis_edges,
            'statistics': {
                'total_drugs': len(vis_nodes),
                'total_interactions': len(interaction_edges),
                'severity_distribution': severity_counts,
                'max_risk_score': max([e.get('risk_score', 0) for e in interaction_edges], default=0)
            },
            'layout': self._suggest_layout(len(vis_nodes))
        }
    
    def _get_node_color(self, drug: str) -> str:
        """Get color for drug node based on class"""
        drug_class = self.nodes.get(drug, {}).get('class', 'unknown')
        
        color_map = {
            'anticoagulant': '#e74c3c',  # Red
            'antiplatelet': '#e67e22',   # Orange
            'nsaid': '#f39c12',          # Yellow-orange
            'ace_inhibitor': '#3498db',  # Blue
            'biguanide': '#9b59b6',      # Purple
            'statin': '#1abc9c',         # Teal
            'analgesic': '#2ecc71',      # Green
            'penicillin': '#16a085',     # Dark teal
            'unknown': '#95a5a6'         # Gray
        }
        
        return color_map.get(drug_class, '#95a5a6')
    
    def _get_edge_color(self, edge_type: str, severity: str = None) -> str:
        """Get color for edge based on type and severity"""
        if edge_type == 'interacts_with':
            severity_colors = {
                'contraindicated': '#c0392b',  # Dark red
                'major': '#e74c3c',            # Red
                'moderate': '#f39c12',         # Orange
                'minor': '#f1c40f'             # Yellow
            }
            return severity_colors.get(severity, '#95a5a6')
        elif edge_type == 'same_class':
            return '#bdc3c7'  # Light gray
        else:
            return '#95a5a6'  # Gray
    
    def _get_edge_width(self, risk_score: float) -> int:
        """Get edge width based on risk score"""
        if risk_score >= 0.8:
            return 4
        elif risk_score >= 0.6:
            return 3
        elif risk_score >= 0.4:
            return 2
        else:
            return 1
    
    def _count_severities(self, edges: List[Dict]) -> Dict[str, int]:
        """Count interactions by severity"""
        counts = {
            'contraindicated': 0,
            'major': 0,
            'moderate': 0,
            'minor': 0
        }
        
        for edge in edges:
            severity = edge.get('severity', 'minor')
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _suggest_layout(self, node_count: int) -> str:
        """Suggest graph layout based on node count"""
        if node_count <= 3:
            return 'circle'
        elif node_count <= 6:
            return 'force'
        else:
            return 'hierarchical'
    
    def get_subgraph(self, drug: str, depth: int = 1) -> Dict:
        """
        Get subgraph around a specific drug
        
        Args:
            drug: Drug name
            depth: How many hops from the drug to include
        
        Returns:
            Subgraph data
        """
        drug = drug.lower()
        
        if drug not in self.nodes:
            return {'nodes': [], 'edges': []}
        
        # BFS to find connected nodes
        visited = set([drug])
        current_level = {drug}
        
        for _ in range(depth):
            next_level = set()
            for edge in self.edges:
                if edge['source'] in current_level and edge['target'] not in visited:
                    next_level.add(edge['target'])
                    visited.add(edge['target'])
                elif edge['target'] in current_level and edge['source'] not in visited:
                    next_level.add(edge['source'])
                    visited.add(edge['source'])
            current_level = next_level
        
        # Build subgraph
        return self.generate_visualization(list(visited))
    
    def find_path(self, drug1: str, drug2: str) -> List[str]:
        """
        Find shortest path between two drugs in the graph
        
        Args:
            drug1: Source drug
            drug2: Target drug
        
        Returns:
            List of drugs in the path
        """
        drug1 = drug1.lower()
        drug2 = drug2.lower()
        
        if drug1 not in self.nodes or drug2 not in self.nodes:
            return []
        
        # BFS for shortest path
        queue = [(drug1, [drug1])]
        visited = {drug1}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == drug2:
                return path
            
            # Find neighbors
            for edge in self.edges:
                neighbor = None
                if edge['source'] == current:
                    neighbor = edge['target']
                elif edge['target'] == current:
                    neighbor = edge['source']
                
                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def get_drug_statistics(self, drug: str) -> Dict:
        """Get statistics for a specific drug"""
        drug = drug.lower()
        
        if drug not in self.nodes:
            return {}
        
        # Count interactions
        interactions = [e for e in self.edges if (e['source'] == drug or e['target'] == drug) and e['type'] == 'interacts_with']
        
        severity_counts = {}
        for interaction in interactions:
            severity = interaction.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Find drugs in same class
        drug_class = self.nodes[drug].get('class')
        same_class_drugs = [
            name for name, node in self.nodes.items()
            if node.get('class') == drug_class and name != drug
        ]
        
        return {
            'total_interactions': len(interactions),
            'severity_distribution': severity_counts,
            'class': drug_class,
            'same_class_drugs': same_class_drugs,
            'high_risk_pairs': [
                {
                    'drug': e['target'] if e['source'] == drug else e['source'],
                    'severity': e.get('severity'),
                    'risk_score': e.get('risk_score', 0)
                }
                for e in interactions
                if e.get('severity') in ['major', 'contraindicated']
            ]
        }
    
    def export_graph(self, format: str = 'json') -> str:
        """Export entire graph in specified format"""
        graph_data = {
            'nodes': list(self.nodes.values()),
            'edges': self.edges,
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges)
            }
        }
        
        if format == 'json':
            return json.dumps(graph_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
