"""
FIT File Parser Module

This module handles parsing of FIT (Flexible and Interoperable Data Transfer) files
commonly used by fitness devices like Garmin, Polar, and others.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

try:
    from fitparse import FitFile
except ImportError:
    raise ImportError("fitparse library is required. Install with: pip install fitparse")


class FitFileParser:
    """Parser for FIT files that extracts activity data and metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse_fit_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a FIT file and extract all relevant data.
        
        Args:
            file_path (str): Path to the FIT file
            
        Returns:
            Dict containing parsed activity data
        """
        try:
            fitfile = FitFile(file_path)
            
            # Initialize data containers
            activity_data = {
                'session_info': {},
                'records': [],
                'laps': [],
                'device_info': {},
                'hr_zones': [],
                'power_zones': [],
                'events': []
            }
            
            # Parse different message types
            for record in fitfile.get_messages():
                msg_type = record.name
                
                if msg_type == 'session':
                    activity_data['session_info'] = self._extract_session_data(record)
                elif msg_type == 'record':
                    activity_data['records'].append(self._extract_record_data(record))
                elif msg_type == 'lap':
                    activity_data['laps'].append(self._extract_lap_data(record))
                elif msg_type == 'device_info':
                    activity_data['device_info'] = self._extract_device_info(record)
                elif msg_type == 'hr_zone':
                    activity_data['hr_zones'].append(self._extract_hr_zone(record))
                elif msg_type == 'power_zone':
                    activity_data['power_zones'].append(self._extract_power_zone(record))
                elif msg_type == 'event':
                    activity_data['events'].append(self._extract_event_data(record))
            
            # Convert records to DataFrame for easier analysis
            if activity_data['records']:
                activity_data['records_df'] = pd.DataFrame(activity_data['records'])
            
            self.logger.info(f"Successfully parsed FIT file: {file_path}")
            return activity_data
            
        except Exception as e:
            self.logger.error(f"Error parsing FIT file {file_path}: {str(e)}")
            raise
    
    def _extract_session_data(self, record) -> Dict[str, Any]:
        """Extract session-level data from FIT file."""
        session_data = {}
        
        for field in record.fields:
            if field.value is not None:
                session_data[field.name] = field.value
        
        return session_data
    
    def _extract_record_data(self, record) -> Dict[str, Any]:
        """Extract individual record data points."""
        record_data = {}
        
        for field in record.fields:
            if field.value is not None:
                record_data[field.name] = field.value
        
        return record_data
    
    def _extract_lap_data(self, record) -> Dict[str, Any]:
        """Extract lap data from FIT file."""
        lap_data = {}
        
        for field in record.fields:
            if field.value is not None:
                lap_data[field.name] = field.value
        
        return lap_data
    
    def _extract_device_info(self, record) -> Dict[str, Any]:
        """Extract device information."""
        device_data = {}
        
        for field in record.fields:
            if field.value is not None:
                device_data[field.name] = field.value
        
        return device_data
    
    def _extract_hr_zone(self, record) -> Dict[str, Any]:
        """Extract heart rate zone information."""
        hr_zone = {}
        
        for field in record.fields:
            if field.value is not None:
                hr_zone[field.name] = field.value
        
        return hr_zone
    
    def _extract_power_zone(self, record) -> Dict[str, Any]:
        """Extract power zone information."""
        power_zone = {}
        
        for field in record.fields:
            if field.value is not None:
                power_zone[field.name] = field.value
        
        return power_zone
    
    def _extract_event_data(self, record) -> Dict[str, Any]:
        """Extract event data (start, stop, etc.)."""
        event_data = {}
        
        for field in record.fields:
            if field.value is not None:
                event_data[field.name] = field.value
        
        return event_data
    
    def get_activity_summary(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the activity from parsed data.
        
        Args:
            activity_data: Parsed activity data from parse_fit_file
            
        Returns:
            Dict containing activity summary
        """
        summary = {}
        
        session = activity_data.get('session_info', {})
        records_df = activity_data.get('records_df')
        
        # Basic activity info
        summary['sport'] = session.get('sport', 'Unknown')
        summary['sub_sport'] = session.get('sub_sport', 'Unknown')
        summary['start_time'] = session.get('start_time')
        summary['total_elapsed_time'] = session.get('total_elapsed_time')
        summary['total_timer_time'] = session.get('total_timer_time')
        summary['total_distance'] = session.get('total_distance')
        
        # Performance metrics
        summary['avg_speed'] = session.get('avg_speed')
        summary['max_speed'] = session.get('max_speed')
        summary['avg_heart_rate'] = session.get('avg_heart_rate')
        summary['max_heart_rate'] = session.get('max_heart_rate')
        summary['avg_power'] = session.get('avg_power')
        summary['max_power'] = session.get('max_power')
        summary['total_calories'] = session.get('total_calories')
        summary['avg_cadence'] = session.get('avg_cadence')
        summary['max_cadence'] = session.get('max_cadence')
        
        # Elevation data
        summary['total_ascent'] = session.get('total_ascent')
        summary['total_descent'] = session.get('total_descent')
        
        # Additional analysis from records
        if records_df is not None and not records_df.empty:
            summary['num_records'] = len(records_df)
            
            # Calculate additional metrics if data is available
            if 'heart_rate' in records_df.columns:
                hr_data = records_df['heart_rate'].dropna()
                if not hr_data.empty:
                    summary['hr_min'] = hr_data.min()
                    summary['hr_std'] = hr_data.std()
            
            if 'power' in records_df.columns:
                power_data = records_df['power'].dropna()
                if not power_data.empty:
                    summary['power_min'] = power_data.min()
                    summary['power_std'] = power_data.std()
                    summary['normalized_power'] = self._calculate_normalized_power(power_data)
            
            if 'speed' in records_df.columns:
                speed_data = records_df['speed'].dropna()
                if not speed_data.empty:
                    summary['speed_min'] = speed_data.min()
                    summary['speed_std'] = speed_data.std()
        
        return summary
    
    def _calculate_normalized_power(self, power_data: pd.Series) -> Optional[float]:
        """Calculate Normalized Power (NP) for cycling activities."""
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