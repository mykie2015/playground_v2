# Google ADK (Agent Development Kit) with Gemini API

This implementation demonstrates how to use Google's Agent Development Kit (ADK) with Gemini 2.5 Pro model in Google Colab.

## Overview

Google's Agent Development Kit (ADK) is a framework for developing and deploying AI agents that can perform complex tasks and workflows. This implementation provides examples of various agent types:

1. **Simple Agent**: A basic agent that uses Gemini to answer questions
2. **Weather Agent**: An agent that uses tools to fetch weather and time information
3. **Code Optimization Agent**: A pipeline of agents that write, review, and refactor code

## Setup Instructions

### Requirements

- Google Colab environment
- Gemini API key
- For weather agent: WeatherAPI.com API key (optional)

### Installation

1. Upload these files to your Google Drive or use them directly in Colab
2. Install required packages:
   ```
   !pip install -r requirements.txt
   ```
3. Set your API key in the notebook:
   ```python
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
   ```

### Files

- `adk_gemini_agent.py`: Main implementation file with agent classes and utility functions
- `adk_gemini_colab.ipynb`: Colab notebook with examples and demonstrations
- `requirements.txt`: Required packages
- `README.md`: This file

## Usage

Open the `adk_gemini_colab.ipynb` notebook in Google Colab and follow the instructions there. You can run the provided examples or create your own custom queries.

### Example: Simple Agent

```python
aivi_agent = AiviAgentExample()
response = aivi_agent.run_agent(
    agent_type="simple", 
    query="What are the key features of Google's Agent Development Kit (ADK)?"
)
```

### Example: Weather Agent

```python
response = aivi_agent.run_agent(
    agent_type="weather", 
    query="What's the current weather in New York?"
)
```

### Example: Code Optimization Agent

```python
response = aivi_agent.run_agent(
    agent_type="code", 
    query="Optimize this code: import urllib.request\ncontents = urllib.request.urlopen('https://www.aivi.fyi/').read()"
)
```

## Resources

- Original source: [AIVI.fyi - Introduce ADK](https://www.aivi.fyi/aiagents/introduce-ADK)
- [Google ADK Documentation](https://github.com/google/adk)
- [Gemini API Documentation](https://ai.google.dev/docs/gemini_api_overview)

## License

This implementation is for educational purposes only. See Google's licensing for ADK and Gemini API usage. 