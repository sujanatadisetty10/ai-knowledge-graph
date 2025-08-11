# Enhanced Features Documentation

## 🚀 New Features Added

This document describes the enhanced features added to the AI Knowledge Graph Generator that make it more powerful and production-ready.

## 📋 Table of Contents

1. [Enhanced Export Capabilities](#enhanced-export-capabilities)
2. [Batch Processing](#batch-processing)
3. [Advanced Filtering](#advanced-filtering)
4. [Configuration Profiles](#configuration-profiles)
5. [Neo4j Integration](#neo4j-integration)
6. [Performance Analytics](#performance-analytics)
7. [Enhanced CLI](#enhanced-cli)

---

## 🔄 Enhanced Export Capabilities

### Multiple Export Formats

The system now supports exporting knowledge graphs to multiple formats:

- **JSON**: Structured data with metadata
- **CSV**: Tabular format for spreadsheet analysis
- **GraphML**: Standard graph format for analysis tools
- **GEXF**: Format for Gephi visualization
- **RDF Turtle**: Semantic web format

### Usage Examples

```bash
# Export to multiple formats
python generate-graph.py --input document.txt --export-formats json,csv,graphml

# Export with custom base filename
python generate-graph.py --input document.txt --export-formats json,gexf --export-base my_graph
```

### Programmatic Usage

```python
from knowledge_graph.export_utils import export_multiple_formats

# Export to multiple formats
results = export_multiple_formats(
    triples, 
    "knowledge_graph", 
    formats=['json', 'csv', 'graphml']
)
```

---

## 🔄 Batch Processing

### Process Multiple Documents

Handle multiple documents efficiently with parallel processing:

```bash
# Batch process all .txt and .md files in a directory
python -m knowledge_graph.cli --batch-input ./documents/ --batch-output ./results/

# Control parallelism
python -m knowledge_graph.cli --batch-input ./docs/ --batch-output ./output/ --max-workers 4

# Specific file patterns
python -m knowledge_graph.cli --batch-input ./docs/ --batch-output ./output/ --file-patterns "*.pdf,*.docx"
```

### Programmatic Batch Processing

```python
from knowledge_graph.batch_processing import batch_process_documents

results = batch_process_documents(
    input_dir="./documents",
    output_dir="./results",
    file_patterns=["*.txt", "*.md"],
    max_workers=3
)

print(f"Processed {results['successful']}/{results['total_files']} files")
```

### Performance Analysis

Automatically generated performance reports include:
- Processing time per file
- Extraction quality metrics
- Throughput statistics
- Error analysis

---

## 🔍 Advanced Filtering

### Entity-Based Filtering

Focus on specific entities or exclude unwanted ones:

```bash
# Include only specific entities
python -m knowledge_graph.cli --input document.txt --filter-entities "AI,machine learning,neural networks"

# Exclude specific entities
python -m knowledge_graph.cli --input document.txt --exclude-entities "irrelevant,noise"
```

### Relationship Filtering

Filter by relationship types:

```bash
# Include only specific relationships
python -m knowledge_graph.cli --input document.txt --filter-relationships "enables,creates,improves"

# Exclude relationships
python -m knowledge_graph.cli --input document.txt --exclude-relationships "mentions,references"
```

### Inference Status Filtering

```bash
# Only original relationships
python -m knowledge_graph.cli --input document.txt --only-original

# Only inferred relationships
python -m knowledge_graph.cli --input document.txt --only-inferred

# Minimum confidence threshold
python -m knowledge_graph.cli --input document.txt --min-confidence 0.8
```

### Subgraph Extraction

Extract subgraphs around specific entities:

```bash
# Get 2-hop neighborhood around "artificial intelligence"
python -m knowledge_graph.cli --input document.txt --subgraph-entity "artificial intelligence" --subgraph-hops 2
```

### Programmatic Filtering

```python
from knowledge_graph.export_utils import GraphFilter

filter_obj = GraphFilter()

# Filter by entities
filtered_triples = filter_obj.filter_by_entities(
    triples, 
    ["AI", "machine learning"], 
    include_mode=True
)

# Extract subgraph
subgraph = filter_obj.get_subgraph_around_entity(
    triples, 
    "artificial intelligence", 
    max_hops=2
)
```

---

## ⚙️ Configuration Profiles

### Pre-built Profiles

Quick setup for different scenarios:

```bash
# Use OpenAI profile
python -m knowledge_graph.cli --input document.txt --profile openai

# Use Ollama with specific model
python -m knowledge_graph.cli --input document.txt --profile ollama

# High-quality processing
python -m knowledge_graph.cli --input document.txt --profile high_quality

# Fast processing
python -m knowledge_graph.cli --input document.txt --profile fast_processing

# Research-oriented setup
python -m knowledge_graph.cli --input document.txt --profile research
```

### Available Profiles

- **openai**: OpenAI GPT-4 optimized
- **claude**: Anthropic Claude optimized
- **ollama**: Local Ollama models
- **fast_processing**: Speed-optimized
- **high_quality**: Quality-optimized
- **minimal**: Minimal processing
- **research**: Academic research optimized

### Create Profile Configurations

```bash
# List available profiles
python -m knowledge_graph.cli --list-profiles

# Create all profile configs
python -m knowledge_graph.cli --create-profiles ./configs/

# Create specific profile
python -c "from knowledge_graph.config_profiles import ConfigurationProfiles; ConfigurationProfiles.create_profile_config('openai', 'openai_config.toml')"
```

### Custom Profile Creation

```python
from knowledge_graph.config_profiles import ConfigurationProfiles

# Create custom profile
custom_config = ConfigurationProfiles.get_openai_profile()
custom_config["chunking"]["chunk_size"] = 300
custom_config["llm"]["temperature"] = 0.1

# Save custom profile
with open("custom_config.toml", "w") as f:
    toml.dump(custom_config, f)
```

---

## 🗄️ Neo4j Integration

### Basic Neo4j Export

```bash
# Export to Neo4j with default settings
python -m knowledge_graph.cli --input document.txt --neo4j-export

# Custom Neo4j connection
python -m knowledge_graph.cli --input document.txt --neo4j-export \
  --neo4j-uri "bolt://localhost:7687" \
  --neo4j-user "neo4j" \
  --neo4j-password "mypassword"

# Clear existing data before import
python -m knowledge_graph.cli --input document.txt --neo4j-export --neo4j-clear
```

### Programmatic Neo4j Usage

```python
from knowledge_graph.neo4j_integration import Neo4jHandler

# Connect to Neo4j
handler = Neo4jHandler(
    uri="bolt://localhost:7687",
    username="neo4j", 
    password="password"
)

# Export knowledge graph
stats = handler.export_knowledge_graph(triples, "MyKnowledgeGraph")

# Query the graph
results = handler.query_graph(
    "MATCH (n:Entity)-[r:RELATES]->(m:Entity) RETURN n.name, r.type, m.name LIMIT 10"
)

# Find shortest path
path = handler.find_shortest_path("AI", "robotics", "MyKnowledgeGraph")

# Get statistics
stats = handler.get_graph_statistics("MyKnowledgeGraph")

handler.close()
```

### Advanced Neo4j Queries

The system provides query templates for common operations:

```python
from knowledge_graph.neo4j_integration import NEO4J_QUERY_TEMPLATES

# Get all entities
entities_query = NEO4J_QUERY_TEMPLATES["find_all_entities"]

# Get entity relationships
rel_query = NEO4J_QUERY_TEMPLATES["entity_relationships"]

# Most influential entities
influence_query = NEO4J_QUERY_TEMPLATES["most_influential_entities"]
```

---

## 📊 Performance Analytics

### Automated Performance Reports

Batch processing automatically generates detailed performance reports:

```markdown
# Batch Processing Performance Report
Generated: 2025-01-31T10:30:00

## Summary
- Total files processed: 25
- Successful: 23
- Failed: 2
- Success rate: 92.0%

## Performance Metrics
- Average processing time: 45.2 seconds
- Fastest file: 12.3 seconds
- Slowest file: 156.7 seconds
- Total processing time: 1,130 seconds

## Extraction Quality
- Average triples per file: 127.5
- Total triples extracted: 2,933
- Average entities per file: 45.2
- Average relationships per file: 23.1

## Throughput
- Files per hour: 79.6
- Triples per minute: 155.8
```

### Custom Performance Analysis

```python
from knowledge_graph.batch_processing import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Analyze batch results
analysis = analyzer.analyze_batch_results(batch_results)

# Generate custom report
report = analyzer.generate_performance_report(
    batch_results, 
    "custom_performance_report.md"
)
```

---

## 💻 Enhanced CLI

### New Command-Line Features

The enhanced CLI provides a comprehensive interface:

```bash
# Show all available options
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

### CLI Option Categories

#### Input/Output Options
- `--input`: Input text file
- `--output`: Output HTML file
- `--export-formats`: Multiple export formats
- `--export-base`: Base filename for exports

#### Batch Processing Options
- `--batch-input`: Input directory
- `--batch-output`: Output directory
- `--file-patterns`: File patterns to process
- `--max-workers`: Parallel processing workers

#### Configuration Options
- `--config`: Configuration file path
- `--profile`: Use predefined profile
- `--create-profiles`: Create all profiles
- `--list-profiles`: List available profiles

#### Processing Options
- `--debug`: Enable debug output
- `--no-standardize`: Disable standardization
- `--no-inference`: Disable inference
- `--chunk-size`: Override chunk size
- `--temperature`: Override LLM temperature

#### Filtering Options
- `--filter-entities`: Include specific entities
- `--filter-relationships`: Include specific relationships
- `--exclude-entities`: Exclude entities
- `--exclude-relationships`: Exclude relationships
- `--only-original`: Only original relationships
- `--only-inferred`: Only inferred relationships
- `--min-confidence`: Minimum confidence threshold

#### Analysis Options
- `--analyze-performance`: Generate performance analysis
- `--subgraph-entity`: Extract entity subgraph
- `--subgraph-hops`: Subgraph hop distance

#### Neo4j Options
- `--neo4j-export`: Export to Neo4j
- `--neo4j-uri`: Neo4j database URI
- `--neo4j-user`: Neo4j username
- `--neo4j-password`: Neo4j password
- `--neo4j-clear`: Clear existing data

---

## 🔧 Installation and Setup

### Install Enhanced Dependencies

```bash
# Install additional dependencies
pip install neo4j toml lxml

# Or install all requirements
pip install -r requirements.txt
```

### Quick Start with Enhanced Features

```bash
# 1. Create configuration profiles
python -m knowledge_graph.cli --create-profiles ./configs/

# 2. Process a document with enhanced features
python -m knowledge_graph.cli \
  --input document.txt \
  --profile openai \
  --export-formats json,csv,graphml \
  --neo4j-export

# 3. Batch process multiple documents
python -m knowledge_graph.cli \
  --batch-input ./documents/ \
  --batch-output ./results/ \
  --profile fast_processing \
  --analyze-performance
```

### Environment Variables

Set up environment variables for API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

---

## 🤝 Contributing to GitHub

These enhanced features are ready for contribution to the GitHub repository. Key improvements include:

### Code Quality
- Comprehensive error handling
- Type hints throughout
- Extensive documentation
- Modular architecture

### New Capabilities
- Multi-format export system
- Batch processing with analytics
- Advanced filtering options
- Configuration profile system
- Neo4j database integration
- Enhanced command-line interface

### Backward Compatibility
- All existing functionality preserved
- Enhanced CLI falls back to basic CLI if dependencies missing
- Optional features don't break existing workflows

### Testing Ready
- Modular design enables easy unit testing
- Example usage throughout documentation
- Error cases handled gracefully

These features significantly expand the project's capabilities while maintaining its ease of use and reliability.
