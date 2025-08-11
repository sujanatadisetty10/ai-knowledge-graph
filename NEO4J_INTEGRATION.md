# 🚀 Neo4j Integration Guide for AI Knowledge Graph Generator

This guide shows you how to integrate your AI Knowledge Graph Generator with Neo4j, a powerful graph database that provides advanced querying, visualization, and analytics capabilities.

## 🎯 Why Neo4j Integration?

### **Benefits of Neo4j Integration:**
- **Professional Graph Database:** Persistent storage with ACID compliance
- **Advanced Querying:** Powerful Cypher query language for complex graph operations
- **Built-in Visualization:** Neo4j Browser provides interactive graph exploration
- **Scalability:** Handle millions of nodes and relationships efficiently
- **Analytics:** Built-in graph algorithms for centrality, community detection, pathfinding
- **Multi-user Access:** Share and collaborate on knowledge graphs
- **API Access:** REST and Bolt protocols for integration with other tools

## 📋 Prerequisites

### 1. Install Neo4j
Choose one of these options:

#### Option A: Neo4j Desktop (Recommended for beginners)
```bash
# Download from: https://neo4j.com/download/
# - Easy GUI management
# - Local development environment
# - Built-in browser and tools
```

#### Option B: Neo4j Community Server
```bash
# On macOS with Homebrew:
brew install neo4j

# On Ubuntu/Debian:
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# On Windows:
# Download from: https://neo4j.com/download-center/#community
```

#### Option C: Docker (For containerized deployment)
```bash
# Run Neo4j in Docker
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 2. Install Python Dependencies
```bash
# Install Neo4j Python driver
pip install neo4j

# Or update requirements
pip install -r requirements.txt
```

### 3. Start Neo4j and Set Password
```bash
# If using Neo4j Community Server:
sudo systemctl start neo4j

# If using Docker:
docker start neo4j

# Open Neo4j Browser: http://localhost:7474
# Default credentials: neo4j/neo4j
# You'll be prompted to change the password
```

## ⚙️ Configuration

### 1. Update Configuration File
Create or update your `config-neo4j.toml`:

```toml
[llm]
model = "gemma3"
api_key = "sk-1234"
base_url = "http://localhost:11434/v1/chat/completions"
max_tokens = 8192
temperature = 0.2

[chunking]
chunk_size = 100
overlap = 20

[standardization]
enabled = true
use_llm_for_entities = true

[inference]
enabled = true
use_llm_for_inference = true
apply_transitive = true

[visualization]
edge_smooth = false

# Neo4j Configuration
[neo4j]
uri = "bolt://localhost:7687"      # Neo4j connection URI
username = "neo4j"                 # Your Neo4j username
password = "your_password_here"    # Change this to your actual password!
database = "neo4j"                 # Database name (default: neo4j)
max_retry_attempts = 3
retry_delay = 1.0
```

### 2. Verify Neo4j Connection
Test your connection:

```bash
# Test connection with example script
python neo4j_example.py --action query --query "RETURN 'Hello Neo4j!' as message"
```

## 🚀 Usage Examples

### 1. Basic Import and Export

#### Import Knowledge Graph to Neo4j
```bash
# Process text file and export to Neo4j
python generate-graph.py \
    --input data/industrial-revolution.txt \
    --output industrial-revolution.html \
    --config config-neo4j.toml \
    --export-neo4j \
    --neo4j-clear

# This will:
# 1. Process the text with LLM
# 2. Extract entities and relationships
# 3. Create HTML visualization
# 4. Export everything to Neo4j
# 5. Clear existing Neo4j data first (--neo4j-clear)
```

#### Export from Neo4j to JSON
```bash
# Export Neo4j graph back to JSON
python neo4j_example.py \
    --config config-neo4j.toml \
    --action export
```

### 2. Advanced Querying

#### Run Demo Queries
```bash
# Run comprehensive demonstration
python neo4j_example.py \
    --config config-neo4j.toml \
    --action demo \
    --input data/industrial-revolution.txt
