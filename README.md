# Jules App - AI-Powered FIT File Analysis

An intelligent agent that uses LangChain to analyze FIT (Flexible and Interoperable Data Transfer) files and provide comprehensive insights about fitness activities.

## Features

- **Comprehensive FIT File Parsing**: Extract all relevant data from FIT files including heart rate, power, GPS, cadence, and more
- **Advanced Analytics**: Calculate training zones, performance metrics, efficiency indicators, and fatigue markers
- **AI-Powered Insights**: Use LangChain and OpenAI to generate human-readable analysis and recommendations
- **Multiple Analysis Types**: Choose from comprehensive, summary, or technical analysis modes
- **Comparative Analysis**: Compare multiple activities to identify trends and patterns
- **Training Recommendations**: Get specific, actionable training advice based on your data
- **Athlete-Specific Analysis**: Customize analysis based on athlete age, weight, FTP, and other parameters

## Installation

### Requirements

- Python 3.8 or higher
- OpenAI API key

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install with optional development dependencies:

```bash
pip install -e ".[dev]"
```

### Environment Setup

Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Or set the environment variable directly:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

### Command Line Interface

Analyze a single FIT file:
```bash
python -m jules_app.cli analyze activity.fit
```

Get a quick summary:
```bash
python -m jules_app.cli analyze activity.fit --type summary
```

Include athlete information for better analysis:
```bash
python -m jules_app.cli analyze activity.fit --athlete-age 30 --athlete-weight 70 --athlete-ftp 250
```

Compare multiple activities:
```bash
python -m jules_app.cli compare activity1.fit activity2.fit activity3.fit
```

Get training recommendations:
```bash
python -m jules_app.cli recommendations activity.fit
```

### Python API

```python
from jules_app import FitAnalysisAgent

# Initialize the agent
agent = FitAnalysisAgent()

# Analyze a FIT file
result = agent.analyze_fit_file("activity.fit", analysis_type="comprehensive")

# Print AI-generated insights
print(result['ai_analysis']['content'])

# Analyze with athlete information
athlete_info = {
    'age': 30,
    'weight': 70.0,  # kg
    'ftp': 250       # watts
}

result = agent.analyze_fit_file(
    "activity.fit", 
    analysis_type="comprehensive",
    athlete_info=athlete_info
)
```

## Analysis Types

### Comprehensive Analysis
Provides detailed technical analysis combined with AI-powered insights including:
- Performance metrics and trends
- Training zone distribution
- Pacing strategy evaluation
- Physiological insights
- Training recommendations
- Recovery considerations

### Summary Analysis
Quick, conversational overview perfect for:
- Post-workout summaries
- Sharing highlights
- Quick performance checks

### Technical Analysis
Raw technical data without AI interpretation, useful for:
- Data export
- Custom analysis
- Integration with other tools

## Supported Data

The agent can analyze any FIT file and will adapt its analysis based on available data:

- **Heart Rate**: Zone analysis, drift calculation, efficiency metrics
- **Power** (cycling): Normalized power, intensity factor, TSS, power zones
- **GPS**: Speed, pace, elevation analysis
- **Cadence**: Running or cycling cadence analysis
- **Temperature**: Environmental factor analysis
- **Laps**: Structured workout analysis

## Architecture

The system consists of three main components:

### 1. FitFileParser (`jules_app.parser`)
- Parses FIT files using the `fitparse` library
- Extracts and organizes all available data
- Calculates basic metrics and summaries

### 2. ActivityAnalyzer (`jules_app.analyzer`)
- Performs detailed technical analysis
- Calculates advanced metrics (normalized power, training zones, etc.)
- Generates performance insights and efficiency metrics

### 3. FitAnalysisAgent (`jules_app.agent`)
- Orchestrates the analysis pipeline
- Uses LangChain to generate AI-powered insights
- Provides multiple analysis modes and output formats

## Examples

See `examples/usage_examples.py` for comprehensive examples including:
- Basic FIT file analysis
- Athlete-specific analysis
- Multiple activity comparison
- Training recommendations
- Programmatic usage

## Configuration

### LLM Models
The agent supports different OpenAI models:

```python
# Use GPT-4 for more detailed analysis
agent = FitAnalysisAgent(model_name="gpt-4", temperature=0.3)

# Use GPT-3.5-turbo for faster, cost-effective analysis
agent = FitAnalysisAgent(model_name="gpt-3.5-turbo", temperature=0.3)
```

### Athlete Information
Enhance analysis accuracy by providing athlete-specific data:

```python
athlete_info = {
    'age': 30,           # For accurate HR zones
    'weight': 70.0,      # For power-to-weight calculations
    'ftp': 250,          # For cycling power zones
    'max_hr': 190        # Override estimated max HR
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black jules_app/
flake8 jules_app/
```

### Adding New Analysis Features

1. Add metrics calculation to `ActivityAnalyzer`
2. Update prompt templates in `FitAnalysisAgent` if needed
3. Add corresponding tests

## Limitations

- Requires OpenAI API key (costs apply)
- Analysis quality depends on data availability in FIT files
- Some advanced metrics require specific data types (e.g., power for cycling)
- Historical trend analysis requires multiple activities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code follows formatting guidelines
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the examples in `examples/usage_examples.py`
2. Review the API documentation in the code
3. Open an issue on GitHub

## Acknowledgments

- Built with [LangChain](https://langchain.com/) for AI capabilities
- Uses [fitparse](https://github.com/dtcooper/python-fitparse) for FIT file parsing
- Powered by OpenAI's language models for intelligent analysis