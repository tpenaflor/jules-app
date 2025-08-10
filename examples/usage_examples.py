"""
Example usage of the Jules App FIT File Analysis Agent

This module demonstrates how to use the AI agent to analyze FIT files
and generate comprehensive insights about fitness activities.
"""

import os
from pathlib import Path
from jules_app import FitAnalysisAgent


def basic_analysis_example():
    """Example of basic FIT file analysis."""
    print("=== Basic FIT File Analysis Example ===")
    
    # Initialize the agent
    # Make sure to set your OPENAI_API_KEY environment variable
    agent = FitAnalysisAgent()
    
    # Example FIT file path (you'll need to provide your own)
    fit_file_path = "examples/sample_activity.fit"
    
    if not os.path.exists(fit_file_path):
        print(f"Sample FIT file not found at {fit_file_path}")
        print("Please provide a valid FIT file path")
        return
    
    try:
        # Analyze the FIT file
        result = agent.analyze_fit_file(fit_file_path, analysis_type="comprehensive")
        
        # Print key information
        print(f"Activity: {result['activity_summary'].get('sport', 'Unknown')}")
        print(f"Duration: {result['activity_summary'].get('total_timer_time', 0) / 60:.1f} minutes")
        print(f"Distance: {result['activity_summary'].get('total_distance', 0) / 1000:.2f} km")
        
        # Print AI analysis
        ai_analysis = result['ai_analysis']['content']
        if isinstance(ai_analysis, dict):
            print("\nAI Analysis:")
            print(ai_analysis.get('analysis', 'No analysis available'))
        else:
            print("\nAI Analysis:")
            print(ai_analysis)
            
    except Exception as e:
        print(f"Error analyzing FIT file: {e}")


def athlete_specific_analysis_example():
    """Example with athlete-specific information."""
    print("=== Athlete-Specific Analysis Example ===")
    
    agent = FitAnalysisAgent()
    
    # Athlete information for more accurate analysis
    athlete_info = {
        'age': 30,
        'weight': 70.0,  # kg
        'ftp': 250       # Functional Threshold Power for cycling
    }
    
    fit_file_path = "examples/sample_activity.fit"
    
    if not os.path.exists(fit_file_path):
        print(f"Sample FIT file not found at {fit_file_path}")
        print("Please provide a valid FIT file path")
        return
    
    try:
        result = agent.analyze_fit_file(
            fit_file_path, 
            analysis_type="comprehensive",
            athlete_info=athlete_info
        )
        
        # Print athlete-specific insights
        athlete_specific = result['detailed_analysis'].get('athlete_specific', {})
        if athlete_specific:
            print("Athlete-Specific Metrics:")
            print(f"Estimated Max HR: {athlete_specific.get('estimated_max_hr', 'N/A')} bpm")
            print(f"Power-to-Weight Ratio: {athlete_specific.get('power_to_weight_ratio', 'N/A'):.2f} W/kg")
        
        print("\nAI Analysis (with athlete context):")
        print(result['ai_analysis']['content'])
        
    except Exception as e:
        print(f"Error: {e}")


def quick_summary_example():
    """Example of quick summary analysis."""
    print("=== Quick Summary Example ===")
    
    agent = FitAnalysisAgent()
    
    fit_file_path = "examples/sample_activity.fit"
    
    if not os.path.exists(fit_file_path):
        print(f"Sample FIT file not found at {fit_file_path}")
        return
    
    try:
        result = agent.analyze_fit_file(fit_file_path, analysis_type="summary")
        
        print("Quick Summary:")
        print(result['ai_analysis']['content'])
        
    except Exception as e:
        print(f"Error: {e}")


def multiple_activities_comparison_example():
    """Example of comparing multiple activities."""
    print("=== Multiple Activities Comparison Example ===")
    
    agent = FitAnalysisAgent()
    
    # List of FIT files to compare
    fit_files = [
        "examples/activity1.fit",
        "examples/activity2.fit",
        "examples/activity3.fit"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in fit_files if os.path.exists(f)]
    
    if len(existing_files) < 2:
        print("Need at least 2 FIT files for comparison")
        print("Please provide valid FIT file paths")
        return
    
    try:
        result = agent.analyze_multiple_activities(existing_files)
        
        print(f"Compared {result['total_activities']} activities")
        print("\nComparative Analysis:")
        print(result['comparative_analysis']['content'])
        
    except Exception as e:
        print(f"Error: {e}")


def training_recommendations_example():
    """Example of generating training recommendations."""
    print("=== Training Recommendations Example ===")
    
    agent = FitAnalysisAgent()
    
    fit_file_path = "examples/sample_activity.fit"
    
    if not os.path.exists(fit_file_path):
        print(f"Sample FIT file not found at {fit_file_path}")
        return
    
    try:
        # First analyze the activity
        analysis = agent.analyze_fit_file(fit_file_path, analysis_type="comprehensive")
        
        # Generate training recommendations
        recommendations = agent.generate_training_recommendations(analysis)
        
        print("Training Recommendations:")
        print(recommendations['recommendations'])
        
    except Exception as e:
        print(f"Error: {e}")


def programmatic_usage_example():
    """Example of using the agent programmatically for custom analysis."""
    print("=== Programmatic Usage Example ===")
    
    from jules_app.parser import FitFileParser
    from jules_app.analyzer import ActivityAnalyzer
    
    # Use individual components for custom analysis
    parser = FitFileParser()
    analyzer = ActivityAnalyzer()
    
    fit_file_path = "examples/sample_activity.fit"
    
    if not os.path.exists(fit_file_path):
        print(f"Sample FIT file not found at {fit_file_path}")
        return
    
    try:
        # Parse the FIT file
        raw_data = parser.parse_fit_file(fit_file_path)
        
        # Get basic summary
        summary = parser.get_activity_summary(raw_data)
        print(f"Activity Type: {summary.get('sport')}")
        print(f"Records: {len(raw_data.get('records', []))}")
        
        # Perform detailed analysis
        detailed_analysis = analyzer.analyze_activity(raw_data)
        
        # Access specific metrics
        hr_analysis = detailed_analysis.get('heart_rate_analysis', {})
        if hr_analysis:
            print(f"Average HR: {hr_analysis.get('avg_hr', 'N/A')} bpm")
            print(f"HR Zones: {hr_analysis.get('hr_zones', {})}")
        
        power_analysis = detailed_analysis.get('power_analysis', {})
        if power_analysis:
            print(f"Normalized Power: {power_analysis.get('normalized_power', 'N/A')} W")
            print(f"Training Stress Score: {power_analysis.get('training_stress_score', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("Jules App FIT File Analysis Examples")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set. AI analysis will not work.")
        print("Set your API key with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    
    print("Note: These examples require actual FIT files in the examples/ directory")
    print("You can obtain FIT files from fitness devices like Garmin, Polar, etc.")
    print()
    
    try:
        # Run examples that don't require FIT files
        programmatic_usage_example()
        
        # The following examples would work with actual FIT files:
        # basic_analysis_example()
        # athlete_specific_analysis_example()
        # quick_summary_example()
        # multiple_activities_comparison_example()
        # training_recommendations_example()
        
    except Exception as e:
        print(f"Example error: {e}")


if __name__ == "__main__":
    main()