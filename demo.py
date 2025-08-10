#!/usr/bin/env python3
"""
Demo script for Jules App FIT File Analysis

This script demonstrates the core functionality without requiring actual FIT files.
"""

import pandas as pd
from jules_app.parser import FitFileParser
from jules_app.analyzer import ActivityAnalyzer


def demo_activity_analysis():
    """Demonstrate activity analysis with synthetic data."""
    print("=" * 60)
    print("JULES APP - FIT FILE ANALYSIS DEMO")
    print("=" * 60)
    print()
    
    # Create synthetic activity data to demonstrate the analysis
    print("Creating synthetic activity data...")
    
    # Simulate a 1-hour cycling workout
    activity_data = {
        'session_info': {
            'sport': 'cycling',
            'sub_sport': 'road',
            'start_time': '2024-01-15T09:00:00Z',
            'total_elapsed_time': 3660,  # 61 minutes
            'total_timer_time': 3600,    # 60 minutes moving
            'total_distance': 45000,     # 45km
            'avg_speed': 12.5,           # m/s (45 km/h)
            'max_speed': 18.0,           # m/s (64.8 km/h)
            'avg_heart_rate': 155,       # bpm
            'max_heart_rate': 185,       # bpm
            'avg_power': 220,            # watts
            'max_power': 450,            # watts
            'total_calories': 850,
            'avg_cadence': 85,           # rpm
            'max_cadence': 110,
            'total_ascent': 650,         # meters
            'total_descent': 650
        },
        'records': [],
        'laps': [],
        'device_info': {'manufacturer': 'Garmin', 'product': 'Edge 530'},
        'hr_zones': [],
        'power_zones': [],
        'events': []
    }
    
    # Create synthetic time-series data (360 records = 1 per 10 seconds for 1 hour)
    import numpy as np
    np.random.seed(42)  # For reproducible results
    
    records_data = {
        'timestamp': pd.date_range('2024-01-15 09:00:00', periods=360, freq='10S'),
        'heart_rate': np.random.normal(155, 15, 360).clip(120, 185).astype(int),
        'power': np.random.normal(220, 40, 360).clip(100, 450).astype(int),
        'speed': np.random.normal(12.5, 2, 360).clip(8, 18),
        'cadence': np.random.normal(85, 10, 360).clip(60, 110).astype(int),
        'altitude': 100 + np.cumsum(np.random.normal(0, 0.5, 360)).clip(-50, 200),
        'temperature': np.random.normal(18, 2, 360).clip(12, 25)
    }
    
    activity_data['records_df'] = pd.DataFrame(records_data)
    
    print("✓ Synthetic data created")
    print(f"  - Sport: {activity_data['session_info']['sport']}")
    print(f"  - Duration: {activity_data['session_info']['total_timer_time'] / 60:.0f} minutes")
    print(f"  - Distance: {activity_data['session_info']['total_distance'] / 1000:.1f} km")
    print(f"  - Data points: {len(activity_data['records_df'])}")
    print()
    
    # Initialize components
    print("Initializing analysis components...")
    parser = FitFileParser()
    analyzer = ActivityAnalyzer()
    print("✓ Components initialized")
    print()
    
    # Generate activity summary
    print("Generating activity summary...")
    summary = parser.get_activity_summary(activity_data)
    
    print("ACTIVITY SUMMARY:")
    print("-" * 20)
    print(f"Sport: {summary.get('sport', 'Unknown')}")
    print(f"Distance: {summary.get('total_distance', 0) / 1000:.2f} km")
    print(f"Duration: {summary.get('total_timer_time', 0) / 60:.1f} minutes")
    print(f"Avg Speed: {summary.get('avg_speed', 0) * 3.6:.1f} km/h")
    print(f"Avg Heart Rate: {summary.get('avg_heart_rate', 0)} bpm")
    print(f"Avg Power: {summary.get('avg_power', 0)} watts")
    print(f"Calories: {summary.get('total_calories', 0)}")
    print()
    
    # Perform detailed analysis
    print("Performing detailed analysis...")
    detailed_analysis = analyzer.analyze_activity(activity_data)
    print("✓ Analysis completed")
    print()
    
    # Display key analysis results
    print("DETAILED ANALYSIS RESULTS:")
    print("-" * 30)
    
    # Basic metrics
    basic = detailed_analysis.get('basic_metrics', {})
    if basic:
        print("Basic Metrics:")
        print(f"  - Activity Factor: {basic.get('activity_factor', 0):.1f}%")
        print(f"  - Elevation Gain Ratio: {basic.get('elevation_gain_ratio', 0):.1f} m/km")
        print(f"  - Calories/hour: {basic.get('calories_per_hour', 0):.0f}")
    
    # Heart rate analysis
    hr_analysis = detailed_analysis.get('heart_rate_analysis', {})
    if hr_analysis:
        print("\nHeart Rate Analysis:")
        print(f"  - Average: {hr_analysis.get('avg_hr', 0):.0f} bpm")
        print(f"  - Max: {hr_analysis.get('max_hr', 0)} bpm")
        print(f"  - Range: {hr_analysis.get('hr_range', 0)} bpm")
        print(f"  - Variability: {hr_analysis.get('hr_variability', 0):.1f}%")
        
        hr_zones = hr_analysis.get('hr_zones', {})
        if hr_zones:
            print("  - Heart Rate Zones:")
            for zone, percentage in hr_zones.items():
                print(f"    {zone}: {percentage:.1f}%")
    
    # Power analysis
    power_analysis = detailed_analysis.get('power_analysis', {})
    if power_analysis:
        print("\nPower Analysis:")
        print(f"  - Average: {power_analysis.get('avg_power', 0):.0f} watts")
        print(f"  - Normalized Power: {power_analysis.get('normalized_power', 0):.0f} watts")
        print(f"  - Variability Index: {power_analysis.get('variability_index', 0):.2f}")
        print(f"  - Training Stress Score: {power_analysis.get('training_stress_score', 0):.0f}")
        
        power_zones = power_analysis.get('power_zones', {})
        if power_zones:
            print("  - Power Zones:")
            for zone, percentage in power_zones.items():
                print(f"    {zone}: {percentage:.1f}%")
    
    # Performance insights
    insights = detailed_analysis.get('performance_insights', {})
    if insights:
        print("\nPerformance Insights:")
        for key, value in insights.items():
            if isinstance(value, str):
                print(f"  - {key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, list):
                print(f"  - {key.replace('_', ' ').title()}:")
                for item in value:
                    print(f"    • {item}")
    
    print()
    print("=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("To use with real FIT files:")
    print("1. Set your OPENAI_API_KEY environment variable")
    print("2. Use: python -m jules_app.cli analyze your_activity.fit")
    print("3. Or use the Python API as shown in examples/usage_examples.py")


if __name__ == "__main__":
    demo_activity_analysis()