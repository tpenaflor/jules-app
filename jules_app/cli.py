#!/usr/bin/env python3
"""
Jules App - CLI for FIT File Analysis

Command-line interface for analyzing FIT files using AI.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional

from jules_app import FitAnalysisAgent


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze FIT files using AI-powered insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze activity.fit                    # Basic analysis
  %(prog)s analyze activity.fit --type summary     # Quick summary
  %(prog)s analyze activity.fit --athlete-age 25   # Include athlete info
  %(prog)s compare *.fit                          # Compare multiple activities
  %(prog)s recommendations activity.fit           # Get training recommendations
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single FIT file')
    analyze_parser.add_argument('file', help='Path to FIT file')
    analyze_parser.add_argument(
        '--type', 
        choices=['comprehensive', 'summary', 'technical'],
        default='comprehensive',
        help='Type of analysis to perform'
    )
    analyze_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    analyze_parser.add_argument('--athlete-age', type=int, help='Athlete age for HR zones')
    analyze_parser.add_argument('--athlete-weight', type=float, help='Athlete weight in kg')
    analyze_parser.add_argument('--athlete-ftp', type=int, help='Athlete FTP for power zones')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple FIT files')
    compare_parser.add_argument('files', nargs='+', help='Paths to FIT files')
    compare_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    compare_parser.add_argument('--athlete-age', type=int, help='Athlete age')
    compare_parser.add_argument('--athlete-weight', type=float, help='Athlete weight in kg')
    compare_parser.add_argument('--athlete-ftp', type=int, help='Athlete FTP')
    
    # Recommendations command
    rec_parser = subparsers.add_parser('recommendations', help='Get training recommendations')
    rec_parser.add_argument('file', help='Path to FIT file')
    rec_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    rec_parser.add_argument('--athlete-age', type=int, help='Athlete age')
    rec_parser.add_argument('--athlete-weight', type=float, help='Athlete weight in kg')
    rec_parser.add_argument('--athlete-ftp', type=int, help='Athlete FTP')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        print("Please set your OpenAI API key:", file=sys.stderr)
        print("  export OPENAI_API_KEY='your-api-key-here'", file=sys.stderr)
        return 1
    
    try:
        # Initialize agent
        agent = FitAnalysisAgent()
        
        # Prepare athlete info if provided
        athlete_info = {}
        if hasattr(args, 'athlete_age') and args.athlete_age:
            athlete_info['age'] = args.athlete_age
        if hasattr(args, 'athlete_weight') and args.athlete_weight:
            athlete_info['weight'] = args.athlete_weight
        if hasattr(args, 'athlete_ftp') and args.athlete_ftp:
            athlete_info['ftp'] = args.athlete_ftp
        
        # Execute command
        if args.command == 'analyze':
            result = agent.analyze_fit_file(
                args.file, 
                args.type, 
                athlete_info if athlete_info else None
            )
        elif args.command == 'compare':
            result = agent.analyze_multiple_activities(
                args.files,
                athlete_info if athlete_info else None
            )
        elif args.command == 'recommendations':
            # First analyze the file
            analysis = agent.analyze_fit_file(
                args.file, 
                'comprehensive',
                athlete_info if athlete_info else None
            )
            # Then get recommendations
            result = agent.generate_training_recommendations(analysis)
        
        # Output result
        output_text = format_output(result, args.command)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Analysis saved to {args.output}")
        else:
            print(output_text)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def format_output(result: dict, command: str) -> str:
    """Format the analysis result for human-readable output."""
    
    if command == 'analyze':
        return format_analysis_output(result)
    elif command == 'compare':
        return format_comparison_output(result)
    elif command == 'recommendations':
        return format_recommendations_output(result)
    else:
        return json.dumps(result, indent=2, default=str)


def format_analysis_output(result: dict) -> str:
    """Format single activity analysis output."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("FIT FILE ANALYSIS REPORT")
    output.append("=" * 60)
    output.append("")
    
    # Basic info
    summary = result.get('activity_summary', {})
    output.append(f"File: {result.get('file_path', 'Unknown')}")
    output.append(f"Sport: {summary.get('sport', 'Unknown')}")
    output.append(f"Date: {summary.get('start_time', 'Unknown')}")
    output.append("")
    
    # Key metrics
    output.append("KEY METRICS")
    output.append("-" * 20)
    
    if summary.get('total_distance'):
        distance_km = summary['total_distance'] / 1000
        output.append(f"Distance: {distance_km:.2f} km")
    
    if summary.get('total_timer_time'):
        duration = format_duration(summary['total_timer_time'])
        output.append(f"Duration: {duration}")
    
    if summary.get('avg_heart_rate'):
        output.append(f"Avg Heart Rate: {summary['avg_heart_rate']} bpm")
    
    if summary.get('avg_power'):
        output.append(f"Avg Power: {summary['avg_power']} watts")
    
    if summary.get('total_calories'):
        output.append(f"Calories: {summary['total_calories']}")
    
    output.append("")
    
    # AI Analysis
    ai_analysis = result.get('ai_analysis', {})
    if ai_analysis and not ai_analysis.get('error'):
        output.append("AI ANALYSIS")
        output.append("-" * 20)
        
        content = ai_analysis.get('content', '')
        if isinstance(content, dict):
            output.append(content.get('analysis', 'No analysis available'))
        else:
            output.append(str(content))
        output.append("")
    
    return "\n".join(output)


def format_comparison_output(result: dict) -> str:
    """Format multi-activity comparison output."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("MULTI-ACTIVITY COMPARISON REPORT")
    output.append("=" * 60)
    output.append("")
    
    output.append(f"Total Activities Analyzed: {result.get('total_activities', 0)}")
    output.append("")
    
    # List activities
    output.append("ACTIVITIES:")
    output.append("-" * 20)
    for i, activity_path in enumerate(result.get('activities_analyzed', []), 1):
        output.append(f"{i}. {Path(activity_path).name}")
    output.append("")
    
    # Comparative analysis
    comparative = result.get('comparative_analysis', {})
    if comparative and not comparative.get('error'):
        output.append("COMPARATIVE ANALYSIS")
        output.append("-" * 30)
        
        content = comparative.get('content', comparative.get('analysis', ''))
        if isinstance(content, dict):
            output.append(content.get('analysis', 'No analysis available'))
        else:
            output.append(str(content))
        output.append("")
    
    return "\n".join(output)


def format_recommendations_output(result: dict) -> str:
    """Format training recommendations output."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("TRAINING RECOMMENDATIONS")
    output.append("=" * 60)
    output.append("")
    
    if result.get('error'):
        output.append(f"Error generating recommendations: {result['error']}")
    else:
        recommendations = result.get('recommendations', '')
        if isinstance(recommendations, dict):
            output.append(recommendations.get('analysis', 'No recommendations available'))
        else:
            output.append(str(recommendations))
    
    output.append("")
    output.append(f"Generated: {result.get('generated_at', 'Unknown')}")
    
    return "\n".join(output)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if not seconds:
        return "0:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours}:{minutes:02d}:{seconds:02d}"


if __name__ == '__main__':
    sys.exit(main())