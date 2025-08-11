# 🚀 Enhanced AI Knowledge Graph Generator

## New Features Added

This fork adds several powerful enhancements to the original AI Knowledge Graph Generator:

### ✨ Key Enhancements

- **🔄 Multi-Format Export**: JSON, CSV, GraphML, GEXF, RDF Turtle
- **⚡ Batch Processing**: Process multiple documents with parallel execution
- **🔍 Advanced Filtering**: Filter by entities, relationships, confidence scores
- **⚙️ Configuration Profiles**: Pre-built configs for different LLM providers and use cases
- **🗄️ Neo4j Integration**: Export to professional graph database with advanced querying
- **📊 Performance Analytics**: Detailed performance reports and metrics
- **💻 Enhanced CLI**: Comprehensive command-line interface with 30+ options

### 🎯 Quick Start

```bash
# Setup enhanced features
python setup_enhanced.py

# Basic usage with enhanced features
python -m knowledge_graph.cli --input document.txt --profile openai --export-formats json,csv

# Batch process multiple documents
python -m knowledge_graph.cli --batch-input ./documents/ --batch-output ./results/

# Advanced filtering and Neo4j export
python -m knowledge_graph.cli --input document.txt --filter-entities "AI,ML" --neo4j-export
```

### 📦 Installation

```bash
# Install enhanced dependencies
pip install neo4j toml lxml

# Run enhanced setup
python setup_enhanced.py
```

### 🔧 Configuration Profiles

Quickly switch between different configurations:

- **openai**: OpenAI GPT-4 optimized
- **claude**: Anthropic Claude optimized  
- **ollama**: Local Ollama models
- **fast_processing**: Speed-optimized
- **high_quality**: Quality-optimized
- **research**: Academic research setup

```bash
# Use a profile
python -m knowledge_graph.cli --input doc.txt --profile research

# Create all profile configs
python -m knowledge_graph.cli --create-profiles ./configs/
```

### 🔄 Export Formats

Export knowledge graphs to multiple formats:

```bash
# Multiple formats
python -m knowledge_graph.cli --input doc.txt --export-formats json,csv,graphml,gexf,turtle

# Programmatic export
from knowledge_graph.export_utils import export_multiple_formats
results = export_multiple_formats(triples, "graph", ["json", "csv"])
```

### ⚡ Batch Processing

Process multiple documents efficiently:

```bash
# Batch process with performance analysis
python -m knowledge_graph.cli \
  --batch-input ./documents/ \
  --batch-output ./results/ \
  --max-workers 4 \
  --analyze-performance
```

### 🔍 Advanced Filtering

Focus on specific parts of your knowledge graph:

```bash
# Entity filtering
python -m knowledge_graph.cli --input doc.txt --filter-entities "AI,machine learning"

# Relationship filtering
python -m knowledge_graph.cli --input doc.txt --filter-relationships "enables,creates"

# Subgraph extraction
python -m knowledge_graph.cli --input doc.txt --subgraph-entity "AI" --subgraph-hops 2

# Confidence filtering
python -m knowledge_graph.cli --input doc.txt --min-confidence 0.8
```

### 🗄️ Neo4j Integration

Export to professional graph database:

```bash
# Basic Neo4j export
python -m knowledge_graph.cli --input doc.txt --neo4j-export

# Custom Neo4j connection
python -m knowledge_graph.cli --input doc.txt --neo4j-export \
  --neo4j-uri "bolt://localhost:7687" \
  --neo4j-user "neo4j" \
  --neo4j-password "password"
```

Query your knowledge graph in Neo4j:

```cypher
// Find most connected entities
MATCH (n:Entity)
RETURN n.name, size((n)--()) as connections
ORDER BY connections DESC LIMIT 10

// Find shortest path between entities
MATCH (start:Entity {name: "AI"}), (end:Entity {name: "robotics"})
MATCH path = shortestPath((start)-[*]-(end))
RETURN path
```

### 📊 Performance Analytics

Get detailed insights into processing performance:

- Processing time per file
- Extraction quality metrics  
- Throughput statistics
- Error analysis
- Batch processing reports

### 💻 Enhanced CLI Options

The enhanced CLI provides 30+ options for complete control:

```bash
python -m knowledge_graph.cli --help

# Example with multiple features
python -m knowledge_graph.cli \
  --input research_paper.txt \
  --profile research \
  --export-formats json,graphml,turtle \
  --filter-entities "AI,machine learning,neural networks" \
  --neo4j-export \
  --analyze-performance
```

### 🔧 Programmatic Usage

All features are available programmatically:

```python
from knowledge_graph.batch_processing import batch_process_documents
from knowledge_graph.export_utils import GraphFilter, export_multiple_formats
from knowledge_graph.neo4j_integration import Neo4jHandler
from knowledge_graph.config_profiles import ConfigurationProfiles

# Batch processing
results = batch_process_documents("./docs", "./output")

# Advanced filtering  
filter_obj = GraphFilter()
filtered = filter_obj.filter_by_entities(triples, ["AI", "ML"])

# Neo4j integration
handler = Neo4jHandler("bolt://localhost:7687", "neo4j", "password")
handler.export_knowledge_graph(triples, "MyGraph")

# Configuration profiles
config = ConfigurationProfiles.get_openai_profile()
```

### 📚 Documentation

- **ENHANCED_FEATURES.md**: Comprehensive feature documentation
- **setup_enhanced.py**: Automated setup script
- Code examples throughout
- Type hints and docstrings

### 🤝 Contributing

These enhancements are designed for easy integration into the main repository:

- ✅ Backward compatible with existing functionality
- ✅ Modular architecture with clear separation
- ✅ Comprehensive error handling
- ✅ Extensive documentation
- ✅ Type hints throughout
- ✅ Optional dependencies don't break existing workflows

### 🎯 Use Cases

Perfect for:

- **Research**: Academic paper analysis with Neo4j integration
- **Business Intelligence**: Batch processing of reports with analytics
- **Content Analysis**: Advanced filtering for focused insights  
- **Production Workflows**: Configuration profiles for different environments
- **Data Science**: Multiple export formats for various analysis tools

### 📈 Performance

- **Batch Processing**: 2-4x faster with parallel processing
- **Memory Efficient**: Streaming processing for large datasets
- **Scalable**: Handles 100+ documents efficiently
- **Robust**: Comprehensive error handling and recovery

---

Ready to supercharge your knowledge graph generation? 🚀

```bash
git clone <your-fork>
cd ai-knowledge-graph
python setup_enhanced.py
python -m knowledge_graph.cli --input example_input.txt --profile openai
```
