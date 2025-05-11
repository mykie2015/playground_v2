import os
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import ConditionalGraphManager
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio

# Create an OpenAI model client
client = OpenAIChatCompletionClient(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Create a classifier agent that determines the task type
classifier = AssistantAgent(
    "classifier",
    model_client=client,
    system_message="You are a task classifier. Determine if the task is about 'writing', 'math', or 'research'. Topics like tennis or sports techniques are 'writing' tasks. Respond with ONLY one word: 'writing', 'math', or 'research'."
)

# Create specialized agents for different task types
writer = AssistantAgent(
    "writer",
    model_client=client,
    system_message="You are an expert writer. Create high-quality content on the given topic."
)

mathematician = AssistantAgent(
    "mathematician",
    model_client=client,
    system_message="You are a math expert. Solve mathematical problems clearly showing your work."
)

researcher = AssistantAgent(
    "researcher",
    model_client=client,
    system_message="You are a thorough researcher. Provide detailed, factual information on the given topic."
)

# A general reviewer that checks all types of work
reviewer = AssistantAgent(
    "reviewer",
    model_client=client,
    system_message="Review the previous work critically and suggest specific improvements."
)

# Define routing logic with condition functions
def is_writing_task(message):
    """Check if the task is about writing."""
    if isinstance(message, str):
        content = message.lower()
    else:
        content = getattr(message, 'content', '').lower()
    
    return "writing" in content or "tennis" in content or "paragraph" in content

def is_math_task(message):
    """Check if the task is about math."""
    if isinstance(message, str):
        content = message.lower()
    else:
        content = getattr(message, 'content', '').lower()
    
    return "math" in content or "equation" in content

def is_research_task(message):
    """Check if the task is about research."""
    if isinstance(message, str):
        content = message.lower()
    else:
        content = getattr(message, 'content', '').lower()
    
    return "research" in content or "history" in content or "impact" in content

# Import our visualization function
from graphflow_parallel import visualize_digraph

# Build the workflow using a conditional graph manager
graph_manager = ConditionalGraphManager(
    agents=[classifier, writer, mathematician, researcher, reviewer],
    default_start_agent=classifier,
    routing_rules=[
        # Routing from classifier based on classification result
        (classifier, writer, is_writing_task),
        (classifier, mathematician, is_math_task),
        (classifier, researcher, is_research_task),
        
        # All specialists output routes to reviewer
        (writer, reviewer, lambda _: True),
        (mathematician, reviewer, lambda _: True),
        (researcher, reviewer, lambda _: True),
    ]
)

async def main():
    print("\n" + "="*80)
    print("STARTING CONDITIONAL GRAPHFLOW SEQUENCE")
    print("="*80 + "\n")
    
    # Get user input for the task
    tasks = [
        "Write a short paragraph about changing arm-lead to core-lead in tennis stroke.",
        "Solve the quadratic equation: 2x^2 + 5x - 3 = 0",
        "Research the history and impact of the Internet."
    ]
    
    print("Choose a task:")
    for i, task in enumerate(tasks):
        print(f"[{i+1}] {task}")
    
    try:
        choice = int(input("\nEnter your choice (1-3): "))
        if choice < 1 or choice > 3:
            print("Invalid choice. Using default task 1.")
            choice = 1
    except (ValueError, TypeError):
        print("Invalid input. Using default task 1.")
        choice = 1
    
    task = tasks[choice-1]
    print(f"\nSelected task: {task}\n")
    
    # Create a dictionary to store messages by source
    messages_by_source = {}
    
    # Run the flow
    print("\nRunning the workflow...\n")
    messages = await graph_manager.run(
        user_input=task,
        sender=UserProxyAgent(name="user"),
    )
    
    # Extract results from messages
    for msg in messages:
        if hasattr(msg, 'sender') and hasattr(msg, 'content'):
            if msg.sender.name not in ['user']:
                messages_by_source[msg.sender.name] = msg.content
                print(f"--- Agent {msg.sender.name} has completed their task ---")
    
    # Display results in a readable format
    print("\n" + "="*80)
    print("CLASSIFICATION")
    print("="*80)
    if 'classifier' in messages_by_source:
        print(messages_by_source['classifier'])
    
    # Determine task type from classifier response
    task_type = 'unknown'
    if 'classifier' in messages_by_source:
        content = messages_by_source['classifier'].lower()
        if 'writing' in content:
            task_type = 'writing'
        elif 'math' in content:
            task_type = 'math'
        elif 'research' in content:
            task_type = 'research'
    
    print("\n" + "="*80)
    if task_type == 'writing':
        print("WRITER'S CONTENT")
        if 'writer' in messages_by_source:
            print(messages_by_source['writer'])
    elif task_type == 'math':
        print("MATHEMATICIAN'S SOLUTION")
        if 'mathematician' in messages_by_source:
            print(messages_by_source['mathematician'])
    elif task_type == 'research':
        print("RESEARCHER'S FINDINGS")
        if 'researcher' in messages_by_source:
            print(messages_by_source['researcher'])
    print("="*80)
    
    print("\n" + "="*80)
    print("REVIEWER'S ASSESSMENT")
    print("="*80)
    if 'reviewer' in messages_by_source:
        print(messages_by_source['reviewer'])
    
    print("\n" + "="*80)
    print("CONDITIONAL WORKFLOW COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 