```

#### Custom Cypher Queries
```bash
# Find most connected entities
python neo4j_example.py \
    --config config-neo4j.toml \
    --action query \
    --query "MATCH (e:Entity) RETURN e.name, e.relationship_count ORDER BY e.relationship_count DESC LIMIT 10"

# Find shortest path between two entities
python neo4j_example.py \
    --config config-neo4j.toml \
    --action query \
    --query "MATCH path = shortestPath((a:Entity {name: 'james watt'})-[*..5]-(b:Entity {name: 'steam engine'})) RETURN path"

# Find all Technology entities
python neo4j_example.py \
    --config config-neo4j.toml \
    --action query \
    --query "MATCH (e:Entity {type: 'Technology'}) RETURN e.name, e.relationship_count ORDER BY e.relationship_count DESC"
```

### 3. Integration in Python Code

```python
from src.knowledge_graph.neo4j_integration import Neo4jIntegration, Neo4jConfig
from src.knowledge_graph.config import load_config

# Load configuration
config = load_config("config-neo4j.toml")

# Create Neo4j integration
neo4j_config = Neo4jConfig(
    uri=config["neo4j"]["uri"],
    username=config["neo4j"]["username"],
    password=config["neo4j"]["password"],
    database=config["neo4j"]["database"]
)

integration = Neo4jIntegration(neo4j_config)

if integration.connect():
    # Get statistics
    entity_stats = integration.get_entity_statistics()
    print(f"Total entities: {entity_stats['total_entities']}")
    
    # Find similar entities
    similar = integration.find_similar_entities("steam engine", similarity_threshold=0.2)
    for entity in similar:
        print(f"Similar to steam engine: {entity['entity_name']} (similarity: {entity['similarity']:.3f})")
    
    # Get entity neighborhood
    neighborhood = integration.get_entity_neighborhood("james watt", depth=2)
    print(f"James Watt has {neighborhood['neighbor_count']} neighbors within 2 steps")
    
    integration.close()
```

## 🔍 Neo4j Browser Exploration

### 1. Open Neo4j Browser
- Navigate to: http://localhost:7474
- Login with your credentials

### 2. Basic Cypher Queries

```cypher
// See all entity types
MATCH (e:Entity) 
RETURN DISTINCT e.type, count(*) as count 
ORDER BY count DESC

// Visualize a subgraph around a specific entity
MATCH (center:Entity {name: "steam engine"})-[r:RELATES_TO*1..2]-(connected:Entity)
RETURN center, r, connected
LIMIT 50

// Find the most important entities (highest betweenness centrality)
MATCH (e:Entity)
RETURN e.name, e.type, e.relationship_count
ORDER BY e.relationship_count DESC
LIMIT 20

// Find entities that bridge different communities
MATCH (a:Entity)-[r1:RELATES_TO]-(bridge:Entity)-[r2:RELATES_TO]-(b:Entity)
WHERE a.type <> b.type AND a <> b
RETURN bridge.name, bridge.type, count(*) as bridge_connections
ORDER BY bridge_connections DESC
LIMIT 10

// Find relationship patterns
MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
RETURN r.predicate, count(*) as frequency, 
       collect(DISTINCT e1.type) as subject_types,
       collect(DISTINCT e2.type) as object_types
ORDER BY frequency DESC
LIMIT 15

// Find transitive relationships
MATCH (a:Entity)-[r1:RELATES_TO]->(b:Entity)-[r2:RELATES_TO]->(c:Entity)
WHERE a <> c
RETURN a.name, r1.predicate, b.name, r2.predicate, c.name
LIMIT 20
```

### 3. Advanced Analytics

```cypher
// PageRank-like analysis (most referenced entities)
MATCH (e:Entity)
OPTIONAL MATCH (e)<-[r:RELATES_TO]-()
RETURN e.name, e.type, count(r) as incoming_references
ORDER BY incoming_references DESC
LIMIT 15

