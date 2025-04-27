"""
Google ADK (Agent Development Kit) Implementation for Colab
Using Gemini 2.5 Pro Preview model

Based on: https://www.aivi.fyi/aiagents/introduce-ADK
"""

# Required package installations (uncomment if needed in Colab)
# !pip install google-adk litellm mcp mcp-server-fetch

import os
import datetime
import requests
from google.adk.agents import Agent, LlmAgent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.models.lite_llm import LiteLlm

# Set your API key
GOOGLE_API_KEY = "AIzaSyADE1ZQ2-vyNz1qGGY1Mz3TWZhOfKEzfLw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# City name mappings (Chinese to English)
CITY_NAME_MAP = {
    "纽约": "New York",
    "伦敦": "London",
    "东京": "Tokyo",
    "北京": "Beijing",
    "上海": "Shanghai",
    "巴黎": "Paris",
    "柏林": "Berlin",
    "悉尼": "Sydney",
    "莫斯科": "Moscow",
    "迪拜": "Dubai",
}

def get_weather(city: str) -> dict:
    """Gets current weather report for the specified city.
    Uses weatherapi.com API to get real-time weather data.
    Supports Chinese city names, converting them to English internally.
    
    Args:
        city (str): City name to get weather for (Chinese or English).
        
    Returns:
        dict: Dictionary with status and result or error information.
    """
    # You need to register for a free API key at weatherapi.com
    api_key = "YOUR_WEATHERAPI_KEY"  # Replace with your actual key
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    # Check if city name needs conversion to English
    query_city = CITY_NAME_MAP.get(city, city)
    
    try:
        # Build API request
        params = {
            "key": api_key,
            "q": query_city
        }
        
        # Send GET request to weather API
        response = requests.get(base_url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            # Extract relevant weather information
            location = data["location"]["name"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            temp_f = data["current"]["temp_f"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            
            # Build weather report (using original input city name)
            report = (
                f"Current weather in {city} ({country}) is {condition}, "
                f"temperature {temp_c}°C ({temp_f}°F), "
                f"humidity {humidity}%, wind speed {wind_kph} km/h."
            )
            
            return {
                "status": "success",
                "report": report,
            }
        else:
            # Handle API errors
            return {
                "status": "error",
                "error_message": f"Could not get weather for '{city}'. API response code: {response.status_code}, please check if city name is correct."
            }
    except Exception as e:
        # Handle other exceptions
        return {
            "status": "error",
            "error_message": f"Error getting weather for '{city}': {str(e)}"
        }

def get_current_time(city: str) -> dict:
    """Gets current time for the specified city.
    Uses weatherapi.com API to get timezone information for the city,
    then calculates current time based on timezone.
    Supports Chinese city names, converting them to English internally.
    
    Args:
        city (str): City name to get current time for (Chinese or English).
        
    Returns:
        dict: Dictionary with status and result or error information.
    """
    # API key and base URL (same as weather API)
    api_key = "YOUR_WEATHERAPI_KEY"  # Replace with your actual key
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    # Check if city name needs conversion to English
    query_city = CITY_NAME_MAP.get(city, city)
    
    try:
        # Build API request
        params = {
            "key": api_key,
            "q": query_city
        }
        
        # Send GET request to API to get timezone information
        response = requests.get(base_url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            # Extract timezone ID and local time
            tz_id = data["location"]["tz_id"]
            localtime = data["location"]["localtime"]
            
            # Build time report (using original input city name)
            report = f"Current time in {city} is {localtime} ({tz_id} timezone)"
            
            return {
                "status": "success",
                "report": report
            }
        else:
            # Handle API errors
            return {
                "status": "error",
                "error_message": f"Could not get timezone for '{city}'. API response code: {response.status_code}, please check if city name is correct."
            }
    except Exception as e:
        # Handle other exceptions
        return {
            "status": "error",
            "error_message": f"Error getting time information for '{city}': {str(e)}"
        }

class AiviAgentExample:
    """Examples of different types of agents using Google's ADK framework"""
    
    def __init__(self):
        """Initialize the class with session service and other common components"""
        self.session_service = InMemorySessionService()
        self.artifacts_service = InMemoryArtifactService()
        
    def create_simple_agent(self):
        """Create the simplest possible agent using Gemini 2.5 Pro"""
        return Agent(
            name="simple_assistant",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            instruction="You are a helpful assistant.",
            description="A helpful assistant."
        )
    
    def create_weather_agent(self):
        """Create a weather and time agent with tools"""
        return Agent(
            name="weather_time_agent",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            description="Smart assistant that can answer questions about weather and time in various cities.",
            instruction=(
                "I'm a smart assistant that can provide weather and time information for cities."
                "When a user asks about the weather in a city, use the get_weather tool to get the latest weather data."
                "When a user asks about the current time in a city, use the get_current_time tool to get the accurate time."
                "Please respond to user inquiries in a friendly manner and provide complete weather or time information."
                "I can understand Chinese city names and automatically convert them to corresponding English names."
            ),
            tools=[get_weather, get_current_time],
        )
    
    def create_code_optimization_agent(self):
        """Create a sequential agent pipeline for code optimization"""
        # Code writer agent
        code_writer_agent = LlmAgent(
            name="CodeWriterAgent",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            instruction="""You are a code writing AI.
            Write initial Python code based on user's request.
            Output only the raw code block.
            """,
            description="Write initial code based on specifications.",
            output_key="generated_code"
        )
        
        # Code reviewer agent
        code_reviewer_agent = LlmAgent(
            name="CodeReviewerAgent",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            instruction="""You are a code review AI.
            Review the Python code in the session state with key 'generated_code'.
            Provide constructive feedback about potential errors, style issues, or improvements.
            Focus on clarity and correctness.
            Output only the review comments.
            """,
            description="Review code and provide feedback.",
            output_key="review_comments"
        )
        
        # Code refactorer agent
        code_refactorer_agent = LlmAgent(
            name="CodeRefactorerAgent",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            instruction="""You are a code refactoring AI.
            Get the original Python code from session state key 'generated_code'
            and the review comments from session state key 'review_comments'.
            Refactor the original code to address the feedback and improve its quality.
            Output only the final, refactored code block.
            """,
            description="Refactor code based on review comments.",
            output_key="refactored_code"
        )
        
        # Create a sequential agent to orchestrate the pipeline
        from google.adk.agents.sequential_agent import SequentialAgent
        
        code_pipeline_agent = SequentialAgent(
            name="CodePipelineAgent",
            sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent]
        )
        
        # Create the root agent that uses the pipeline
        return Agent(
            name="CodeAssistant",
            model="gemini-2.5-pro-preview-03-25",  # Using the specified model
            instruction="""You are a code assistant AI.
            Your role is to help users improve code through a three-step pipeline:
            1. Write initial code based on specifications
            2. Review code to identify issues and improvements
            3. Refactor code based on review feedback
            Present the final, refactored code to the user as your response.
            """,
            description="Assistant that improves code through a write-review-refactor pipeline.",
            tools=[],
            sub_agents=[code_pipeline_agent]
        )
    
    def run_agent(self, agent_type="simple", query="Hello, how can you help me?"):
        """Run the specified agent with the given query
        
        Args:
            agent_type (str): Type of agent to run ("simple", "weather", or "code")
            query (str): Query to send to the agent
            
        Returns:
            str: Agent's response
        """
        # Create the appropriate agent
        if agent_type == "weather":
            agent = self.create_weather_agent()
        elif agent_type == "code":
            agent = self.create_code_optimization_agent()
        else:  # default to simple
            agent = self.create_simple_agent()
        
        # Set up session
        session = self.session_service.create_session(
            state={}, app_name='aivi_agent_demo', user_id='user_demo'
        )
        
        # Create runner
        runner = Runner(
            app_name='aivi_agent_demo',
            agent=agent,
            artifact_service=self.artifacts_service,
            session_service=self.session_service,
        )
        
        # Create user content
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent
        print(f"Running {agent_type} agent with query: '{query}'")
        
        responses = []
        events = runner.run(
            session_id=session.id, user_id=session.user_id, new_message=content
        )
        
        # Process events
        for event in events:
            if event.is_final_response():
                response = event.content.parts[0].text
                responses.append(response)
                print(f"Agent response: {response}")
        
        return '\n'.join(responses)

# Example code to be included in a Colab notebook
def colab_demo():
    """Run demo in Colab"""
    aivi_agent = AiviAgentExample()
    
    # Example 1: Simple agent
    simple_response = aivi_agent.run_agent(
        agent_type="simple", 
        query="What are the key features of Google's Agent Development Kit (ADK)?"
    )
    
    # Example 2: Weather agent
    weather_response = aivi_agent.run_agent(
        agent_type="weather", 
        query="What's the current weather in New York?"
    )
    
    # Example 3: Code optimization agent
    code_response = aivi_agent.run_agent(
        agent_type="code", 
        query="Optimize this code: import urllib.request\ncontents = urllib.request.urlopen('https://www.aivi.fyi/').read()"
    )
    
    return {
        "simple_agent": simple_response,
        "weather_agent": weather_response,
        "code_agent": code_response
    }

if __name__ == "__main__":
    # This will only run when the script is executed directly
    # (not when imported as a module)
    colab_demo() 