"""
Enhanced command-line interface with new features.
"""
import argparse
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .main import process_text_in_chunks, main as original_main
from .config import load_config
from .export_utils import export_multiple_formats, GraphFilter
from .batch_processing import batch_process_documents, PerformanceAnalyzer
from .config_profiles import ConfigurationProfiles


def create_enhanced_parser() -> argparse.ArgumentParser:
    """Create enhanced argument parser with new features."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Knowledge Graph Generator with Enhanced Features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m knowledge_graph.cli --input document.txt --output graph.html
  
  # Use a specific configuration profile
  python -m knowledge_graph.cli --input document.txt --profile openai
  
  # Batch process multiple files
  python -m knowledge_graph.cli --batch-input ./documents/ --batch-output ./results/
  
  # Export to multiple formats
  python -m knowledge_graph.cli --input document.txt --export-formats json,csv,graphml
  
  # Filter by specific entities
  python -m knowledge_graph.cli --input document.txt --filter-entities "AI,machine learning"
  
  # Generate configuration profiles
  python -m knowledge_graph.cli --create-profiles ./configs/
        """
    )
    
    # Input/Output options
    io_group = parser.add_argument_group('Input/Output Options')
    io_group.add_argument('--input', type=str, help='Input text file to process')
    io_group.add_argument('--output', type=str, default='knowledge_graph.html', 
                         help='Output HTML file path (default: knowledge_graph.html)')
    io_group.add_argument('--export-formats', type=str, 
                         help='Comma-separated list of export formats (json,csv,graphml,gexf,turtle)')
    io_group.add_argument('--export-base', type=str,
                         help='Base filename for exports (without extension)')
    
    # Batch processing options
    batch_group = parser.add_argument_group('Batch Processing Options')
    batch_group.add_argument('--batch-input', type=str,
                            help='Directory containing input files for batch processing')
    batch_group.add_argument('--batch-output', type=str,
                            help='Directory for batch processing outputs')
    batch_group.add_argument('--file-patterns', type=str, default='*.txt,*.md',
                            help='File patterns for batch processing (default: *.txt,*.md)')
    batch_group.add_argument('--max-workers', type=int, default=2,
                            help='Maximum parallel workers for batch processing (default: 2)')
    
    # Configuration options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument('--config', type=str, default='config.toml',
                             help='Path to configuration file (default: config.toml)')
    config_group.add_argument('--profile', type=str,
                             help='Use predefined configuration profile (openai,claude,ollama,etc.)')
    config_group.add_argument('--create-profiles', type=str,
                             help='Create all configuration profiles in specified directory')
    config_group.add_argument('--list-profiles', action='store_true',
                             help='List available configuration profiles')
    
    # Processing options
    processing_group = parser.add_argument_group('Processing Options')
    processing_group.add_argument('--debug', action='store_true',
                                 help='Enable debug output with raw LLM responses')
    processing_group.add_argument('--no-standardize', action='store_true',
                                 help='Disable entity standardization')
    processing_group.add_argument('--no-inference', action='store_true',
                                 help='Disable relationship inference')
    processing_group.add_argument('--chunk-size', type=int,
                                 help='Override chunk size from config')
    processing_group.add_argument('--temperature', type=float,
                                 help='Override LLM temperature from config')
    
    # Filtering options
    filter_group = parser.add_argument_group('Filtering Options')
    filter_group.add_argument('--filter-entities', type=str,
                             help='Comma-separated list of entities to focus on')
    filter_group.add_argument('--filter-relationships', type=str,
                             help='Comma-separated list of relationships to include')
    filter_group.add_argument('--exclude-entities', type=str,
                             help='Comma-separated list of entities to exclude')
    filter_group.add_argument('--exclude-relationships', type=str,
                             help='Comma-separated list of relationships to exclude')
    filter_group.add_argument('--only-original', action='store_true',
                             help='Include only original (non-inferred) relationships')
    filter_group.add_argument('--only-inferred', action='store_true',
                             help='Include only inferred relationships')
    filter_group.add_argument('--min-confidence', type=float, default=0.0,
                             help='Minimum confidence threshold for relationships')
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis Options')
    analysis_group.add_argument('--analyze-performance', action='store_true',
                               help='Generate performance analysis report')
    analysis_group.add_argument('--subgraph-entity', type=str,
                               help='Extract subgraph around specific entity')
    analysis_group.add_argument('--subgraph-hops', type=int, default=2,
                               help='Maximum hops for subgraph extraction (default: 2)')
    
    # Neo4j options
    neo4j_group = parser.add_argument_group('Neo4j Options')
    neo4j_group.add_argument('--neo4j-export', action='store_true',
                            help='Export to Neo4j database')
    neo4j_group.add_argument('--neo4j-uri', type=str, default='bolt://localhost:7687',
                            help='Neo4j database URI')
    neo4j_group.add_argument('--neo4j-user', type=str, default='neo4j',
                            help='Neo4j username')
    neo4j_group.add_argument('--neo4j-password', type=str,
                            help='Neo4j password')
    neo4j_group.add_argument('--neo4j-clear', action='store_true',
                            help='Clear existing data in Neo4j before import')
    
    # Legacy compatibility
    parser.add_argument('--test', action='store_true',
                       help='Generate a test visualization with sample data')
    
    return parser


