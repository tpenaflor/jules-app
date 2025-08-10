"""
FIT File Analysis AI Agent using LangChain

This module provides an AI agent that analyzes FIT files and generates
comprehensive, human-readable reports about fitness activities.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import BaseOutputParser
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "LangChain dependencies missing. Install with: pip install langchain langchain-openai python-dotenv"
    )

from .parser import FitFileParser
from .analyzer import ActivityAnalyzer


class AnalysisReport(BaseOutputParser):
    """Custom output parser for structured analysis reports."""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the LLM output into a structured report."""
        try:
            # Try to parse as JSON first
            return json.loads(text)
        except json.JSONDecodeError:
            # If not JSON, return as structured text
            return {
                "analysis": text,
                "timestamp": datetime.now().isoformat(),
                "format": "text"
            }


class FitAnalysisAgent:
    """
    AI Agent for comprehensive FIT file analysis using LangChain.
    
    This agent combines technical fitness data analysis with AI-powered insights
    to provide comprehensive, human-readable reports about athletic activities.
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.3):
        """
        Initialize the FIT Analysis Agent.
        
        Args:
            openai_api_key: OpenAI API key (if not provided, will look for OPENAI_API_KEY env var)
            model_name: LLM model to use for analysis
            temperature: Temperature for LLM responses (0.0 = deterministic, 1.0 = creative)
        """
        # Load environment variables
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize API key
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass it directly."
            )
        
        # Initialize components
        self.parser = FitFileParser()
        self.analyzer = ActivityAnalyzer()
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=self.api_key
        )
        
        self.output_parser = AnalysisReport()
        
        # Create analysis prompt templates
        self._setup_prompts()
        
        # Create analysis chains
        self._setup_chains()
    
    def _setup_prompts(self):
        """Set up prompt templates for different types of analysis."""
        
        # Main comprehensive analysis prompt
        self.comprehensive_analysis_prompt = ChatPromptTemplate.from_template("""
You are an expert fitness coach and sports scientist analyzing a workout from FIT file data. 
Provide a comprehensive, insightful analysis that would be valuable to an athlete.

ACTIVITY DATA:
{activity_summary}

DETAILED ANALYSIS:
{detailed_analysis}

Please provide a comprehensive analysis covering:

1. **Activity Overview**: Summarize the key details of this workout
2. **Performance Analysis**: Analyze the athlete's performance including strengths and areas for improvement
3. **Training Zones**: Explain time spent in different training zones and what this means
4. **Pacing Strategy**: Evaluate the pacing strategy used during the activity
5. **Physiological Insights**: Interpret heart rate, power (if available), and other physiological data
6. **Training Recommendations**: Suggest specific improvements or training focuses based on this data
7. **Recovery Considerations**: Advise on recovery needs based on the intensity and duration

Make your analysis specific, actionable, and tailored to the data provided. Use sports science principles 
and avoid generic advice. If certain data is missing, acknowledge it and work with what's available.

Format your response as a well-structured analysis with clear sections and bullet points where appropriate.
""")
        
        # Quick summary prompt
        self.quick_summary_prompt = ChatPromptTemplate.from_template("""
Provide a concise but informative summary of this fitness activity:

ACTIVITY DATA:
{activity_summary}

Create a brief summary (2-3 paragraphs) that captures:
- What type of activity this was and its key metrics
- The most notable aspects of the performance
- One key insight or recommendation

Keep it conversational and engaging, as if you're a coach talking to an athlete.
""")
        
        # Comparative analysis prompt (for multiple activities)
        self.comparative_analysis_prompt = ChatPromptTemplate.from_template("""
Compare and analyze these fitness activities to identify trends and patterns:

ACTIVITIES DATA:
{activities_data}

Provide an analysis that includes:
1. **Performance Trends**: How has performance changed across these activities?
2. **Training Patterns**: What patterns do you see in training intensity, duration, or focus?
3. **Areas of Improvement**: What specific areas should the athlete focus on?
4. **Training Recommendations**: Based on these patterns, what training adjustments would you recommend?

