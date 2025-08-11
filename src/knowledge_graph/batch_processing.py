"""
Batch processing capabilities for handling multiple documents.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from .main import process_text_in_chunks
from .config import load_config
from .export_utils import export_multiple_formats


class BatchProcessor:
    """Handles batch processing of multiple documents."""
    
    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize batch processor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
    def process_directory(self, input_dir: str, output_dir: str, 
                         file_patterns: List[str] = None,
                         max_workers: int = 2) -> Dict[str, Any]:
        """
        Process all files in a directory.
        
        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files
            file_patterns: List of file patterns to match (e.g., ['*.txt', '*.md'])
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with processing results
        """
        if file_patterns is None:
            file_patterns = ['*.txt', '*.md']
        
        # Find input files
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        input_files = []
        for pattern in file_patterns:
            input_files.extend(input_path.glob(pattern))
        
        if not input_files:
            self.logger.warning(f"No files found matching patterns {file_patterns} in {input_dir}")
            return {"status": "no_files", "files_processed": 0}
        
        self.logger.info(f"Found {len(input_files)} files to process")
        
        # Process files
        results = {}
        total_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {}
            for input_file in input_files:
                output_base = output_path / input_file.stem
                future = executor.submit(self._process_single_file, 
                                       str(input_file), str(output_base))
                future_to_file[future] = input_file
            
            # Collect results
            completed = 0
            for future in as_completed(future_to_file):
                input_file = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[str(input_file)] = result
                    self.logger.info(f"Processed {completed}/{len(input_files)}: {input_file.name}")
                except Exception as e:
                    self.logger.error(f"Error processing {input_file}: {e}")
                    results[str(input_file)] = {"status": "error", "error": str(e)}
        
        total_time = time.time() - total_start_time
        
        # Summary statistics
        successful = len([r for r in results.values() if r.get("status") == "success"])
        failed = len(results) - successful
        
        summary = {
            "status": "completed",
            "total_files": len(input_files),
            "successful": successful,
            "failed": failed,
            "total_processing_time": total_time,
            "average_time_per_file": total_time / len(input_files) if input_files else 0,
            "results": results
        }
        
        # Save batch summary
        summary_file = output_path / "batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Batch processing completed: {successful}/{len(input_files)} successful")
        return summary
    
    def _process_single_file(self, input_file: str, output_base: str) -> Dict[str, Any]:
        """
        Process a single file.
        
        Args:
            input_file: Path to input file
            output_base: Base path for output files (without extension)
            
        Returns:
            Processing result dictionary
        """
        start_time = time.time()
        
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                return {"status": "error", "error": "Empty file"}
            
            # Process with knowledge graph generator
            triples = process_text_in_chunks(self.config, text)
            
            if not triples:
                return {"status": "error", "error": "No triples extracted"}
            
            # Export to multiple formats
            export_results = export_multiple_formats(
                triples, 
                output_base, 
                formats=['json', 'csv', 'html']
            )
            
            processing_time = time.time() - start_time
            
            return {
                "status": "success",
                "input_file": input_file,
                "processing_time": processing_time,
                "triples_extracted": len(triples),
                "exports": export_results,
                "statistics": {
                    "total_triples": len(triples),
                    "inferred_triples": len([t for t in triples if t.get("inferred", False)]),
                    "unique_entities": len(set(
                        [t.get("subject") for t in triples] + 
                        [t.get("object") for t in triples]
                    )),
                    "unique_relationships": len(set([t.get("predicate") for t in triples]))
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def process_file_list(self, file_list: List[str], output_dir: str, 
                         max_workers: int = 2) -> Dict[str, Any]:
        """
        Process a specific list of files.
        
        Args:
            file_list: List of file paths to process
            output_dir: Directory for output files
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with processing results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        total_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}
            for input_file in file_list:
                file_path = Path(input_file)
                output_base = output_path / file_path.stem
                future = executor.submit(self._process_single_file, 
                                       input_file, str(output_base))
                future_to_file[future] = input_file
            
            # Collect results
            for future in as_completed(future_to_file):
                input_file = future_to_file[future]
                try:
                    result = future.result()
                    results[input_file] = result
                except Exception as e:
                    results[input_file] = {"status": "error", "error": str(e)}
        
        total_time = time.time() - total_start_time
        successful = len([r for r in results.values() if r.get("status") == "success"])
        
        return {
            "status": "completed",
            "total_files": len(file_list),
            "successful": successful,
            "failed": len(file_list) - successful,
            "total_processing_time": total_time,
            "results": results
        }


