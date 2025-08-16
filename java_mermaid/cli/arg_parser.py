"""
CLI Argument Parser for Java Mermaid Flowchart Generator.

Handles command-line argument parsing with support for output control flags.
"""

import argparse
import os
import sys
from typing import NamedTuple


class CliArgs(NamedTuple):
    """Named tuple for parsed CLI arguments."""
    java_file: str
    class_name: str
    method_name: str
    api_key: str = None
    api_endpoint: str = None
    model: str = None
    output_dir: str = "."
    pic_off: bool = False
    doc_off: bool = False
    comments_off: bool = False
    verbose: bool = False
    dry_run: bool = False
    config: str = None


def parse_cli_args() -> CliArgs:
    """
    Parse command line arguments for the Java Mermaid flowchart generator.
    
    Returns:
        CliArgs: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate Mermaid flowcharts from Java methods using LLM analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MyClass myMethod MyFile.java
  %(prog)s MyClass myMethod MyFile.java --doc-off
  %(prog)s MyClass myMethod MyFile.java --pic-off --output-dir ./docs/
  %(prog)s MyClass myMethod MyFile.java --api-endpoint https://internal-llm.local
  %(prog)s MyClass myMethod MyFile.java --verbose --dry-run
        """
    )
    
    # Positional arguments
    parser.add_argument(
        "class_name",
        help="Name of the Java class containing the method"
    )
    parser.add_argument(
        "method_name",
        help="Name of the Java method to analyze"
    )
    parser.add_argument(
        "java_file",
        help="Path to the Java source file"
    )
    
    # Output control flags
    output_group = parser.add_argument_group("Output Control")
    output_group.add_argument(
        "--pic-off",
        action="store_true",
        help="Disable PNG image generation"
    )
    output_group.add_argument(
        "--doc-off",
        action="store_true",
        help="Disable JavaDoc comment insertion"
    )
    output_group.add_argument(
        "--comments-off",
        action="store_true",
        help="Disable all comment generation"
    )
    output_group.add_argument(
        "--output-dir",
        default=".",
        help="Specify custom output directory (default: current directory)"
    )
    
    # LLM configuration
    llm_group = parser.add_argument_group("LLM Configuration")
    llm_group.add_argument(
        "--api-key",
        help="OpenAI API key or compatible API key"
    )
    llm_group.add_argument(
        "--api-endpoint",
        default="https://api.openai.com/v1",
        help="Custom LLM API endpoint (default: https://api.openai.com/v1)"
    )
    llm_group.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="LLM model to use (default: gpt-3.5-turbo)"
    )
    
    # Configuration and debugging
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--config",
        help="Load configuration from file"
    )
    config_group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    config_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without making changes"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    _validate_arguments(args)
    
    # Load configuration from file if specified
    if args.config:
        _load_config_file(args)
    
    # Load API key from environment if not provided
    if not args.api_key:
        args.api_key = os.getenv("OPENAI_API_KEY")
        if not args.api_key:
            print("Warning: No API key provided. Set OPENAI_API_KEY environment variable.", file=sys.stderr)
    
    return CliArgs(
        java_file=args.java_file,
        class_name=args.class_name,
        method_name=args.method_name,
        api_key=args.api_key,
        api_endpoint=args.api_endpoint,
        model=args.model,
        output_dir=args.output_dir,
        pic_off=args.pic_off,
        doc_off=args.doc_off,
        comments_off=args.comments_off,
        verbose=args.verbose,
        dry_run=args.dry_run,
        config=args.config
    )


def _validate_arguments(args):
    """Validate command line arguments."""
    # Check if Java file exists
    if not os.path.exists(args.java_file):
        print(f"Error: Java file '{args.java_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(args.java_file):
        print(f"Error: '{args.java_file}' is not a file", file=sys.stderr)
        sys.exit(1)
    
    if not args.java_file.endswith('.java'):
        print(f"Error: '{args.java_file}' is not a Java file (.java extension expected)", file=sys.stderr)
        sys.exit(1)
    
    # Check output directory
    if args.output_dir != ".":
        if not os.path.exists(args.output_dir):
            try:
                os.makedirs(args.output_dir, exist_ok=True)
            except OSError as e:
                print(f"Error: Cannot create output directory '{args.output_dir}': {e}", file=sys.stderr)
                sys.exit(1)
        elif not os.path.isdir(args.output_dir):
            print(f"Error: Output path '{args.output_dir}' is not a directory", file=sys.stderr)
            sys.exit(1)


def _load_config_file(args):
    """Load configuration from file."""
    import json
    
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Override CLI args with config file values
        for key, value in config.items():
            if hasattr(args, key) and getattr(args, key) is None:
                setattr(args, key, value)
                
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{args.config}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # For testing
    args = parse_cli_args()
    print(f"Parsed arguments: {args}")