Focus on actionable insights that can help improve future performance.
""")
    
    def _setup_chains(self):
        """Set up LangChain chains for different analysis types."""
        
        self.comprehensive_chain = LLMChain(
            llm=self.llm,
            prompt=self.comprehensive_analysis_prompt,
            output_parser=self.output_parser
        )
        
        self.summary_chain = LLMChain(
            llm=self.llm,
            prompt=self.quick_summary_prompt,
            output_parser=self.output_parser
        )
        
        self.comparative_chain = LLMChain(
            llm=self.llm,
            prompt=self.comparative_analysis_prompt,
            output_parser=self.output_parser
        )
    
    def analyze_fit_file(self, 
                        file_path: str, 
                        analysis_type: str = "comprehensive",
                        athlete_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a FIT file and generate an AI-powered report.
        
        Args:
            file_path: Path to the FIT file
            analysis_type: Type of analysis ("comprehensive", "summary", or "technical")
            athlete_info: Optional athlete information (age, weight, FTP, etc.)
            
        Returns:
            Dict containing the analysis report and raw data
        """
        try:
            # Step 1: Parse the FIT file
            self.logger.info(f"Parsing FIT file: {file_path}")
            raw_data = self.parser.parse_fit_file(file_path)
            
            # Step 2: Generate activity summary
            activity_summary = self.parser.get_activity_summary(raw_data)
            
            # Step 3: Perform detailed analysis
            detailed_analysis = self.analyzer.analyze_activity(raw_data)
            
            # Step 4: Enhance with athlete-specific info if provided
            if athlete_info:
                detailed_analysis = self._enhance_with_athlete_info(detailed_analysis, athlete_info)
            
            # Step 5: Generate AI analysis based on type
            ai_analysis = self._generate_ai_analysis(
                activity_summary, 
                detailed_analysis, 
                analysis_type
            )
            
            # Step 6: Compile final report
            report = {
                "file_path": file_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type,
                "activity_summary": activity_summary,
                "detailed_analysis": detailed_analysis,
                "ai_analysis": ai_analysis,
                "raw_data_summary": {
                    "total_records": len(raw_data.get('records', [])),
                    "total_laps": len(raw_data.get('laps', [])),
                    "has_heart_rate": 'heart_rate' in raw_data.get('records_df', {}).columns if raw_data.get('records_df') is not None else False,
                    "has_power": 'power' in raw_data.get('records_df', {}).columns if raw_data.get('records_df') is not None else False,
                    "has_gps": any(['position_lat' in raw_data.get('records_df', {}).columns, 
                                   'position_long' in raw_data.get('records_df', {}).columns]) if raw_data.get('records_df') is not None else False
                }
            }
            
            self.logger.info("FIT file analysis completed successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Error analyzing FIT file {file_path}: {str(e)}")
            raise
    
    def _enhance_with_athlete_info(self, analysis: Dict[str, Any], athlete_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis with athlete-specific information."""
        
        # Add athlete-specific calculations
        if 'age' in athlete_info:
            max_hr_estimated = 220 - athlete_info['age']
            analysis['athlete_specific'] = {
                'estimated_max_hr': max_hr_estimated,
                'age': athlete_info['age']
            }
        
        if 'weight' in athlete_info:
            analysis['athlete_specific'] = analysis.get('athlete_specific', {})
            analysis['athlete_specific']['weight'] = athlete_info['weight']
            
            # Calculate power-to-weight ratio if power data available
            if 'power_analysis' in analysis and analysis['power_analysis'].get('avg_power'):
                power_to_weight = analysis['power_analysis']['avg_power'] / athlete_info['weight']
                analysis['athlete_specific']['power_to_weight_ratio'] = power_to_weight
        
        if 'ftp' in athlete_info:
            analysis['athlete_specific'] = analysis.get('athlete_specific', {})
            analysis['athlete_specific']['ftp'] = athlete_info['ftp']
            
            # Recalculate power zones based on actual FTP
            if 'power_analysis' in analysis:
                power_data = analysis.get('raw_power_data')  # Would need to pass this through
                if power_data is not None:
                    analysis['power_analysis']['power_zones'] = self.analyzer._calculate_power_zones(
                        power_data, athlete_info['ftp']
                    )
        
        return analysis
    
    def _generate_ai_analysis(self, 
                             activity_summary: Dict[str, Any],
                             detailed_analysis: Dict[str, Any],
                             analysis_type: str) -> Dict[str, Any]:
        """Generate AI-powered analysis using LangChain."""
        
        # Prepare data for the LLM
        summary_text = self._format_data_for_llm(activity_summary, "Activity Summary")
        analysis_text = self._format_data_for_llm(detailed_analysis, "Detailed Analysis")
        
        try:
            if analysis_type == "comprehensive":
                result = self.comprehensive_chain.run(
                    activity_summary=summary_text,
                    detailed_analysis=analysis_text
                )
            elif analysis_type == "summary":
                result = self.summary_chain.run(
                    activity_summary=summary_text
                )
            else:  # technical
                # For technical analysis, return the detailed analysis as-is
                result = {
                    "analysis": "Technical analysis complete",
                    "note": "This is the raw technical analysis without AI interpretation"
                }
            
            return {
                "type": analysis_type,
                "content": result,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI analysis: {str(e)}")
            return {
                "type": analysis_type,
                "content": f"Error generating AI analysis: {str(e)}",
                "error": True,
                "generated_at": datetime.now().isoformat()
            }
    
    def _format_data_for_llm(self, data: Dict[str, Any], section_title: str) -> str:
        """Format analysis data for LLM consumption."""
        
        def format_value(key: str, value: Any, indent: int = 0) -> str:
            prefix = "  " * indent
            
            if isinstance(value, dict):
                result = f"{prefix}{key}:\n"
                for k, v in value.items():
                    result += format_value(k, v, indent + 1)
                return result
            elif isinstance(value, list):
                if len(value) == 0:
                    return f"{prefix}{key}: (empty)\n"
                result = f"{prefix}{key}:\n"
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result += f"{prefix}  Item {i+1}:\n"
                        for k, v in item.items():
                            result += format_value(k, v, indent + 2)
                    else:
                        result += f"{prefix}  - {item}\n"
                return result
            else:
                # Format numeric values nicely
                if isinstance(value, float):
                    if value > 100 or value < 0.01:
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)
                return f"{prefix}{key}: {formatted_value}\n"
        
        result = f"=== {section_title} ===\n"
        for key, value in data.items():
            result += format_value(key, value)
        
        return result
    
    def analyze_multiple_activities(self, 
                                  file_paths: List[str],
                                  athlete_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze multiple FIT files and provide comparative insights.
        
        Args:
            file_paths: List of paths to FIT files
            athlete_info: Optional athlete information
            
        Returns:
            Dict containing comparative analysis
        """
        activities_data = []
        
        # Analyze each activity
        for file_path in file_paths:
            try:
                analysis = self.analyze_fit_file(file_path, "technical", athlete_info)
                activities_data.append({
                    "file_path": file_path,
                    "activity_summary": analysis["activity_summary"],
                    "key_metrics": self._extract_key_metrics(analysis)
                })
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {str(e)}")
                continue
        
        if not activities_data:
            raise ValueError("No activities could be successfully analyzed")
        
        # Generate comparative analysis
        activities_text = self._format_data_for_llm(activities_data, "Activities Comparison")
        
        try:
            comparative_result = self.comparative_chain.run(
                activities_data=activities_text
            )
            
            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "total_activities": len(activities_data),
                "activities_analyzed": [a["file_path"] for a in activities_data],
                "comparative_analysis": comparative_result,
                "individual_summaries": activities_data
            }
            
        except Exception as e:
            self.logger.error(f"Error generating comparative analysis: {str(e)}")
            raise
    
    def _extract_key_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from a full analysis for comparison."""
        summary = analysis.get("activity_summary", {})
        detailed = analysis.get("detailed_analysis", {})
        
        key_metrics = {
            "sport": summary.get("sport"),
            "duration": summary.get("total_timer_time"),
            "distance": summary.get("total_distance"),
            "avg_heart_rate": summary.get("avg_heart_rate"),
            "max_heart_rate": summary.get("max_heart_rate"),
            "avg_power": summary.get("avg_power"),
            "calories": summary.get("total_calories")
        }
        
        # Add training zone distribution if available
        if "training_zones" in detailed:
            key_metrics["training_zones"] = detailed["training_zones"]
        
        return {k: v for k, v in key_metrics.items() if v is not None}
    
    def generate_training_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific training recommendations based on analysis."""
        
        recommendations_prompt = ChatPromptTemplate.from_template("""
Based on this fitness activity analysis, provide specific, actionable training recommendations:

ANALYSIS DATA:
{analysis_data}

Provide recommendations in these categories:
1. **Immediate Recovery**: What should the athlete do in the next 24-48 hours?
2. **Next Workout**: What type of workout should follow this one?
3. **Weekly Training Focus**: What should be the focus for the upcoming week?
4. **Technique Improvements**: Any specific technique or pacing improvements?
5. **Long-term Development**: What areas need development over the next month?

Make recommendations specific to the data shown and avoid generic advice.
""")
        
        chain = LLMChain(llm=self.llm, prompt=recommendations_prompt)
        
        analysis_text = self._format_data_for_llm(analysis, "Activity Analysis")
        
        try:
            recommendations = chain.run(analysis_data=analysis_text)
            return {
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "based_on_file": analysis.get("file_path", "unknown")
            }
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "error": f"Could not generate recommendations: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }