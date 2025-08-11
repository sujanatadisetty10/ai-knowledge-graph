"""
Enhanced export utilities for knowledge graphs.
Provides multiple export formats and advanced filtering capabilities.
"""
import json
import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
import logging
from pathlib import Path
import networkx as nx
from datetime import datetime


class ExportManager:
    """Manages multiple export formats for knowledge graphs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_to_json(self, triples: List[Dict], output_path: str, 
                      include_metadata: bool = True) -> Dict[str, Any]:
        """
        Export knowledge graph to JSON format with metadata.
        
        Args:
            triples: List of triple dictionaries
            output_path: Output file path
            include_metadata: Whether to include export metadata
            
        Returns:
            Export statistics
        """
        export_data = {
            "triples": triples,
            "statistics": {
                "total_triples": len(triples),
                "unique_entities": len(self._get_unique_entities(triples)),
                "unique_relationships": len(self._get_unique_relationships(triples)),
                "inferred_triples": len([t for t in triples if t.get("inferred", False)])
            }
        }
        
        if include_metadata:
            export_data["metadata"] = {
                "export_timestamp": datetime.now().isoformat(),
                "format_version": "1.0",
                "generator": "AI Knowledge Graph Generator"
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported {len(triples)} triples to JSON: {output_path}")
        return export_data["statistics"]
    
    def export_to_csv(self, triples: List[Dict], output_path: str) -> Dict[str, Any]:
        """
        Export knowledge graph to CSV format.
        
        Args:
            triples: List of triple dictionaries
            output_path: Output file path
            
        Returns:
            Export statistics
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = ['subject', 'predicate', 'object', 'inferred', 'chunk', 'confidence']
            writer.writerow(headers)
            
            # Write data
            for triple in triples:
                row = [
                    triple.get('subject', ''),
                    triple.get('predicate', ''),
                    triple.get('object', ''),
                    triple.get('inferred', False),
                    triple.get('chunk', 0),
                    triple.get('confidence', 1.0)
                ]
                writer.writerow(row)
        
        stats = {
            "total_triples": len(triples),
            "format": "CSV"
        }
        
        self.logger.info(f"Exported {len(triples)} triples to CSV: {output_path}")
        return stats
    
    def export_to_graphml(self, triples: List[Dict], output_path: str) -> Dict[str, Any]:
        """
        Export knowledge graph to GraphML format for use with graph analysis tools.
        
        Args:
            triples: List of triple dictionaries
            output_path: Output file path
            
        Returns:
            Export statistics
        """
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for triple in triples:
            subject = triple.get('subject', '')
            obj = triple.get('object', '')
            predicate = triple.get('predicate', '')
            
            if subject and obj and predicate:
                # Add nodes with attributes
                G.add_node(subject, type='entity')
                G.add_node(obj, type='entity')
                
                # Add edge with attributes
                G.add_edge(subject, obj, 
                          relationship=predicate,
                          inferred=triple.get('inferred', False),
                          chunk=triple.get('chunk', 0),
                          confidence=triple.get('confidence', 1.0))
        
        # Export to GraphML
        nx.write_graphml(G, output_path)
        
        stats = {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "format": "GraphML"
        }
        
        self.logger.info(f"Exported graph to GraphML: {output_path}")
        return stats
    
    def export_to_gexf(self, triples: List[Dict], output_path: str) -> Dict[str, Any]:
        """
        Export knowledge graph to GEXF format for Gephi visualization.
        
        Args:
            triples: List of triple dictionaries
            output_path: Output file path
            
        Returns:
            Export statistics
        """
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes and edges with attributes
        for triple in triples:
            subject = triple.get('subject', '')
            obj = triple.get('object', '')
            predicate = triple.get('predicate', '')
            
            if subject and obj and predicate:
                G.add_node(subject, label=subject)
                G.add_node(obj, label=obj)
                G.add_edge(subject, obj, 
                          label=predicate,
                          weight=1.0 if not triple.get('inferred', False) else 0.5)
        
        # Export to GEXF
        nx.write_gexf(G, output_path)
        
        stats = {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "format": "GEXF"
        }
        
        self.logger.info(f"Exported graph to GEXF: {output_path}")
        return stats
    
    def export_to_rdf_turtle(self, triples: List[Dict], output_path: str) -> Dict[str, Any]:
        """
        Export knowledge graph to RDF Turtle format.
        
        Args:
            triples: List of triple dictionaries
            output_path: Output file path
            
        Returns:
            Export statistics
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write prefixes
            f.write("@prefix kg: <http://example.org/knowledge-graph/> .\n")
            f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
            f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")
            
            # Write triples
            for triple in triples:
                subject = self._format_uri(triple.get('subject', ''))
                predicate = self._format_uri(triple.get('predicate', ''))
                obj = self._format_uri(triple.get('object', ''))
                
                if subject and predicate and obj:
                    f.write(f"kg:{subject} kg:{predicate} kg:{obj} .\n")
        
        stats = {
            "total_triples": len(triples),
            "format": "RDF Turtle"
        }
        
        self.logger.info(f"Exported {len(triples)} triples to RDF Turtle: {output_path}")
        return stats
    
    def _format_uri(self, text: str) -> str:
        """Format text for use in URI."""
        return text.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
    
    def _get_unique_entities(self, triples: List[Dict]) -> Set[str]:
        """Get set of unique entities from triples."""
        entities = set()
        for triple in triples:
            entities.add(triple.get('subject', ''))
            entities.add(triple.get('object', ''))
        entities.discard('')  # Remove empty strings
        return entities
    
    def _get_unique_relationships(self, triples: List[Dict]) -> Set[str]:
        """Get set of unique relationships from triples."""
        relationships = set()
        for triple in triples:
            rel = triple.get('predicate', '')
            if rel:
                relationships.add(rel)
        return relationships


class GraphFilter:
    """Advanced filtering capabilities for knowledge graphs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def filter_by_entities(self, triples: List[Dict], entities: List[str], 
                          include_mode: bool = True) -> List[Dict]:
        """
        Filter triples by specific entities.
        
        Args:
            triples: List of triple dictionaries
            entities: List of entity names to filter by
            include_mode: If True, include only these entities; if False, exclude them
            
        Returns:
            Filtered list of triples
        """
        entities_set = set(entity.lower() for entity in entities)
        filtered = []
        
        for triple in triples:
            subject = triple.get('subject', '').lower()
            obj = triple.get('object', '').lower()
            
            has_entity = subject in entities_set or obj in entities_set
            
            if (include_mode and has_entity) or (not include_mode and not has_entity):
                filtered.append(triple)
        
        self.logger.info(f"Filtered {len(triples)} -> {len(filtered)} triples by entities")
        return filtered
    
    def filter_by_relationships(self, triples: List[Dict], relationships: List[str], 
                              include_mode: bool = True) -> List[Dict]:
        """
        Filter triples by specific relationship types.
        
        Args:
            triples: List of triple dictionaries
            relationships: List of relationship types to filter by
            include_mode: If True, include only these relationships; if False, exclude them
            
        Returns:
            Filtered list of triples
        """
        relationships_set = set(rel.lower() for rel in relationships)
        filtered = []
        
        for triple in triples:
            predicate = triple.get('predicate', '').lower()
            
            has_relationship = predicate in relationships_set
            
            if (include_mode and has_relationship) or (not include_mode and not has_relationship):
                filtered.append(triple)
        
        self.logger.info(f"Filtered {len(triples)} -> {len(filtered)} triples by relationships")
        return filtered
    
    def filter_by_inference_status(self, triples: List[Dict], include_inferred: bool = True, 
                                 include_original: bool = True) -> List[Dict]:
        """
        Filter triples by inference status.
        
        Args:
            triples: List of triple dictionaries
            include_inferred: Whether to include inferred relationships
            include_original: Whether to include original relationships
            
        Returns:
            Filtered list of triples
        """
        filtered = []
        
        for triple in triples:
            is_inferred = triple.get('inferred', False)
            
            if (is_inferred and include_inferred) or (not is_inferred and include_original):
                filtered.append(triple)
        
        self.logger.info(f"Filtered {len(triples)} -> {len(filtered)} triples by inference status")
        return filtered
    
    def filter_by_confidence(self, triples: List[Dict], min_confidence: float = 0.0, 
                           max_confidence: float = 1.0) -> List[Dict]:
        """
        Filter triples by confidence score.
        
        Args:
            triples: List of triple dictionaries
            min_confidence: Minimum confidence threshold
            max_confidence: Maximum confidence threshold
            
        Returns:
            Filtered list of triples
        """
        filtered = []
        
        for triple in triples:
            confidence = triple.get('confidence', 1.0)
            
            if min_confidence <= confidence <= max_confidence:
                filtered.append(triple)
        
        self.logger.info(f"Filtered {len(triples)} -> {len(filtered)} triples by confidence")
        return filtered
    
    def filter_by_chunk(self, triples: List[Dict], chunks: List[int]) -> List[Dict]:
        """
        Filter triples by source chunk.
        
        Args:
            triples: List of triple dictionaries
            chunks: List of chunk numbers to include
            
        Returns:
            Filtered list of triples
        """
        chunks_set = set(chunks)
        filtered = []
        
        for triple in triples:
            chunk = triple.get('chunk', 0)
            
            if chunk in chunks_set:
                filtered.append(triple)
        
        self.logger.info(f"Filtered {len(triples)} -> {len(filtered)} triples by chunks")
        return filtered
    
    def get_subgraph_around_entity(self, triples: List[Dict], entity: str, 
                                 max_hops: int = 2) -> List[Dict]:
        """
        Extract subgraph around a specific entity within specified hops.
        
        Args:
            triples: List of triple dictionaries
            entity: Central entity name
            max_hops: Maximum number of hops from the central entity
            
        Returns:
            Subgraph triples
        """
        # Build adjacency information
        adjacency = {}
        triple_dict = {}
        
        for triple in triples:
            subject = triple.get('subject', '')
            obj = triple.get('object', '')
            
            if subject not in adjacency:
                adjacency[subject] = set()
            if obj not in adjacency:
                adjacency[obj] = set()
            
            adjacency[subject].add(obj)
            adjacency[obj].add(subject)  # Undirected for neighborhood search
            
            triple_dict[(subject, obj)] = triple
        
        # BFS to find entities within max_hops
        visited = set()
        queue = [(entity.lower(), 0)]  # (entity, distance)
        entities_in_subgraph = set()
        
        while queue:
            current_entity, distance = queue.pop(0)
            
            if current_entity in visited or distance > max_hops:
                continue
            
            visited.add(current_entity)
            entities_in_subgraph.add(current_entity)
            
            # Add neighbors
            for neighbor in adjacency.get(current_entity, []):
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
        
        # Filter triples to include only those in the subgraph
        subgraph_triples = []
        for triple in triples:
            subject = triple.get('subject', '').lower()
            obj = triple.get('object', '').lower()
            
            if subject in entities_in_subgraph and obj in entities_in_subgraph:
                subgraph_triples.append(triple)
        
        self.logger.info(f"Extracted subgraph around '{entity}': {len(subgraph_triples)} triples")
        return subgraph_triples


