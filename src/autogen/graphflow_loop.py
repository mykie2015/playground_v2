"""
Simple implementation of a conditional loop workflow with approval/revision pattern.
This uses a simple direct approach without relying on specific GraphFlow features.
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient
from graphflow_parallel import visualize_digraph
from dotenv import load_dotenv

load_dotenv()

# Function to call OpenAI API directly
def call_openai(system_prompt: str, user_content: str) -> str:
    """Call OpenAI API directly without using client libraries"""
    api_key = os.getenv("OPENAI_API_KEY")
    # Always use the correct endpoint for OpenAI chat completions
    base_url = os.getenv("OPENAI_API_BASE")
    if base_url:
        # If user provides a custom base, ensure it ends with /chat/completions
        if not base_url.rstrip("/").endswith("chat/completions"):
            base_url = base_url.rstrip("/") + "/chat/completions"
    else:
        base_url = "https://api.openai.com/v1/chat/completions"
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(base_url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return f"Error calling API: {response.status_code}"

# Define system prompts for each agent
WRITER_PROMPT = """
You are a tennis expert who creates clear, helpful content about tennis techniques.
Your task is to write a short paragraph (150-200 words) on changing from arm-lead to core-lead in tennis strokes.
Focus on explaining the concept, benefits, and practical tips for implementation.
Be precise, practical, and engaging.
"""

REVIEWER_PROMPT = """
You are a tennis publication editor who reviews content for clarity, accuracy, and helpfulness.
Review the paragraph about changing from arm-lead to core-lead in tennis strokes.
If the content needs improvement, respond with:
"REVISE: [your specific feedback for improvements]"

If the content is ready for publication, respond with:
"APPROVE: [brief positive feedback on the content]"

Your feedback should be specific and actionable when revisions are needed.
"""

def create_workflow_diagram():
    """Create a simple ASCII workflow diagram"""
    diagram = """
    ┌─────────┐     ┌─────────┐
    │         │     │         │
    │  Writer ├────►│ Reviewer│
    │         │     │         │
    └────▲────┘     └────┬────┘
         │               │
         │    REVISE     │
         └───────────────┘
                         │
                         │ APPROVE
                         ▼
                     ┌────────┐
                     │        │
                     │  Done  │
                     │        │
                     └────────┘
    """
    print(diagram)

# Create an OpenAI model client
client = OpenAIChatCompletionClient(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Define agents
writer = AssistantAgent(
    "writer",
    model_client=client,
    system_message="You are a tennis expert who creates clear, helpful content about tennis techniques. Your task is to write a short paragraph (150-200 words) on changing from arm-lead to core-lead in tennis strokes. Focus on explaining the concept, benefits, and practical tips for implementation. Be precise, practical, and engaging."
)

reviewer = AssistantAgent(
    "reviewer",
    model_client=client,
    system_message="You are a tennis publication editor who reviews content for clarity, accuracy, and helpfulness. Review the paragraph about changing from arm-lead to core-lead in tennis strokes. If the content needs improvement, respond with: 'REVISE: [your specific feedback for improvements]'. If the content is ready for publication, respond with: 'APPROVE: [brief positive feedback on the content]'. Your feedback should be specific and actionable when revisions are needed."
)

done = AssistantAgent(
    "done",
    model_client=client,
    system_message="This is the end of the workflow."
)

task = "Write a short paragraph about changing from arm-lead to core-lead in tennis strokes."
start = AssistantAgent("start", model_client=client, system_message=task)

# Build the workflow graph
builder = DiGraphBuilder()
builder.add_node(start).add_node(writer).add_node(reviewer).add_node(done)
builder.add_edge(start, writer)
builder.add_edge(writer, reviewer)
builder.add_edge(reviewer, writer, condition="REVISE")
builder.add_edge(reviewer, done, condition="APPROVE")

graph = builder.build()

flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)

async def main():
    print("\n" + "="*80)
    print("STARTING GRAPHFLOW LOOP (APPROVAL/REVISION)")
    print("="*80 + "\n")
    print(f"Task: {task}\n")
    visualize_digraph(builder, graph, output_path="graphflow_loop_visualization.png")
    messages_by_source = {}
    print("\nRunning the workflow...\n")
    stream = flow.run_stream(task=task)
    async for event in stream:
        if hasattr(event, 'source') and hasattr(event, 'content'):
            if event.source not in ['user', 'DiGraphStopAgent']:
                messages_by_source[event.source] = event.content
                print(f"--- Agent {event.source} has completed their task ---")

    print("\n" + "="*80)
    print("WRITER'S FINAL DRAFT")
    print("="*80)
    if 'writer' in messages_by_source:
        print(messages_by_source['writer'])
    print("\n" + "="*80)
    print("REVIEWER'S FINAL FEEDBACK")
    print("="*80)
    if 'reviewer' in messages_by_source:
        print(messages_by_source['reviewer'])
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWorkflow interrupted by user.")
    except Exception as e:
        print(f"\nError during workflow: {str(e)}")
        import traceback
        traceback.print_exc() 