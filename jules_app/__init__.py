"""
Jules App - AI Agent for FIT File Analysis

This package provides an AI agent that uses LangChain to analyze FIT files
and provide comprehensive insights about fitness activities.
"""

__version__ = "0.1.0"
__author__ = "Jules App"

from .agent import FitAnalysisAgent
from .parser import FitFileParser
from .analyzer import ActivityAnalyzer

__all__ = ["FitAnalysisAgent", "FitFileParser", "ActivityAnalyzer"]