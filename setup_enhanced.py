#!/usr/bin/env python3
"""
Quick setup script for AI Knowledge Graph Generator with enhanced features.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing Dependencies")
    print("=" * 50)
    
    # Core dependencies
    deps = [
        "pip install -r requirements.txt",
        "pip install neo4j toml lxml",  # Enhanced features
    ]
    
    for dep in deps:
        if not run_command(dep, f"Installing {dep.split()[-1]}"):
            return False
    
    return True


def create_config_profiles():
    """Create configuration profiles."""
    print("\n⚙️ Creating Configuration Profiles")
    print("=" * 50)
    
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)
    
    try:
        from src.knowledge_graph.config_profiles import create_all_profiles
        create_all_profiles(str(config_dir))
        print("✅ Configuration profiles created in ./configs/")
        return True
    except Exception as e:
        print(f"❌ Failed to create profiles: {e}")
        return False


def setup_neo4j():
    """Check Neo4j setup and provide instructions."""
    print("\n🗄️ Neo4j Setup (Optional)")
    print("=" * 50)
    
    # Check if Neo4j is running
    try:
        import neo4j
        print("✅ Neo4j Python driver installed")
        
        # Try to connect to default Neo4j instance
        try:
            driver = neo4j.GraphDatabase.driver("bolt://localhost:7687", 
                                               auth=("neo4j", "password"))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            print("✅ Neo4j database connection successful")
            return True
        except Exception:
            print("⚠️  Neo4j database not accessible at bolt://localhost:7687")
            print("   To set up Neo4j:")
            print("   1. Download Neo4j Desktop from https://neo4j.com/download/")
            print("   2. Create a new database with password 'password'")
            print("   3. Start the database")
            print("   4. Or use Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j")
            return False
            
    except ImportError:
        print("❌ Neo4j driver not installed")
        return False


def check_ollama():
    """Check if Ollama is available for local models."""
    print("\n🤖 Ollama Setup (Optional)")
    print("=" * 50)
    
    if shutil.which("ollama"):
        print("✅ Ollama CLI found")
        
        # Check if Ollama service is running
        try:
            result = subprocess.run("ollama list", shell=True, 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Ollama service is running")
                models = [line.split()[0] for line in result.stdout.split('\n')[1:] if line.strip()]
                if models:
                    print(f"   Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                else:
                    print("   No models installed. Run: ollama pull llama3.2")
                return True
            else:
                print("⚠️  Ollama service not running. Start with: ollama serve")
                return False
        except subprocess.TimeoutExpired:
            print("⚠️  Ollama service not responding")
            return False
    else:
        print("⚠️  Ollama not found")
        print("   Install from: https://ollama.ai/")
        return False


def create_example_configs():
    """Create example configuration files."""
    print("\n📄 Creating Example Files")
    print("=" * 50)
    
    # Create example input file
    example_text = '''
Artificial Intelligence (AI) has revolutionized many industries. Machine learning, a subset of AI, 
enables computers to learn from data without explicit programming. Deep learning, which uses neural 
networks, has particularly advanced computer vision and natural language processing. Companies like 
Google, Microsoft, and OpenAI have made significant contributions to AI research and development.
'''
    
    with open("example_input.txt", "w") as f:
        f.write(example_text.strip())
    print("✅ Created example_input.txt")
    
    # Create example batch directory
    batch_dir = Path("example_batch")
    batch_dir.mkdir(exist_ok=True)
    
    for i in range(3):
        with open(batch_dir / f"document_{i+1}.txt", "w") as f:
            f.write(f"This is example document {i+1}. " + example_text)
    print(f"✅ Created example batch directory with 3 documents")
    
    return True


def print_usage_examples():
    """Print usage examples."""
    print("\n🚀 Quick Start Examples")
    print("=" * 50)
    
    examples = [
        ("Basic Usage", "python generate-graph.py --input example_input.txt"),
        ("With OpenAI Profile", "python -m knowledge_graph.cli --input example_input.txt --profile openai"),
        ("Multiple Export Formats", "python -m knowledge_graph.cli --input example_input.txt --export-formats json,csv,graphml"),
        ("Batch Processing", "python -m knowledge_graph.cli --batch-input example_batch/ --batch-output results/"),
        ("With Neo4j Export", "python -m knowledge_graph.cli --input example_input.txt --neo4j-export"),
        ("Advanced Filtering", "python -m knowledge_graph.cli --input example_input.txt --filter-entities 'AI,machine learning'"),
    ]
    
    for name, command in examples:
        print(f"\n{name}:")
        print(f"  {command}")
    
    print(f"\n📚 For more examples, see ENHANCED_FEATURES.md")


def main():
    """Main setup function."""
    print("🧠 AI Knowledge Graph Generator - Enhanced Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create configuration profiles
    if not create_config_profiles():
        print("⚠️  Configuration profiles not created (optional)")
    
    # Check optional services
    setup_neo4j()
    check_ollama()
    
    # Create example files
    create_example_configs()
    
    # Print usage examples
    print_usage_examples()
    
    print(f"\n✅ Setup Complete!")
    print(f"🎯 Try the basic example: python generate-graph.py --input example_input.txt")
    print(f"📖 Read ENHANCED_FEATURES.md for comprehensive documentation")


if __name__ == "__main__":
    main()
