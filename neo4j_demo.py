#!/usr/bin/env python3
"""
Neo4j Integration Demo for AI Knowledge Graph Generator
This script demonstrates how to set up and use Neo4j with the knowledge graph generator.
"""

def demo_neo4j_setup():
    """Demonstrate Neo4j setup and usage."""
    print("🚀 AI Knowledge Graph Generator - Neo4j Integration Demo")
    print("=" * 60)
    
    print("\n📋 Prerequisites:")
    print("1. Install Neo4j Desktop or Docker")
    print("2. Start Neo4j database")
    print("3. Install Python neo4j package: pip install neo4j")
    
    print("\n🐳 Quick Setup with Docker:")
    print("docker run \\")
    print("    --name neo4j \\")
    print("    -p7474:7474 -p7687:7687 \\")
    print("    -d \\")
    print("    -e NEO4J_AUTH=neo4j/your_password \\")
    print("    neo4j:latest")
    
    print("\n🎯 Usage Examples:")
    print("\n1. Basic Neo4j Export:")
    print("python3 -m src.knowledge_graph.cli \\")
    print("    --input data/industrial-revolution.txt \\")
    print("    --neo4j-export \\")
    print("    --neo4j-clear")
    
    print("\n2. Custom Neo4j Configuration:")
    print("python3 -m src.knowledge_graph.cli \\")
    print("    --input data/industrial-revolution.txt \\")
    print("    --neo4j-export \\")
    print("    --neo4j-uri bolt://localhost:7687 \\")
    print("    --neo4j-user neo4j \\")
    print("    --neo4j-password your_password")
    
    print("\n3. Export with Multiple Formats + Neo4j:")
    print("python3 -m src.knowledge_graph.cli \\")
    print("    --input data/industrial-revolution.txt \\")
    print("    --export-formats json,csv,graphml \\")
    print("    --neo4j-export")
    
    print("\n🔍 Neo4j Cypher Queries:")
    print("\n# Find all inventors and their inventions")
    print("MATCH (inventor:Entity)-[r:invented]->(invention:Entity)")
    print("RETURN inventor.name, r.relationship, invention.name")
    
    print("\n# Find the most connected entities")
    print("MATCH (n:Entity)")
    print("RETURN n.name, size((n)--()) as connections")
    print("ORDER BY connections DESC LIMIT 10")
    
    print("\n# Find shortest path between two entities")
    print("MATCH path = shortestPath(")
    print("  (start:Entity {name: 'steam engine'})-[*]-(end:Entity {name: 'internet'})")
    print(")")
    print("RETURN path")
    
    print("\n🌐 After Export, open Neo4j Browser:")
    print("http://localhost:7474")
    print("\nLogin: neo4j / your_password")
    
    print("\n✅ Integration Features:")
    print("• Automatic node and relationship creation")
    print("• Community detection labels")
    print("• Metadata preservation")
    print("• Batch processing support")
    print("• Custom query capabilities")
    
    print("\n📚 For detailed documentation, see:")
    print("- NEO4J_INTEGRATION.md")
    print("- src/knowledge_graph/neo4j_integration.py")

if __name__ == "__main__":
    demo_neo4j_setup()