// Community detection (entities that share many connections)
MATCH (e1:Entity)-[:RELATES_TO]-(shared:Entity)-[:RELATES_TO]-(e2:Entity)
WHERE e1 < e2
RETURN e1.name, e2.name, count(shared) as shared_connections
ORDER BY shared_connections DESC
LIMIT 20

// Find entities with unique relationship types
MATCH (e:Entity)-[r:RELATES_TO]-()
WITH e, collect(DISTINCT r.predicate) as predicates
RETURN e.name, e.type, size(predicates) as unique_relationships, predicates
ORDER BY unique_relationships DESC
LIMIT 15
```

## 🛠️ Advanced Features

### 1. Batch Processing
```python
# Process multiple files
files = ["doc1.txt", "doc2.txt", "doc3.txt"]
all_triples = []

for file in files:
    with open(file, 'r') as f:
        text = f.read()
    triples = process_text_in_chunks(config, text)
    all_triples.extend(triples)

# Export all to Neo4j
export_triples_to_neo4j(all_triples, config)
```

### 2. Incremental Updates
```python
# Add new data without clearing existing
export_triples_to_neo4j(new_triples, config, clear_first=False)
```

### 3. Data Validation
```python
# Validate data before export
def validate_triples(triples):
    valid = []
    for triple in triples:
        if (triple.get("subject") and 
            triple.get("predicate") and 
            triple.get("object") and
            triple["subject"] != triple["object"]):
            valid.append(triple)
    return valid

validated_triples = validate_triples(raw_triples)
export_triples_to_neo4j(validated_triples, config)
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Connection Failed
```bash
# Check if Neo4j is running
sudo systemctl status neo4j

# Check ports
netstat -tlnp | grep :7687
netstat -tlnp | grep :7474

# Test connection
telnet localhost 7687
```

#### 2. Authentication Error
```python
# Verify credentials in Neo4j Browser first
# Update config-neo4j.toml with correct password
# Check if password was changed from default
```

#### 3. Import Errors
```bash
# Check Neo4j logs
tail -f /var/log/neo4j/neo4j.log

# Verify data format
python -c "
import json
with open('kg-run.json') as f:
    data = json.load(f)
    print(f'Loaded {len(data)} triples')
    print('Sample:', data[0] if data else 'No data')
"
```

#### 4. Performance Issues
```cypher
// Check database size
MATCH (n) RETURN count(n) as nodes;
MATCH ()-[r]->() RETURN count(r) as relationships;

// Create indexes for better performance
CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX relationship_predicate_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.predicate);
```

## 📊 Performance Guidelines

### Recommended Limits
- **Entities:** Neo4j can handle millions, but 1,000-10,000 is good for exploration
- **Relationships:** Up to 100,000 relationships for interactive queries
- **Query Response:** Limit results to 100-1,000 nodes for visualization

### Optimization Tips
1. **Use Indexes:** Create indexes on frequently queried properties
2. **Limit Results:** Always use LIMIT in exploratory queries
3. **Use Labels:** Properly label nodes for efficient filtering
4. **Batch Operations:** Import data in batches of 1,000-10,000 records

## 🌟 Next Steps

1. **Explore Graph Algorithms:** Use Neo4j's Graph Data Science library
2. **Create Custom Visualizations:** Build web apps with Neo4j drivers
3. **Set up Monitoring:** Use Neo4j metrics for performance tracking
4. **Scale Up:** Consider Neo4j Enterprise for production workloads
5. **Integrate with Other Tools:** Connect to Jupyter, Tableau, or other analytics platforms

## 📚 Resources

- **Neo4j Documentation:** https://neo4j.com/docs/
- **Cypher Query Language:** https://neo4j.com/docs/cypher-manual/
- **Graph Data Science:** https://neo4j.com/docs/graph-data-science/
- **Neo4j Browser Guide:** https://neo4j.com/docs/browser-manual/
- **Python Driver Documentation:** https://neo4j.com/docs/python-manual/

This integration transforms your AI Knowledge Graph Generator into a professional-grade knowledge management system with the power of a dedicated graph database! 🚀
