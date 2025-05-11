import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import inspect

# Create an OpenAI model client
# client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

client = OpenAIChatCompletionClient(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
    )

# Create the writer agent
writer = AssistantAgent("writer", model_client=client, system_message="Draft a short paragraph on climate change.")

# Create the reviewer agent
reviewer = AssistantAgent("reviewer", model_client=client, system_message="Review the draft and suggest improvements.")

def visualize_graph(builder, output_path=None):
    """
    Visualize the GraphFlow using networkx and matplotlib.
    If dependencies aren't installed, falls back to ASCII visualization.
    
    Args:
        builder: DiGraphBuilder instance
        output_path: Optional path to save the image
    """
    print("\n" + "="*80)
    print("GRAPHFLOW VISUALIZATION")
    print("="*80)
    
    try:
        # Get all nodes and edges with direct access to the agents
        # The nodes in DiGraphBuilder are the actual agent objects themselves
        agents = [writer, reviewer]
        node_names = [agent.name for agent in agents]
        
        # Get edge information - in our case, just a simple writer -> reviewer flow
        edges = [{"from_node": agents[0], "to_node": agents[1], "condition": None}]
        
        # Print agents
        print("\nAgents:")
        for i, agent in enumerate(agents):
            system_message = getattr(agent, 'system_message', 'No system message')
            print(f"  [{i+1}] {agent.name}: {system_message}")
        
        # Print edges (connections between agents)
        print("\nEdges (Workflow):")
        for edge in edges:
            try:
                from_name = edge["from_node"].name
                to_name = edge["to_node"].name
                condition = f" (condition: {edge['condition']})" if edge.get('condition') else ""
                print(f"  {from_name} ----→ {to_name}{condition}")
            except (AttributeError, KeyError, TypeError) as e:
                print(f"  Warning: Could not format edge: {e}")
        
        # Try to use networkx and matplotlib for visualization if available
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes with labels
            for agent in agents:
                G.add_node(agent.name)
            
            # Add edges
            for edge in edges:
                try:
                    from_name = edge["from_node"].name
                    to_name = edge["to_node"].name
                    condition = edge.get('condition', '')
                    
                    if condition:
                        G.add_edge(from_name, to_name, label=str(condition))
                    else:
                        G.add_edge(from_name, to_name)
                except (AttributeError, KeyError, TypeError) as e:
                    print(f"Warning: Could not add edge to graph: {e}")
                    continue
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(G, seed=42)  # positions for all nodes
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=2, arrowsize=20)
            
            # Draw edge labels (conditions)
            edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if 'label' in d}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
            
            # Draw node labels (agent names)
            nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
            
            plt.title("GraphFlow Visualization")
            plt.axis("off")
            
            # Save or display
            if output_path:
                plt.savefig(output_path, bbox_inches="tight")
                print(f"\nGraph visualization saved to: {output_path}")
            else:
                plt.tight_layout()
                plt.show()
                
        except ImportError:
            # Fallback to ASCII visualization - dependencies not installed
            print("\nASCII Visualization (install networkx and matplotlib for better visualization):")
            _print_ascii_graph(agents)
            
        except Exception as e:
            # Fallback to ASCII visualization on any other error during matplotlib usage
            print(f"\nError during matplotlib visualization: {e}")
            print("\nFalling back to ASCII visualization:")
            _print_ascii_graph(agents)
            
    except Exception as e:
        print(f"\nError during graph visualization: {e}")
        print("\nFalling back to basic ASCII visualization:")
        _print_ascii_graph([writer, reviewer])
    
    print("\n" + "="*80 + "\n")

def _print_ascii_graph(agents):
    """Helper function to print a simple ASCII representation of the graph."""
    if not agents:
        print("  (No agents found)")
        return
        
    try:
        # Simple sequential display for now
        for i, agent in enumerate(agents):
            if i > 0:
                print("       │")
                print("       ▼")
            
            name = agent.name
            padding = max(0, 9 - len(name))
            left_pad = padding // 2
            right_pad = padding - left_pad
            
            print(f"  ┌─{'─' * len(name)}{'─' * padding}┐")
            print(f"  │ {' ' * left_pad}{name}{' ' * right_pad}│")
            print(f"  └─{'─' * len(name)}{'─' * padding}┘")
    except Exception as e:
        print(f"  Error in ASCII visualization: {e}")
        print("  [Agent 1] → [Agent 2]")

# Build the graph
builder = DiGraphBuilder()
builder.add_node(writer).add_node(reviewer)
builder.add_edge(writer, reviewer)

# Build and validate the graph
graph = builder.build()

# Create the flow
flow = GraphFlow([writer, reviewer], graph=graph)

async def main():
    print("\n" + "="*80)
    print("STARTING GRAPHFLOW SEQUENCE")
    print("="*80 + "\n")
    
    print("Task: Write a short paragraph about changing arm-lead to core-lead in tennis stroke.\n")
    
    # Visualize the graph
    visualize_graph(builder, output_path="graphflow_visualization.png")
    
    # Create a dictionary to store messages by source
    messages_by_source = {}
    
    # Run the flow
    stream = flow.run_stream(task="Write a short paragraph about changing arm-lead to core-lead in tennis stroke.")
    async for event in stream:
        # Store messages by their source
        if hasattr(event, 'source') and hasattr(event, 'content'):
            if event.source not in ['user', 'DiGraphStopAgent']:
                messages_by_source[event.source] = event.content
    
    # Display results in a readable format
    print("\n" + "="*80)
    print("WRITER'S DRAFT")
    print("="*80)
    if 'writer' in messages_by_source:
        print(messages_by_source['writer'])
    
    print("\n" + "="*80)
    print("REVIEWER'S IMPROVED VERSION")
    print("="*80)
    if 'reviewer' in messages_by_source:
        print(messages_by_source['reviewer'])
    
    print("\n" + "="*80)
    print("SEQUENCE COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