def handle_configuration_profiles(args) -> Optional[str]:
    """Handle configuration profile operations."""
    if args.list_profiles:
        profiles = ConfigurationProfiles.get_available_profiles()
        print("Available configuration profiles:")
        for profile in profiles:
            print(f"  - {profile}")
        return None
    
    if args.create_profiles:
        from .config_profiles import create_all_profiles
        create_all_profiles(args.create_profiles)
        return None
    
    if args.profile:
        # Create temporary config file from profile
        temp_config_path = f"temp_config_{args.profile}.toml"
        success = ConfigurationProfiles.create_profile_config(args.profile, temp_config_path)
        if success:
            return temp_config_path
        else:
            print(f"Error: Failed to create configuration for profile '{args.profile}'")
            sys.exit(1)
    
    return args.config


def apply_filtering(triples: List[Dict], args) -> List[Dict]:
    """Apply filtering based on command line arguments."""
    filter_obj = GraphFilter()
    
    # Entity filtering
    if args.filter_entities:
        entities = [e.strip() for e in args.filter_entities.split(',')]
        triples = filter_obj.filter_by_entities(triples, entities, include_mode=True)
    
    if args.exclude_entities:
        entities = [e.strip() for e in args.exclude_entities.split(',')]
        triples = filter_obj.filter_by_entities(triples, entities, include_mode=False)
    
    # Relationship filtering
    if args.filter_relationships:
        relationships = [r.strip() for r in args.filter_relationships.split(',')]
        triples = filter_obj.filter_by_relationships(triples, relationships, include_mode=True)
    
    if args.exclude_relationships:
        relationships = [r.strip() for r in args.exclude_relationships.split(',')]
        triples = filter_obj.filter_by_relationships(triples, relationships, include_mode=False)
    
    # Inference status filtering
    if args.only_original:
        triples = filter_obj.filter_by_inference_status(triples, include_inferred=False, include_original=True)
    elif args.only_inferred:
        triples = filter_obj.filter_by_inference_status(triples, include_inferred=True, include_original=False)
    
    # Confidence filtering
    if args.min_confidence > 0.0:
        triples = filter_obj.filter_by_confidence(triples, min_confidence=args.min_confidence)
    
    # Subgraph extraction
    if args.subgraph_entity:
        triples = filter_obj.get_subgraph_around_entity(triples, args.subgraph_entity, args.subgraph_hops)
    
    return triples


def handle_exports(triples: List[Dict], args) -> None:
    """Handle multiple export formats."""
    if args.export_formats:
        formats = [f.strip() for f in args.export_formats.split(',')]
        base_filename = args.export_base or Path(args.output).stem
        
        export_results = export_multiple_formats(triples, base_filename, formats)
        
        print("\\nExport Results:")
        for format_name, result in export_results.items():
            if result["status"] == "success":
                print(f"  ✓ {format_name.upper()}: {result['file_path']}")
            else:
                print(f"  ✗ {format_name.upper()}: {result['error']}")