def export_multiple_formats(triples: List[Dict], base_filename: str, 
                          formats: List[str] = None) -> Dict[str, Any]:
    """
    Export knowledge graph to multiple formats.
    
    Args:
        triples: List of triple dictionaries
        base_filename: Base filename without extension
        formats: List of formats to export ('json', 'csv', 'graphml', 'gexf', 'turtle')
        
    Returns:
        Dictionary with export results for each format
    """
    if formats is None:
        formats = ['json', 'csv', 'graphml']
    
    exporter = ExportManager()
    results = {}
    
    for format_name in formats:
        try:
            output_path = f"{base_filename}.{format_name}"
            
            if format_name == 'json':
                stats = exporter.export_to_json(triples, output_path)
            elif format_name == 'csv':
                stats = exporter.export_to_csv(triples, output_path)
            elif format_name == 'graphml':
                stats = exporter.export_to_graphml(triples, output_path)
            elif format_name == 'gexf':
                stats = exporter.export_to_gexf(triples, output_path)
            elif format_name == 'turtle':
                stats = exporter.export_to_rdf_turtle(triples, output_path)
            else:
                logging.warning(f"Unknown export format: {format_name}")
                continue
            
            results[format_name] = {
                "status": "success",
                "file_path": output_path,
                "statistics": stats
            }
            
        except Exception as e:
            logging.error(f"Failed to export to {format_name}: {e}")
            results[format_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results
