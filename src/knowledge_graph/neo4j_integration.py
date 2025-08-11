"""
Neo4j integration module for the AI Knowledge Graph Generator.
Provides functionality to export knowledge graphs to Neo4j and perform advanced queries.
"""
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j package not installed. Run 'pip install neo4j' to enable Neo4j integration.")

@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"
    max_retry_attempts: int = 3
    retry_delay: float = 1.0

class Neo4jIntegration:
    """Handles all Neo4j operations for the knowledge graph."""
    
    def __init__(self, config: Neo4jConfig):
        """
        Initialize Neo4j integration.
        
        Args:
            config: Neo4j connection configuration
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package is required. Install with: pip install neo4j")
        
        self.config = config
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password)
            )
            
            # Test connection
            with self.driver.session(database=self.config.database) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
            self.logger.info(f"Successfully connected to Neo4j at {self.config.uri}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.logger.info("Closed Neo4j connection")
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from the database.
        WARNING: This will delete all data!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                # Delete all relationships first, then nodes
                session.run("MATCH ()-[r]-() DELETE r")
                session.run("MATCH (n) DELETE n")
                
            self.logger.info("Successfully cleared Neo4j database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear database: {e}")
            return False
    
    def create_constraints_and_indexes(self):
        """Create constraints and indexes for better performance."""
        constraints_and_indexes = [
            # Create uniqueness constraint on Entity.name
            "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
            
            # Create indexes for better query performance
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX relationship_type_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.predicate)",
            "CREATE INDEX relationship_inferred_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.inferred)",
        ]
        
        with self.driver.session(database=self.config.database) as session:
            for constraint in constraints_and_indexes:
                try:
                    session.run(constraint)
                    self.logger.debug(f"Created constraint/index: {constraint}")
                except Exception as e:
                    self.logger.warning(f"Failed to create constraint/index: {e}")
    
    def import_knowledge_graph(self, triples: List[Dict[str, Any]], 
                             stats: Optional[Dict[str, Any]] = None,
                             clear_first: bool = True) -> bool:
        """
        Import knowledge graph triples into Neo4j.
        
        Args:
            triples: List of triple dictionaries with subject, predicate, object
            stats: Optional statistics about the graph
            clear_first: Whether to clear existing data first
            
        Returns:
            True if import successful, False otherwise
        """
        if not self.driver:
            self.logger.error("Not connected to Neo4j. Call connect() first.")
            return False
        
        try:
            # Clear database if requested
            if clear_first:
                self.clear_database()
            
            # Create constraints and indexes
            self.create_constraints_and_indexes()
            
            # Import entities and relationships
            self._import_entities(triples)
            self._import_relationships(triples)
            
            # Store metadata about the import
            if stats:
                self._store_metadata(stats)
            
            self.logger.info(f"Successfully imported {len(triples)} triples to Neo4j")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import knowledge graph: {e}")
            return False
    
    def _import_entities(self, triples: List[Dict[str, Any]]):
        """Import entities as nodes."""
        # Extract unique entities
        entities = set()
        entity_details = {}
        
        for triple in triples:
            subject = triple["subject"]
            obj = triple["object"]
            entities.add(subject)
            entities.add(obj)
            
            # Store additional details if available
            for entity in [subject, obj]:
                if entity not in entity_details:
                    entity_details[entity] = {
                        "name": entity,
                        "type": self._infer_entity_type(entity),
                        "chunk_count": 0,
                        "relationship_count": 0
                    }
                
                entity_details[entity]["chunk_count"] += 1
        
        # Count relationships for each entity
        for triple in triples:
            entity_details[triple["subject"]]["relationship_count"] += 1
            entity_details[triple["object"]]["relationship_count"] += 1
        
        # Batch create entities
        with self.driver.session(database=self.config.database) as session:
            batch_size = 1000
            entity_list = list(entities)
            
            for i in range(0, len(entity_list), batch_size):
                batch = entity_list[i:i + batch_size]
                batch_data = [entity_details[entity] for entity in batch]
                
                session.run("""
                    UNWIND $entities AS entity
                    MERGE (e:Entity {name: entity.name})
                    SET e.type = entity.type,
                        e.chunk_count = entity.chunk_count,
                        e.relationship_count = entity.relationship_count,
                        e.created_at = datetime(),
                        e.updated_at = datetime()
                """, entities=batch_data)
        
        self.logger.info(f"Imported {len(entities)} entities")
    
    def _import_relationships(self, triples: List[Dict[str, Any]]):
        """Import relationships as edges."""
        with self.driver.session(database=self.config.database) as session:
            batch_size = 1000
            
            for i in range(0, len(triples), batch_size):
                batch = triples[i:i + batch_size]
                
                session.run("""
                    UNWIND $triples AS triple
                    MATCH (subject:Entity {name: triple.subject})
                    MATCH (object:Entity {name: triple.object})
                    MERGE (subject)-[r:RELATES_TO {predicate: triple.predicate}]->(object)
                    SET r.inferred = COALESCE(triple.inferred, false),
                        r.chunk = COALESCE(triple.chunk, 0),
                        r.created_at = datetime(),
                        r.predicate_normalized = toLower(replace(triple.predicate, ' ', '_'))
                """, triples=batch)
        
        self.logger.info(f"Imported {len(triples)} relationships")
    
    def _store_metadata(self, stats: Dict[str, Any]):
        """Store metadata about the knowledge graph."""
        with self.driver.session(database=self.config.database) as session:
            session.run("""
                MERGE (meta:Metadata {type: 'knowledge_graph'})
                SET meta.nodes = $nodes,
                    meta.edges = $edges,
                    meta.communities = $communities,
                    meta.original_edges = $original_edges,
                    meta.inferred_edges = $inferred_edges,
                    meta.import_date = datetime(),
                    meta.version = '1.0'
            """, **stats)
    
    def _infer_entity_type(self, entity: str) -> str:
        """Infer entity type based on naming patterns."""
        entity_lower = entity.lower()
        
        # Person indicators
        if any(word in entity_lower for word in ['john', 'mary', 'james', 'smith', 'dr.', 'mr.', 'ms.']):
            return 'Person'
        
        # Location indicators
        if any(word in entity_lower for word in ['city', 'country', 'state', 'street', 'america', 'europe', 'asia']):
            return 'Location'
        
        # Technology indicators
        if any(word in entity_lower for word in ['engine', 'machine', 'computer', 'ai', 'software', 'technology']):
            return 'Technology'
        
        # Organization indicators
        if any(word in entity_lower for word in ['company', 'corporation', 'university', 'institute', 'organization']):
            return 'Organization'
        
        # Concept indicators
        if any(word in entity_lower for word in ['theory', 'concept', 'principle', 'method', 'process']):
            return 'Concept'
        
        # Default
        return 'General'
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about entities in the database."""
        with self.driver.session(database=self.config.database) as session:
            result = session.run("""
                MATCH (e:Entity)
                RETURN 
                    count(e) as total_entities,
                    collect(DISTINCT e.type) as entity_types,
                    avg(e.relationship_count) as avg_relationships,
                    max(e.relationship_count) as max_relationships,
                    min(e.relationship_count) as min_relationships
            """)
            
            record = result.single()
            if record:
                return dict(record)
            return {}
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get statistics about relationships in the database."""
        with self.driver.session(database=self.config.database) as session:
            result = session.run("""
                MATCH ()-[r:RELATES_TO]->()
                RETURN 
                    count(r) as total_relationships,
                    count(CASE WHEN r.inferred = true THEN 1 END) as inferred_relationships,
                    count(CASE WHEN r.inferred = false THEN 1 END) as original_relationships,
                    collect(DISTINCT r.predicate)[0..10] as sample_predicates
            """)
            
            record = result.single()
            if record:
                return dict(record)
            return {}
    
    def find_shortest_path(self, start_entity: str, end_entity: str, max_length: int = 5) -> List[Dict[str, Any]]:
        """
        Find shortest path between two entities.
        
        Args:
            start_entity: Starting entity name
            end_entity: Ending entity name
            max_length: Maximum path length to consider
            
        Returns:
            List of path dictionaries with nodes and relationships
        """
        with self.driver.session(database=self.config.database) as session:
            result = session.run("""
                MATCH path = shortestPath((start:Entity {name: $start})-[*..{max_length}]-(end:Entity {name: $end}))
                RETURN path,
                       length(path) as path_length,
                       [node in nodes(path) | node.name] as entity_names,
                       [rel in relationships(path) | rel.predicate] as predicates
                ORDER BY path_length
                LIMIT 5
            """.format(max_length=max_length), start=start_entity, end=end_entity)
            
            paths = []
            for record in result:
                paths.append({
                    "length": record["path_length"],
                    "entities": record["entity_names"],
                    "predicates": record["predicates"]
                })
            
            return paths
    
    def find_similar_entities(self, entity_name: str, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Find entities similar to the given entity based on shared relationships.
        
        Args:
            entity_name: Entity to find similarities for
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar entities with similarity scores
        """
        with self.driver.session(database=self.config.database) as session:
            result = session.run("""
                MATCH (target:Entity {name: $entity_name})-[r1:RELATES_TO]-(shared)
                MATCH (similar:Entity)-[r2:RELATES_TO]-(shared)
                WHERE target <> similar
                WITH target, similar, count(shared) as shared_connections,
                     size((target)-[:RELATES_TO]-()) as target_total,
                     size((similar)-[:RELATES_TO]-()) as similar_total
                WITH target, similar, shared_connections,
                     toFloat(shared_connections) / sqrt(target_total * similar_total) as similarity
                WHERE similarity >= $threshold
                RETURN similar.name as entity_name,
                       similar.type as entity_type,
                       shared_connections,
                       similarity
                ORDER BY similarity DESC
                LIMIT 20
            """, entity_name=entity_name, threshold=similarity_threshold)
            
            return [dict(record) for record in result]
    
    def get_entity_neighborhood(self, entity_name: str, depth: int = 2) -> Dict[str, Any]:
        """
        Get the neighborhood of an entity up to specified depth.
        
        Args:
            entity_name: Entity to get neighborhood for
            depth: Depth of neighborhood to retrieve
            
        Returns:
            Dictionary with nodes and relationships in the neighborhood
        """
        with self.driver.session(database=self.config.database) as session:
            result = session.run("""
                MATCH path = (center:Entity {name: $entity_name})-[*1..{depth}]-(neighbor:Entity)
                RETURN DISTINCT
                       collect(DISTINCT neighbor.name) as neighbors,
                       collect(DISTINCT center.name) as center_node
                UNION
                MATCH (center:Entity {name: $entity_name})-[r:RELATES_TO]-(neighbor:Entity)
                RETURN collect(DISTINCT {{
                    subject: startNode(r).name,
                    predicate: r.predicate,
                    object: endNode(r).name,
                    inferred: r.inferred
                }}) as relationships,
                       [] as center_node
            """.format(depth=depth), entity_name=entity_name)
            
            neighbors = set()
            relationships = []
            
            for record in result:
                if record["neighbors"]:
                    neighbors.update(record["neighbors"])
                if record.get("relationships"):
                    relationships.extend(record["relationships"])
            
            return {
                "center": entity_name,
                "neighbors": list(neighbors),
                "relationships": relationships,
                "neighbor_count": len(neighbors),
                "relationship_count": len(relationships)
            }
    
    def export_to_json(self, output_file: str = "neo4j_export.json") -> bool:
        """
        Export the entire knowledge graph from Neo4j to JSON.
        
        Args:
            output_file: Output JSON file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get all entities
                entities_result = session.run("""
                    MATCH (e:Entity)
                    RETURN e.name as name, e.type as type, 
                           e.relationship_count as relationship_count
                """)
                
                entities = [dict(record) for record in entities_result]
                
                # Get all relationships
                relationships_result = session.run("""
                    MATCH (s:Entity)-[r:RELATES_TO]->(o:Entity)
                    RETURN s.name as subject, r.predicate as predicate, 
                           o.name as object, r.inferred as inferred
                """)
                
                relationships = [dict(record) for record in relationships_result]
                
                # Get metadata
                metadata_result = session.run("""
                    MATCH (m:Metadata {type: 'knowledge_graph'})
                    RETURN m.nodes as nodes, m.edges as edges, 
                           m.communities as communities, m.import_date as import_date
                """)
                
                metadata = {}
                if metadata_result.peek():
                    metadata = dict(metadata_result.single())
                
                # Combine all data
                export_data = {
                    "metadata": metadata,
                    "entities": entities,
                    "relationships": relationships,
                    "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_entities": len(entities),
                    "total_relationships": len(relationships)
                }
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Exported knowledge graph to {output_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            return False

def create_neo4j_config_from_dict(config_dict: Dict[str, Any]) -> Neo4jConfig:
    """Create Neo4jConfig from dictionary configuration."""
    neo4j_config = config_dict.get("neo4j", {})
    
    return Neo4jConfig(
        uri=neo4j_config.get("uri", "bolt://localhost:7687"),
        username=neo4j_config.get("username", "neo4j"),
        password=neo4j_config.get("password", "password"),
        database=neo4j_config.get("database", "neo4j"),
        max_retry_attempts=neo4j_config.get("max_retry_attempts", 3),
        retry_delay=neo4j_config.get("retry_delay", 1.0)
    )

# Convenience functions for easy integration
def export_triples_to_neo4j(triples: List[Dict[str, Any]], 
                           config_dict: Dict[str, Any],
                           stats: Optional[Dict[str, Any]] = None,
                           clear_first: bool = True) -> bool:
    """
    Convenience function to export triples to Neo4j.
    
    Args:
        triples: List of triple dictionaries
        config_dict: Configuration dictionary
        stats: Optional graph statistics
        clear_first: Whether to clear existing data
        
    Returns:
        True if successful, False otherwise
    """
    neo4j_config = create_neo4j_config_from_dict(config_dict)
    integration = Neo4jIntegration(neo4j_config)
    
    if not integration.connect():
        return False
    
    try:
        success = integration.import_knowledge_graph(triples, stats, clear_first)
        return success
    finally:
        integration.close()

def query_neo4j_knowledge_graph(query: str, 
                               config_dict: Dict[str, Any],
                               parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute a custom Cypher query on the knowledge graph.
    
    Args:
        query: Cypher query string
        config_dict: Configuration dictionary
        parameters: Optional query parameters
        
    Returns:
        List of query results
    """
    neo4j_config = create_neo4j_config_from_dict(config_dict)
    integration = Neo4jIntegration(neo4j_config)
    
    if not integration.connect():
        return []
    
    try:
        with integration.driver.session(database=neo4j_config.database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    except Exception as e:
        print(f"Query failed: {e}")
        return []
    finally:
        integration.close()
