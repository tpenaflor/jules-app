"""
Activity Analyzer Module

This module provides detailed analysis of fitness activity data,
including performance metrics, training zones, and insights.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class ActivityAnalyzer:
    """Analyzer for fitness activity data with comprehensive metrics calculation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of activity data.
        
        Args:
            activity_data: Parsed activity data from FitFileParser
            
        Returns:
            Dict containing detailed analysis results
        """
        analysis = {
            'basic_metrics': {},
            'heart_rate_analysis': {},
            'power_analysis': {},
            'pace_speed_analysis': {},
            'training_zones': {},
            'performance_insights': {},
            'efficiency_metrics': {},
            'environmental_factors': {}
        }
        
        session = activity_data.get('session_info', {})
        records_df = activity_data.get('records_df')
        laps = activity_data.get('laps', [])
        
        # Basic metrics analysis
        analysis['basic_metrics'] = self._analyze_basic_metrics(session, records_df)
        
        # Heart rate analysis
        if records_df is not None and 'heart_rate' in records_df.columns:
            analysis['heart_rate_analysis'] = self._analyze_heart_rate(records_df, session)
        
        # Power analysis (for cycling)
        if records_df is not None and 'power' in records_df.columns:
            analysis['power_analysis'] = self._analyze_power(records_df, session)
        
        # Pace/Speed analysis
        if records_df is not None and 'speed' in records_df.columns:
            analysis['pace_speed_analysis'] = self._analyze_pace_speed(records_df, session)
        
        # Training zones analysis
        analysis['training_zones'] = self._analyze_training_zones(records_df, session)
        
        # Performance insights
        analysis['performance_insights'] = self._generate_performance_insights(
            analysis, session, records_df
        )
        
        # Efficiency metrics
        analysis['efficiency_metrics'] = self._calculate_efficiency_metrics(
            records_df, session
        )
        
        # Environmental factors
        analysis['environmental_factors'] = self._analyze_environmental_factors(
            records_df, session
        )
        
        return analysis
    
    def _analyze_basic_metrics(self, session: Dict, records_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Analyze basic activity metrics."""
        metrics = {}
        
        # Duration analysis
        total_time = session.get('total_elapsed_time', 0)
        moving_time = session.get('total_timer_time', 0)
        
        metrics['total_duration'] = self._format_duration(total_time)
        metrics['moving_duration'] = self._format_duration(moving_time)
        metrics['stopped_time'] = total_time - moving_time if total_time and moving_time else 0
        metrics['activity_factor'] = (moving_time / total_time * 100) if total_time > 0 else 0
        
        # Distance and elevation
        metrics['total_distance_km'] = (session.get('total_distance', 0) / 1000) if session.get('total_distance') else 0
        metrics['total_ascent_m'] = session.get('total_ascent', 0)
        metrics['total_descent_m'] = session.get('total_descent', 0)
        metrics['elevation_gain_ratio'] = (metrics['total_ascent_m'] / metrics['total_distance_km']) if metrics['total_distance_km'] > 0 else 0
        
        # Calories and intensity
        metrics['total_calories'] = session.get('total_calories', 0)
        metrics['calories_per_hour'] = (metrics['total_calories'] / (moving_time / 3600)) if moving_time > 0 else 0
        
        return metrics
    
    def _analyze_heart_rate(self, records_df: pd.DataFrame, session: Dict) -> Dict[str, Any]:
        """Analyze heart rate data and training zones."""
        hr_analysis = {}
        
        hr_data = records_df['heart_rate'].dropna()
        if hr_data.empty:
            return hr_analysis
        
        # Basic HR statistics
        hr_analysis['avg_hr'] = session.get('avg_heart_rate', hr_data.mean())
        hr_analysis['max_hr'] = session.get('max_heart_rate', hr_data.max())
        hr_analysis['min_hr'] = hr_data.min()
        hr_analysis['hr_range'] = hr_analysis['max_hr'] - hr_analysis['min_hr']
        hr_analysis['hr_std'] = hr_data.std()
        hr_analysis['hr_variability'] = (hr_analysis['hr_std'] / hr_analysis['avg_hr'] * 100)
        
        # Heart rate zones (assuming max HR of 220 - age, can be customized)
        estimated_max_hr = 190  # Default, should be configurable
        hr_analysis['hr_zones'] = self._calculate_hr_zones(hr_data, estimated_max_hr)
        
        # Heart rate trends
        hr_analysis['hr_drift'] = self._calculate_hr_drift(hr_data)
        
        return hr_analysis
    
    def _analyze_power(self, records_df: pd.DataFrame, session: Dict) -> Dict[str, Any]:
        """Analyze power data for cycling activities."""
        power_analysis = {}
        
        power_data = records_df['power'].dropna()
        if power_data.empty:
            return power_analysis
        
        # Basic power statistics
        power_analysis['avg_power'] = session.get('avg_power', power_data.mean())
        power_analysis['max_power'] = session.get('max_power', power_data.max())
        power_analysis['min_power'] = power_data.min()
        power_analysis['power_std'] = power_data.std()
        
        # Advanced power metrics
        power_analysis['normalized_power'] = self._calculate_normalized_power(power_data)
        power_analysis['intensity_factor'] = self._calculate_intensity_factor(
            power_analysis['normalized_power'], 250  # FTP placeholder
        )
        power_analysis['training_stress_score'] = self._calculate_tss(
            power_analysis['normalized_power'], 
            power_analysis['intensity_factor'],
            len(power_data) / 60  # duration in hours
        )
        
        # Power distribution
        power_analysis['power_zones'] = self._calculate_power_zones(power_data, 250)  # FTP placeholder
        
        # Variability Index
        power_analysis['variability_index'] = (power_analysis['normalized_power'] / 
                                             power_analysis['avg_power']) if power_analysis['avg_power'] > 0 else 0
        
        return power_analysis
    
    def _analyze_pace_speed(self, records_df: pd.DataFrame, session: Dict) -> Dict[str, Any]:
        """Analyze pace and speed data."""
        pace_analysis = {}
        
        speed_data = records_df['speed'].dropna()
        if speed_data.empty:
            return pace_analysis
        
        # Convert speed (m/s) to pace (min/km) for running
        # and to km/h for cycling
        sport = session.get('sport', '').lower()
        
        if sport in ['running', 'walking']:
            # Convert to pace (minutes per kilometer)
            pace_data = 1000 / (speed_data * 60)  # min/km
            pace_analysis['avg_pace_min_per_km'] = pace_data.mean()
            pace_analysis['best_pace_min_per_km'] = pace_data.min()
            pace_analysis['pace_variability'] = pace_data.std()
        else:
            # Convert to km/h for cycling and other sports
            speed_kmh = speed_data * 3.6
            pace_analysis['avg_speed_kmh'] = speed_kmh.mean()
            pace_analysis['max_speed_kmh'] = speed_kmh.max()
            pace_analysis['speed_variability'] = speed_kmh.std()
        
        return pace_analysis
    
    def _analyze_training_zones(self, records_df: Optional[pd.DataFrame], session: Dict) -> Dict[str, Any]:
        """Analyze time spent in different training zones."""
        zones_analysis = {}
        
        if records_df is None:
            return zones_analysis
        
        # Heart rate zones
        if 'heart_rate' in records_df.columns:
            hr_data = records_df['heart_rate'].dropna()
            if not hr_data.empty:
                zones_analysis['hr_zones_time'] = self._calculate_hr_zones(hr_data, 190)
        
        # Power zones (for cycling)
        if 'power' in records_df.columns:
            power_data = records_df['power'].dropna()
            if not power_data.empty:
                zones_analysis['power_zones_time'] = self._calculate_power_zones(power_data, 250)
        
        return zones_analysis
    
    def _generate_performance_insights(self, analysis: Dict, session: Dict, 
                                     records_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Generate performance insights and recommendations."""
        insights = {}
        
        sport = session.get('sport', '').lower()
        
        # Pacing insights
        if 'pace_speed_analysis' in analysis and analysis['pace_speed_analysis']:
            insights['pacing_strategy'] = self._analyze_pacing_strategy(analysis['pace_speed_analysis'])
        
        # Effort distribution
        if 'heart_rate_analysis' in analysis and analysis['heart_rate_analysis']:
            insights['effort_distribution'] = self._analyze_effort_distribution(
                analysis['heart_rate_analysis']
            )
        
        # Fatigue indicators
        insights['fatigue_indicators'] = self._analyze_fatigue_indicators(analysis, records_df)
        
        # Performance trends (would require historical data)
        insights['workout_quality'] = self._assess_workout_quality(analysis, session)
        
        return insights
    
    def _calculate_efficiency_metrics(self, records_df: Optional[pd.DataFrame], 
                                    session: Dict) -> Dict[str, Any]:
        """Calculate efficiency and economy metrics."""
        efficiency = {}
        
        if records_df is None:
            return efficiency
        
        # Heart rate efficiency (speed per heart rate)
        if 'heart_rate' in records_df.columns and 'speed' in records_df.columns:
            hr_data = records_df['heart_rate'].dropna()
            speed_data = records_df['speed'].dropna()
            
            if not hr_data.empty and not speed_data.empty:
                # Calculate efficiency as speed per heart rate
                common_indices = hr_data.index.intersection(speed_data.index)
                if len(common_indices) > 0:
                    efficiency_ratio = speed_data[common_indices] / hr_data[common_indices]
                    efficiency['hr_efficiency'] = efficiency_ratio.mean()
        
        # Power efficiency (for cycling)
        if 'power' in records_df.columns and 'speed' in records_df.columns:
            power_data = records_df['power'].dropna()
            speed_data = records_df['speed'].dropna()
            
            if not power_data.empty and not speed_data.empty:
                common_indices = power_data.index.intersection(speed_data.index)
                if len(common_indices) > 0:
                    efficiency_ratio = speed_data[common_indices] / power_data[common_indices]
                    efficiency['power_efficiency'] = efficiency_ratio.mean()
        
        return efficiency
    
    def _analyze_environmental_factors(self, records_df: Optional[pd.DataFrame], 
                                     session: Dict) -> Dict[str, Any]:
        """Analyze environmental factors that may affect performance."""
        environmental = {}
        
        if records_df is None:
            return environmental
        
        # Temperature analysis
        if 'temperature' in records_df.columns:
            temp_data = records_df['temperature'].dropna()
            if not temp_data.empty:
                environmental['avg_temperature'] = temp_data.mean()
                environmental['temp_range'] = temp_data.max() - temp_data.min()
        
        # Elevation profile analysis
        if 'altitude' in records_df.columns:
            altitude_data = records_df['altitude'].dropna()
            if not altitude_data.empty:
                environmental['elevation_profile'] = {
                    'min_elevation': altitude_data.min(),
                    'max_elevation': altitude_data.max(),
                    'elevation_range': altitude_data.max() - altitude_data.min(),
                    'avg_elevation': altitude_data.mean()
                }
        
        return environmental
    
    # Helper methods for calculations
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format."""
        if not seconds:
            return "0:00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def _calculate_hr_zones(self, hr_data: pd.Series, max_hr: int) -> Dict[str, float]:
        """Calculate time spent in heart rate zones."""
        zones = {
            'Zone 1 (50-60%)': (0.5 * max_hr, 0.6 * max_hr),
            'Zone 2 (60-70%)': (0.6 * max_hr, 0.7 * max_hr),
            'Zone 3 (70-80%)': (0.7 * max_hr, 0.8 * max_hr),
            'Zone 4 (80-90%)': (0.8 * max_hr, 0.9 * max_hr),
            'Zone 5 (90-100%)': (0.9 * max_hr, max_hr)
        }
        
        zone_times = {}
        total_records = len(hr_data)
        
        for zone_name, (min_hr, max_hr_zone) in zones.items():
            in_zone = hr_data[(hr_data >= min_hr) & (hr_data <= max_hr_zone)]
            zone_times[zone_name] = (len(in_zone) / total_records * 100) if total_records > 0 else 0
        
        return zone_times
    
    def _calculate_power_zones(self, power_data: pd.Series, ftp: int) -> Dict[str, float]:
        """Calculate time spent in power zones based on FTP."""
        zones = {
            'Zone 1 (0-55%)': (0, 0.55 * ftp),
            'Zone 2 (55-75%)': (0.55 * ftp, 0.75 * ftp),
            'Zone 3 (75-90%)': (0.75 * ftp, 0.90 * ftp),
            'Zone 4 (90-105%)': (0.90 * ftp, 1.05 * ftp),
            'Zone 5 (105-120%)': (1.05 * ftp, 1.20 * ftp),
            'Zone 6 (120%+)': (1.20 * ftp, float('inf'))
        }
        
        zone_times = {}
        total_records = len(power_data)
        
        for zone_name, (min_power, max_power) in zones.items():
            in_zone = power_data[(power_data >= min_power) & (power_data <= max_power)]
            zone_times[zone_name] = (len(in_zone) / total_records * 100) if total_records > 0 else 0
        
        return zone_times
    
    def _calculate_normalized_power(self, power_data: pd.Series) -> Optional[float]:
        """Calculate Normalized Power (NP)."""
        try:
            if len(power_data) < 30:
                return None
            
            # 30-second rolling average
            rolling_avg = power_data.rolling(window=30, center=True).mean()
            
            # Fourth power of the rolling averages
            fourth_power = rolling_avg ** 4
            
            # Average of fourth powers, then fourth root
            normalized_power = (fourth_power.mean()) ** 0.25
            
            return float(normalized_power)
        except Exception:
            return None
    
    def _calculate_intensity_factor(self, normalized_power: Optional[float], ftp: int) -> Optional[float]:
        """Calculate Intensity Factor (IF)."""
        if normalized_power is None or ftp <= 0:
            return None
        return normalized_power / ftp
    
    def _calculate_tss(self, normalized_power: Optional[float], intensity_factor: Optional[float], 
                      duration_hours: float) -> Optional[float]:
        """Calculate Training Stress Score (TSS)."""
        if intensity_factor is None or duration_hours <= 0:
            return None
        return (duration_hours * intensity_factor ** 2) * 100
    
    def _calculate_hr_drift(self, hr_data: pd.Series) -> Optional[float]:
        """Calculate heart rate drift over the activity."""
        if len(hr_data) < 10:
            return None
        
        # Calculate trend using linear regression
        x = np.arange(len(hr_data))
        coeffs = np.polyfit(x, hr_data, 1)
        return float(coeffs[0])  # Slope indicates drift
    
    def _analyze_pacing_strategy(self, pace_analysis: Dict) -> str:
        """Analyze pacing strategy."""
        # This would be more sophisticated with lap data
        if 'pace_variability' in pace_analysis:
            variability = pace_analysis['pace_variability']
            if variability < 0.5:
                return "Very consistent pacing - excellent for endurance"
            elif variability < 1.0:
                return "Good pacing consistency"
            else:
                return "Variable pacing - may indicate fatigue or tactical changes"
        return "Pacing analysis requires more data"
    
    def _analyze_effort_distribution(self, hr_analysis: Dict) -> str:
        """Analyze effort distribution."""
        if 'hr_zones' in hr_analysis:
            zones = hr_analysis['hr_zones']
            zone2_time = zones.get('Zone 2 (60-70%)', 0)
            high_intensity = sum([
                zones.get('Zone 4 (80-90%)', 0),
                zones.get('Zone 5 (90-100%)', 0)
            ])
            
            if zone2_time > 70:
                return "Primarily aerobic base training"
            elif high_intensity > 20:
                return "High-intensity training session"
            else:
                return "Mixed intensity training"
        return "Effort distribution analysis requires heart rate data"
    
    def _analyze_fatigue_indicators(self, analysis: Dict, records_df: Optional[pd.DataFrame]) -> List[str]:
        """Analyze indicators of fatigue during the activity."""
        indicators = []
        
        # Heart rate drift
        if 'heart_rate_analysis' in analysis and analysis['heart_rate_analysis'].get('hr_drift', 0) > 0.1:
            indicators.append("Significant heart rate drift indicating cardiovascular fatigue")
        
        # Power decline (if available)
        if 'power_analysis' in analysis:
            vi = analysis['power_analysis'].get('variability_index', 0)
            if vi > 1.1:
                indicators.append("High power variability suggesting fatigue or pacing issues")
        
        if not indicators:
            indicators.append("No significant fatigue indicators detected")
        
        return indicators
    
    def _assess_workout_quality(self, analysis: Dict, session: Dict) -> str:
        """Assess overall workout quality."""
        quality_score = 0
        factors = 0
        
        # Consistency factors
        if 'heart_rate_analysis' in analysis:
            hr_var = analysis['heart_rate_analysis'].get('hr_variability', 0)
            if hr_var < 10:  # Low variability is good for steady state
                quality_score += 1
            factors += 1
        
        # Completion factor
        total_time = session.get('total_elapsed_time', 0)
        moving_time = session.get('total_timer_time', 0)
        if total_time > 0 and (moving_time / total_time) > 0.8:
            quality_score += 1
        factors += 1
        
        if factors > 0:
            quality_ratio = quality_score / factors
            if quality_ratio > 0.8:
                return "Excellent workout quality"
            elif quality_ratio > 0.6:
                return "Good workout quality"
            else:
                return "Room for improvement in workout quality"
        
        return "Workout quality assessment requires more data"