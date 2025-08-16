#!/usr/bin/env python3
"""
Java Mermaid Flowchart Generator - Main Entry Point

A tool for generating Mermaid flowcharts from Java methods using LLM analysis.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from java_mermaid.core.flowchart_generator import FlowchartGenerator
from java_mermaid.cli.arg_parser import parse_cli_args
from java_mermaid.utils.logger import setup_logger


def main():
    """Main entry point for the Java Mermaid flowchart generator."""
    try:
        # Parse command line arguments
        args = parse_cli_args()
        
        # Setup logging based on verbose flag
        logger = setup_logger(verbose=args.verbose)
        logger.info("Starting Java Mermaid flowchart generator")
        
        # Initialize the generator
        generator = FlowchartGenerator(
            api_key=args.api_key,
            api_endpoint=args.api_endpoint,
            model=args.model,
            output_dir=args.output_dir,
            generate_png=not args.pic_off,
            generate_comments=not args.comments_off,
            generate_javadoc=not args.doc_off,
            verbose=args.verbose
        )
        
        # Generate flowchart
        generator.generate(
            java_file=args.java_file,
            class_name=args.class_name,
            method_name=args.method_name
        )
        
        logger.info("Flowchart generation completed successfully")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()