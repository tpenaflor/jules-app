"""
Tests for the Jules App FIT File Analysis system.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
import pandas as pd

from jules_app.parser import FitFileParser
from jules_app.analyzer import ActivityAnalyzer
from jules_app.agent import FitAnalysisAgent


class TestFitFileParser:
    """Tests for FitFileParser class."""
    
    def test_init(self):
        """Test parser initialization."""
        parser = FitFileParser()
        assert parser is not None
        assert hasattr(parser, 'logger')
    
    def test_parser_initialization(self):
        """Test parser initialization and basic functionality."""
        parser = FitFileParser()
        
        # Test that parser has required methods
        assert hasattr(parser, 'parse_fit_file')
        assert hasattr(parser, 'get_activity_summary')
        assert hasattr(parser, '_calculate_normalized_power')
    
    def test_calculate_normalized_power(self):
        """Test normalized power calculation."""
        parser = FitFileParser()
        
        # Test with insufficient data
        short_data = pd.Series([100, 200, 150])
        assert parser._calculate_normalized_power(short_data) is None
        
        # Test with sufficient data
        power_data = pd.Series([200] * 100)  # 100 data points of 200W
        np_result = parser._calculate_normalized_power(power_data)
        assert np_result is not None
        assert isinstance(np_result, float)
        assert np_result > 0


class TestActivityAnalyzer:
    """Tests for ActivityAnalyzer class."""
    
    def test_init(self):
        """Test analyzer initialization."""
        analyzer = ActivityAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'logger')
    
    def test_format_duration(self):
        """Test duration formatting helper."""
        analyzer = ActivityAnalyzer()
        
        assert analyzer._format_duration(0) == "0:00:00"
        assert analyzer._format_duration(3665) == "1:01:05"
    
    def test_calculate_hr_zones(self):
        """Test heart rate zones calculation."""
        analyzer = ActivityAnalyzer()
        
        # Create sample HR data that should be distributed across zones
        # Use data that falls clearly into different zones
        hr_data = pd.Series([105, 125, 145, 165, 185] * 20)  # 100 data points
        max_hr = 200
        
        zones = analyzer._calculate_hr_zones(hr_data, max_hr)
        
        assert isinstance(zones, dict)
        assert len(zones) == 5
        assert all(0 <= percentage <= 100 for percentage in zones.values())
        # Note: Heart rate zones can overlap, so total may be > 100%
    
    def test_calculate_power_zones(self):
        """Test power zones calculation."""
        analyzer = ActivityAnalyzer()
        
        # Create sample power data
        power_data = pd.Series([150, 200, 250, 300, 350] * 20)  # 100 data points
        ftp = 250
        
        zones = analyzer._calculate_power_zones(power_data, ftp)
        
        assert isinstance(zones, dict)
        assert len(zones) == 6
        assert all(0 <= percentage <= 100 for percentage in zones.values())
    
    def test_analyze_basic_metrics(self):
        """Test basic metrics analysis."""
        analyzer = ActivityAnalyzer()
        
        session_data = {
            'total_elapsed_time': 3600,
            'total_timer_time': 3500,
            'total_distance': 10000,
            'total_ascent': 100,
            'total_calories': 500
        }
        
        metrics = analyzer._analyze_basic_metrics(session_data, None)
        
        assert 'total_duration' in metrics
        assert 'moving_duration' in metrics
        assert 'total_distance_km' in metrics
        assert metrics['total_distance_km'] == 10.0
        assert 'calories_per_hour' in metrics
        assert metrics['calories_per_hour'] > 0


class TestFitAnalysisAgent:
    """Tests for FitAnalysisAgent class."""
    
    def test_init_without_api_key(self):
        """Test agent initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key required"):
                FitAnalysisAgent()
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_format_data_for_llm(self):
        """Test data formatting for LLM."""
        # Create a minimal mock that doesn't trigger the LLMChain validation
        with patch('jules_app.agent.ChatOpenAI') as mock_chat:
            with patch.object(FitAnalysisAgent, '_setup_chains'):
                agent = FitAnalysisAgent()
                
                test_data = {
                    'sport': 'cycling',
                    'duration': 3600,
                    'metrics': {
                        'avg_power': 200,
                        'max_power': 400
                    },
                    'zones': ['Zone 1', 'Zone 2']
                }
                
                formatted = agent._format_data_for_llm(test_data, "Test Data")
                
                assert isinstance(formatted, str)
                assert "Test Data" in formatted
                assert "sport: cycling" in formatted
                assert "avg_power: 200" in formatted
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_extract_key_metrics(self):
        """Test key metrics extraction."""
        with patch('jules_app.agent.ChatOpenAI'):
            with patch.object(FitAnalysisAgent, '_setup_chains'):
                agent = FitAnalysisAgent()
                
                analysis_data = {
                    'activity_summary': {
                        'sport': 'running',
                        'total_timer_time': 3600,
                        'total_distance': 10000,
                        'avg_heart_rate': 150,
                        'total_calories': 500
                    },
                    'detailed_analysis': {
                        'training_zones': {
                            'Zone 1': 20,
                            'Zone 2': 60,
                            'Zone 3': 20
                        }
                    }
                }
                
                key_metrics = agent._extract_key_metrics(analysis_data)
                
                assert key_metrics['sport'] == 'running'
                assert key_metrics['duration'] == 3600
                assert key_metrics['avg_heart_rate'] == 150
                assert 'training_zones' in key_metrics


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_sample_activity_data_analysis(self):
        """Test analysis with sample activity data."""
        # Create sample activity data
        activity_data = {
            'session_info': {
                'sport': 'cycling',
                'total_timer_time': 3600,
                'total_distance': 25000,
                'avg_heart_rate': 145,
                'avg_power': 200,
                'total_calories': 800
            },
            'records': [],
            'records_df': pd.DataFrame({
                'heart_rate': [140, 145, 150, 155, 160] * 20,
                'power': [180, 200, 220, 240, 200] * 20,
                'speed': [10, 11, 12, 11, 10] * 20
            }),
            'laps': [],
            'device_info': {},
            'hr_zones': [],
            'power_zones': [],
            'events': []
        }
        
        # Test analyzer
        analyzer = ActivityAnalyzer()
        analysis = analyzer.analyze_activity(activity_data)
        
        assert 'basic_metrics' in analysis
        assert 'heart_rate_analysis' in analysis
        assert 'power_analysis' in analysis
        assert 'training_zones' in analysis
    
    def test_parser_summary_generation(self):
        """Test summary generation from mock data."""
        parser = FitFileParser()
        
        # Mock activity data
        activity_data = {
            'session_info': {
                'sport': 'running',
                'total_timer_time': 2400,
                'total_distance': 8000,
                'avg_heart_rate': 155,
                'total_calories': 400
            },
            'records_df': pd.DataFrame({
                'heart_rate': [150, 155, 160, 165, 155] * 10
            })
        }
        
        summary = parser.get_activity_summary(activity_data)
        
        assert summary['sport'] == 'running'
        assert summary['total_timer_time'] == 2400
        assert summary['total_distance'] == 8000
        assert summary['avg_heart_rate'] == 155


if __name__ == '__main__':
    pytest.main([__file__])