class PerformanceAnalyzer:
    """Analyzes performance metrics across batch processing."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_batch_results(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance metrics from batch processing results.
        
        Args:
            batch_results: Results from batch processing
            
        Returns:
            Performance analysis dictionary
        """
        results = batch_results.get("results", {})
        successful_results = [r for r in results.values() if r.get("status") == "success"]
        
        if not successful_results:
            return {"status": "no_successful_results"}
        
        # Extract metrics
        processing_times = [r["processing_time"] for r in successful_results]
        triples_counts = [r["triples_extracted"] for r in successful_results]
        entity_counts = [r["statistics"]["unique_entities"] for r in successful_results]
        relationship_counts = [r["statistics"]["unique_relationships"] for r in successful_results]
        
        analysis = {
            "performance_metrics": {
                "avg_processing_time": sum(processing_times) / len(processing_times),
                "min_processing_time": min(processing_times),
                "max_processing_time": max(processing_times),
                "total_processing_time": sum(processing_times)
            },
            "extraction_metrics": {
                "avg_triples_per_file": sum(triples_counts) / len(triples_counts),
                "min_triples_per_file": min(triples_counts),
                "max_triples_per_file": max(triples_counts),
                "total_triples": sum(triples_counts),
                "avg_entities_per_file": sum(entity_counts) / len(entity_counts),
                "avg_relationships_per_file": sum(relationship_counts) / len(relationship_counts)
            },
            "throughput_metrics": {
                "files_per_hour": len(successful_results) / (sum(processing_times) / 3600),
                "triples_per_minute": sum(triples_counts) / (sum(processing_times) / 60)
            }
        }
        
        return analysis
    
    def generate_performance_report(self, batch_results: Dict[str, Any], 
                                  output_path: str = None) -> str:
        """
        Generate a detailed performance report.
        
        Args:
            batch_results: Results from batch processing
            output_path: Optional path to save the report
            
        Returns:
            Report content as string
        """
        analysis = self.analyze_batch_results(batch_results)
        
        if analysis.get("status") == "no_successful_results":
            return "No successful results to analyze."
        
        report = f"""
# Batch Processing Performance Report
Generated: {datetime.now().isoformat()}

## Summary
- Total files processed: {batch_results.get('total_files', 0)}
- Successful: {batch_results.get('successful', 0)}
- Failed: {batch_results.get('failed', 0)}
- Success rate: {(batch_results.get('successful', 0) / max(batch_results.get('total_files', 1), 1)) * 100:.1f}%

## Performance Metrics
- Average processing time: {analysis['performance_metrics']['avg_processing_time']:.2f} seconds
- Fastest file: {analysis['performance_metrics']['min_processing_time']:.2f} seconds
- Slowest file: {analysis['performance_metrics']['max_processing_time']:.2f} seconds
- Total processing time: {analysis['performance_metrics']['total_processing_time']:.2f} seconds

## Extraction Quality
- Average triples per file: {analysis['extraction_metrics']['avg_triples_per_file']:.1f}
- Total triples extracted: {analysis['extraction_metrics']['total_triples']}
- Average entities per file: {analysis['extraction_metrics']['avg_entities_per_file']:.1f}
- Average relationships per file: {analysis['extraction_metrics']['avg_relationships_per_file']:.1f}

## Throughput
- Files per hour: {analysis['throughput_metrics']['files_per_hour']:.1f}
- Triples per minute: {analysis['throughput_metrics']['triples_per_minute']:.1f}

## File-by-File Results
"""
        
        results = batch_results.get("results", {})
        for file_path, result in results.items():
            if result.get("status") == "success":
                report += f"- {Path(file_path).name}: {result['triples_extracted']} triples, {result['processing_time']:.2f}s\\n"
            else:
                report += f"- {Path(file_path).name}: FAILED - {result.get('error', 'Unknown error')}\\n"
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            self.logger.info(f"Performance report saved to {output_path}")
        
        return report


def batch_process_documents(input_dir: str, output_dir: str, 
                          config_path: str = "config.toml",
                          file_patterns: List[str] = None,
                          max_workers: int = 2) -> Dict[str, Any]:
    """
    Convenience function for batch processing documents.
    
    Args:
        input_dir: Directory containing input files
        output_dir: Directory for output files
        config_path: Path to configuration file
        file_patterns: List of file patterns to match
        max_workers: Maximum number of parallel workers
        
    Returns:
        Processing results with performance analysis
    """
    processor = BatchProcessor(config_path)
    results = processor.process_directory(input_dir, output_dir, file_patterns, max_workers)
    
    # Add performance analysis
    analyzer = PerformanceAnalyzer()
    performance_analysis = analyzer.analyze_batch_results(results)
    results["performance_analysis"] = performance_analysis
    
    # Generate report
    report = analyzer.generate_performance_report(results, 
                                                os.path.join(output_dir, "performance_report.md"))
    
    return results
