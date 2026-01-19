"""
Financial Knowledge Graph Builder
Extracts entities and relationships from financial documents to build a knowledge graph.
"""

from typing import List, Dict, Any, Tuple
import re
from collections import defaultdict

class FinancialKnowledgeGraph:
    """
    Builds a knowledge graph from financial documents.
    Nodes: Companies, Metrics, People, Products, Industries
    Edges: Relationships (competes_with, has_metric, reports, etc.)
    """
    
    def __init__(self):
        self.nodes = {}  # {node_id: {type, name, properties}}
        self.edges = []  # [{source, target, relationship, properties}]
        self.node_counter = 0
    
    def extract_entities(self, text: str, ticker: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text using pattern matching and NLP.
        """
        entities = []
        
        # Extract company mentions
        company_patterns = [
            r'\b([A-Z]{2,5})\b',  # Ticker symbols
            r'\b(Apple|Microsoft|Google|Amazon|Tesla|Meta|NVIDIA)\b',  # Major companies
        ]
        
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group(1),
                    'type': 'COMPANY',
                    'start': match.start(),
                    'end': match.end()
                }
                entities.append(entity)
        
        # Extract financial metrics
        metric_patterns = [
            r'\b(Revenue|Net Income|EBITDA|EPS|Cash Flow|Assets|Liabilities|Equity)\b',
            r'\b(Operating Margin|Profit Margin|ROE|ROA|Debt-to-Equity)\b',
        ]
        
        for pattern in metric_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group(1),
                    'type': 'METRIC',
                    'start': match.start(),
                    'end': match.end()
                }
                entities.append(entity)
        
        # Extract people (executives, board members)
        people_patterns = [
            r'\b(CEO|CFO|CTO|President|Chairman)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(CEO|CFO|CTO|President)',
        ]
        
        for pattern in people_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group(0),
                    'type': 'PERSON',
                    'start': match.start(),
                    'end': match.end()
                }
                entities.append(entity)
        
        # Extract products/services
        product_patterns = [
            r'\b(iPhone|iPad|Mac|Windows|Azure|AWS|Tesla Model|Xbox|PlayStation)\b',
        ]
        
        for pattern in product_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group(1),
                    'type': 'PRODUCT',
                    'start': match.start(),
                    'end': match.end()
                }
                entities.append(entity)
        
        return entities
    
    def extract_relationships(self, text: str, entities: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities.
        """
        relationships = []
        
        # Pattern: Company has Metric
        for i, entity1 in enumerate(entities):
            if entity1['type'] == 'COMPANY':
                # Look for metrics nearby
                for entity2 in entities[i+1:i+10]:  # Check next 10 entities
                    if entity2['type'] == 'METRIC':
                        # Check if they're close in text
                        if abs(entity1['end'] - entity2['start']) < 200:
                            relationships.append({
                                'source': entity1['text'],
                                'target': entity2['text'],
                                'relationship': 'HAS_METRIC',
                                'confidence': 0.8
                            })
        
        # Pattern: Company competes with Company
        companies = [e for e in entities if e['type'] == 'COMPANY']
        for i, company1 in enumerate(companies):
            for company2 in companies[i+1:]:
                # Check if they appear in competitive context
                text_between = text[min(company1['end'], company2['end']):max(company1['start'], company2['start'])]
                competitive_keywords = ['competitor', 'compete', 'rival', 'vs', 'versus', 'compared to']
                if any(kw in text_between.lower() for kw in competitive_keywords):
                    relationships.append({
                        'source': company1['text'],
                        'target': company2['text'],
                        'relationship': 'COMPETES_WITH',
                        'confidence': 0.7
                    })
        
        # Pattern: Person works_at Company
        people = [e for e in entities if e['type'] == 'PERSON']
        for person in people:
            # Find nearest company
            for company in companies:
                if abs(person['start'] - company['start']) < 300:
                    relationships.append({
                        'source': person['text'],
                        'target': company['text'],
                        'relationship': 'WORKS_AT',
                        'confidence': 0.6
                    })
        
        return relationships
    
    def add_document(self, text: str, ticker: str, metadata: Dict = None):
        """
        Process a document and add nodes/edges to the graph.
        """
        # Extract entities
        entities = self.extract_entities(text, ticker)
        
        # Extract relationships
        relationships = self.extract_relationships(text, entities)
        
        # Add company node
        company_id = self._add_node(ticker, 'COMPANY', {'ticker': ticker})
        
        # Add metric nodes and edges
        metrics_found = set()
        for entity in entities:
            if entity['type'] == 'METRIC':
                metric_name = entity['text']
                if metric_name not in metrics_found:
                    metric_id = self._add_node(metric_name, 'METRIC', {})
                    self._add_edge(company_id, metric_id, 'HAS_METRIC', {})
                    metrics_found.add(metric_name)
        
        # Add relationship edges
        for rel in relationships:
            source_id = self._get_or_create_node(rel['source'], self._infer_type(rel['source']))
            target_id = self._get_or_create_node(rel['target'], self._infer_type(rel['target']))
            self._add_edge(source_id, target_id, rel['relationship'], {'confidence': rel['confidence']})
        
        return {
            'entities': len(entities),
            'relationships': len(relationships),
            'nodes_added': len(self.nodes)
        }
    
    def _add_node(self, name: str, node_type: str, properties: Dict) -> str:
        """Add a node to the graph."""
        node_id = f"{node_type}_{name}"
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                'id': node_id,
                'name': name,
                'type': node_type,
                'properties': properties
            }
        return node_id
    
    def _get_or_create_node(self, name: str, node_type: str) -> str:
        """Get existing node or create new one."""
        node_id = f"{node_type}_{name}"
        if node_id not in self.nodes:
            return self._add_node(name, node_type, {})
        return node_id
    
    def _infer_type(self, name: str) -> str:
        """Infer entity type from name."""
        if re.match(r'^[A-Z]{2,5}$', name):
            return 'COMPANY'
        if name in ['Revenue', 'Net Income', 'EBITDA', 'EPS']:
            return 'METRIC'
        if 'CEO' in name or 'CFO' in name:
            return 'PERSON'
        return 'ENTITY'
    
    def _add_edge(self, source_id: str, target_id: str, relationship: str, properties: Dict):
        """Add an edge to the graph."""
        edge = {
            'source': source_id,
            'target': target_id,
            'relationship': relationship,
            'properties': properties
        }
        self.edges.append(edge)
    
    def query(self, query_type: str, **kwargs) -> List[Dict]:
        """
        Query the knowledge graph.
        
        Examples:
        - query('companies_with_metric', metric='Revenue')
        - query('competitors', company='AAPL')
        - query('metrics', company='AAPL')
        """
        if query_type == 'companies_with_metric':
            metric = kwargs.get('metric')
            results = []
            for edge in self.edges:
                if edge['relationship'] == 'HAS_METRIC':
                    target_node = self.nodes.get(edge['target'])
                    if target_node and target_node['name'] == metric:
                        source_node = self.nodes.get(edge['source'])
                        if source_node:
                            results.append(source_node['name'])
            return results
        
        elif query_type == 'competitors':
            company = kwargs.get('company')
            results = []
            company_id = f"COMPANY_{company}"
            for edge in self.edges:
                if edge['relationship'] == 'COMPETES_WITH':
                    if edge['source'] == company_id:
                        target_node = self.nodes.get(edge['target'])
                        if target_node:
                            results.append(target_node['name'])
                    elif edge['target'] == company_id:
                        source_node = self.nodes.get(edge['source'])
                        if source_node:
                            results.append(source_node['name'])
            return results
        
        elif query_type == 'metrics':
            company = kwargs.get('company')
            company_id = f"COMPANY_{company}"
            results = []
            for edge in self.edges:
                if edge['relationship'] == 'HAS_METRIC' and edge['source'] == company_id:
                    target_node = self.nodes.get(edge['target'])
                    if target_node:
                        results.append(target_node['name'])
            return results
        
        return []
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node['type']] += 1
        
        relationship_types = defaultdict(int)
        for edge in self.edges:
            relationship_types[edge['relationship']] += 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': dict(node_types),
            'relationship_types': dict(relationship_types)
        }


# Global instance
_knowledge_graph = None

def get_knowledge_graph() -> FinancialKnowledgeGraph:
    """Get or create knowledge graph instance."""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = FinancialKnowledgeGraph()
    return _knowledge_graph