def handle_batch_processing(args, config_path) -> None:
    """Handle batch processing of multiple files."""
    file_patterns = [p.strip() for p in args.file_patterns.split(',')]
    
    print(f"Starting batch processing...")
    print(f"Input directory: {args.batch_input}")
    print(f"Output directory: {args.batch_output}")
    print(f"File patterns: {file_patterns}")
    print(f"Max workers: {args.max_workers}")
    
    results = batch_process_documents(
        args.batch_input,
        args.batch_output,
        config_path=config_path,  # Pass the actual config path
        file_patterns=file_patterns,
        max_workers=args.max_workers
    )
    
    print(f"\\nBatch Processing Results:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Total time: {results['total_processing_time']:.2f} seconds")
    
    if args.analyze_performance:
        analyzer = PerformanceAnalyzer()
        report_path = os.path.join(args.batch_output, "detailed_performance_report.md")
        analyzer.generate_performance_report(results, report_path)
        print(f"  Performance report: {report_path}")


def main():
    """Enhanced main function with new features."""
    parser = create_enhanced_parser()
    args = parser.parse_args()
    
    # Handle configuration profiles
    config_path = handle_configuration_profiles(args)
    if config_path is None:  # Profile operations that exit early
        return
    
    # Handle batch processing
    if args.batch_input and args.batch_output:
        handle_batch_processing(args, config_path)
        return
    
    # Handle test mode (legacy compatibility)
    if args.test:
        from .visualization import sample_data_visualization
        sample_data_visualization(args.output)
        print(f"Test visualization saved to: {args.output}")
        return
    
    # Regular processing
    if not args.input:
        print("Error: --input is required for single file processing")
        parser.print_help()
        sys.exit(1)
    
    # Load and modify configuration
    config = load_config(config_path)
    
    # Apply command-line overrides
    if args.chunk_size:
        config["chunking"]["chunk_size"] = args.chunk_size
    if args.temperature:
        config["llm"]["temperature"] = args.temperature
    if args.no_standardize:
        config["standardization"]["enabled"] = False
    if args.no_inference:
        config["inference"]["enabled"] = False
    
    # Neo4j configuration
    if args.neo4j_export:
        config["neo4j"] = {
            "enabled": True,
            "uri": args.neo4j_uri,
            "username": args.neo4j_user,
            "password": args.neo4j_password or input("Neo4j password: "),
            "clear_existing": args.neo4j_clear
        }
    
    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Process text
    print(f"Processing: {args.input}")
    triples = process_text_in_chunks(config, text, debug=args.debug)
    
    if not triples:
        print("Error: No triples extracted from input text")
        sys.exit(1)
    
    # Apply filtering
    original_count = len(triples)
    triples = apply_filtering(triples, args)
    if len(triples) != original_count:
        print(f"Filtering: {original_count} -> {len(triples)} triples")
    
    # Generate visualization
    from .visualization import visualize_knowledge_graph
    stats = visualize_knowledge_graph(triples, args.output, config=config)
    
    print(f"\\nKnowledge Graph Generated:")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Communities: {stats['communities']}")
    print(f"  Visualization: {args.output}")
    
    # Handle multiple exports
    handle_exports(triples, args)
    
    # Neo4j export
    if args.neo4j_export:
        try:
            from .neo4j_integration import export_triples_to_neo4j
            success = export_triples_to_neo4j(triples, config, stats, args.neo4j_clear)
            if success:
                print(f"  ✓ Neo4j export successful")
                print(f"   🌐 You can explore the graph in Neo4j Browser: http://localhost:7474")
                print(f"   📊 Exported: {stats['nodes']} entities, {stats['edges']} relationships")
            else:
                print(f"  ✗ Neo4j export failed. Check your Neo4j connection settings.")
        except ImportError:
            print("  ✗ Neo4j export requires 'neo4j' package: pip install neo4j")
    
    # Clean up temporary config file
    if args.profile and config_path.startswith("temp_config_"):
        try:
            os.remove(config_path)
        except:
            pass


if __name__ == "__main__":
    main()
