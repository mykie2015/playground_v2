import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import inspect

# Create an OpenAI model client
client = OpenAIChatCompletionClient(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Create the writer agent
writer = AssistantAgent("writer", model_client=client, system_message="Draft a short paragraph about changing arm-lead to core-lead in tennis stroke.")

# Create two editor agents
editor1 = AssistantAgent("editor1", model_client=client, system_message="Edit the paragraph for grammar.")

editor2 = AssistantAgent("editor2", model_client=client, system_message="Edit the paragraph for style.")

# Create the final reviewer agent
final_reviewer = AssistantAgent(
    "final_reviewer",
    model_client=client,
    system_message="Consolidate the grammar and style edits into a final version.",
)

def visualize_digraph(builder, graph=None, output_path=None, custom_edges=None):
    """
    Visualize the GraphFlow from a DiGraphBuilder or DiGraph directly
    If dependencies aren't installed, falls back to ASCII visualization.
    
    Args:
        builder: DiGraphBuilder instance
        graph: Optional DiGraph instance (if already built)
        output_path: Optional path to save the image
        custom_edges: Optional list of explicitly defined edges to use for visualization
    """
    print("\n" + "="*80)
    print("GRAPHFLOW VISUALIZATION")
    print("="*80)
    
    try:
        # Extract agents and edges from the builder/graph
        agents = []
        edges = []
        
        # If custom edges were provided, use those first
        if custom_edges is not None:
            edges = custom_edges
        
        # If we have a graph, use it to extract structure
        elif graph is not None and hasattr(graph, 'nodes') and hasattr(graph, 'edges'):
            try:
                agents = list(graph.nodes)
                for from_node in graph.nodes:
                    for to_node in graph.edges.get(from_node, []):
                        condition = graph.edges[from_node].get(to_node, {}).get('condition')
                        edges.append({
                            "from_node": from_node,
                            "to_node": to_node,
                            "condition": condition
                        })
            except Exception as e:
                print(f"Error extracting from graph: {e}")
        
        # Otherwise, try to extract from the builder
        if not agents and hasattr(builder, 'get_participants'):
            try:
                agents = builder.get_participants()
            except Exception as e:
                print(f"Error getting participants: {e}")
                
        # Try getting edges from the builder's internal structure 
        if not edges:
            try:
                # Different methods to extract edges
                if hasattr(builder, '_edges') and builder._edges:
                    for edge in builder._edges:
                        edges.append({
                            "from_node": edge.from_node,
                            "to_node": edge.to_node,
                            "condition": edge.condition if hasattr(edge, 'condition') else None
                        })
                elif hasattr(builder, '_graph'):
                    for from_node, to_nodes in builder._graph.items():
                        for to_node in to_nodes:
                            edges.append({
                                "from_node": from_node,
                                "to_node": to_node,
                                "condition": None
                            })
            except Exception as e:
                print(f"Error extracting edges: {e}")
        
        # If we still don't have the structure, use the agents we created manually
        if not agents:
            try:
                # Look for any agent objects in the builder's attributes
                print("Attempting to extract agents from builder attributes...")
                for attr_name in dir(builder):
                    attr = getattr(builder, attr_name)
                    if hasattr(attr, 'name') and hasattr(attr, 'model_client'):
                        agents.append(attr)
                
                # Remove duplicates while preserving order
                seen = set()
                agents = [a for a in agents if not (a in seen or seen.add(a))]
                
                if not agents:
                    # Last resort - find all agent objects in the module's global scope
                    import sys
                    current_module = sys.modules[__name__]
                    for attr_name in dir(current_module):
                        attr = getattr(current_module, attr_name)
                        if hasattr(attr, 'name') and hasattr(attr, 'model_client'):
                            agents.append(attr)
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    agents = [a for a in agents if not (a in seen or seen.add(a))]
                
                print(f"Found {len(agents)} agents from environment")
            except Exception as e:
                print(f"Error finding agents: {e}")
            
        if not edges and agents:
            try:
                # Attempt to infer edges
                print("Attempting to infer workflow edges...")
                # Simple heuristic: assume agents form a sequence unless names indicate parallelism
                for i, agent in enumerate(agents):
                    # The last agent has no outgoing edges
                    if i == len(agents) - 1:
                        continue
                        
                    # If this is a "writer" or start agent, check if we should fan out
                    agent_name = agent.name.lower()
                    if (agent_name.startswith('writer') or 
                        'start' in agent_name or 
                        'initial' in agent_name):
                        # Look for editor or parallel agents to fan out to
                        parallel_agents = []
                        for j, potential_parallel in enumerate(agents):
                            if i == j:  # Skip self
                                continue
                                
                            p_name = potential_parallel.name.lower()
                            if ('edit' in p_name or 
                                'review' in p_name or 
                                'check' in p_name):
                                parallel_agents.append(potential_parallel)
                        
                        # If we found parallel agents, create edges to them
                        if len(parallel_agents) > 1:
                            for p_agent in parallel_agents:
                                edges.append({
                                    "from_node": agent,
                                    "to_node": p_agent,
                                    "condition": None
                                })
                        else:
                            # No parallel pattern detected, connect to next agent
                            edges.append({
                                "from_node": agent,
                                "to_node": agents[i+1],
                                "condition": None
                            })
                    else:
                        # If this is a middle agent, check if it should feed into a final agent
                        for j, potential_final in enumerate(agents):
                            if i >= j:  # Only look at agents that come after
                                continue
                                
                            p_name = potential_final.name.lower()
                            if ('final' in p_name or 
                                'consolidate' in p_name or 
                                'combine' in p_name):
                                edges.append({
                                    "from_node": agent,
                                    "to_node": potential_final,
                                    "condition": None
                                })
                                break
                        else:
                            # No final agent found, just connect to next
                            if i + 1 < len(agents):
                                edges.append({
                                    "from_node": agent,
                                    "to_node": agents[i+1],
                                    "condition": None
                                })
                
                # If we still don't have edges, create a simple chain
                if not edges and len(agents) > 1:
                    for i in range(len(agents) - 1):
                        edges.append({
                            "from_node": agents[i],
                            "to_node": agents[i+1],
                            "condition": None
                        })
                
                print(f"Inferred {len(edges)} edges in the workflow")
            except Exception as e:
                print(f"Error inferring edges: {e}")
        
        # If we still couldn't extract the structure, try scanning the builder object
        if not agents or not edges:
            # Introspect the builder to find agents and connections
            for attr_name in dir(builder):
                if attr_name.startswith('_'):
                    continue
                    
                attr = getattr(builder, attr_name)
                if callable(attr) and attr_name in ['get_participants', 'get_edges', 'get_nodes']:
                    try:
                        result = attr()
                        if not agents and attr_name == 'get_participants':
                            agents = result
                        elif not agents and attr_name == 'get_nodes':
                            agents = result
                        elif not edges and attr_name == 'get_edges':
                            edges = result
                    except Exception:
                        pass
        
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
            
            # Use hierarchical layout if available for better visualization of flow
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                # Fall back to spring layout
                pos = nx.spring_layout(G, seed=42)
            
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
            _print_ascii_graph_parallel(agents, edges)
            
        except Exception as e:
            # Fallback to ASCII visualization on any other error during matplotlib usage
            print(f"\nError during matplotlib visualization: {e}")
            print("\nFalling back to ASCII visualization:")
            _print_ascii_graph_parallel(agents, edges)
            
    except Exception as e:
        print(f"\nError during graph visualization: {e}")
        print("\nFalling back to basic ASCII visualization:")
        # Don't use hardcoded visualization - detect the structure from agents we have
        try:
            if not agents:
                # Try to find agents in the module scope
                import sys
                current_module = sys.modules[__name__]
                agents = []
                for attr_name in dir(current_module):
                    attr = getattr(current_module, attr_name)
                    if hasattr(attr, 'name') and hasattr(attr, 'model_client'):
                        agents.append(attr)
            
            if not edges:
                # Attempt to guess the structure based on available agents
                edges = []
                
                # Try to infer connections from agent names/roles
                for i, agent in enumerate(agents):
                    # If this isn't the last agent, connect to the next one as a basic fallback
                    if i < len(agents) - 1:
                        edges.append({
                            "from_node": agent,
                            "to_node": agents[i+1],
                            "condition": None
                        })
            
            _print_ascii_graph_parallel(agents, edges)
        except Exception as ex:
            print(f"  Error creating fallback visualization: {ex}")
            print("  [Agent Flow Visualization Failed]")
    
    print("\n" + "="*80 + "\n")

def _print_ascii_graph_parallel(agents, edges):
    """
    Helper function to print an ASCII representation of the graph.
    Attempts to create a more generalized ASCII visualization of the workflow.
    """
    try:
        # Create an adjacency list from edges
        adjacency = {}
        for edge in edges:
            from_node = edge["from_node"]
            to_node = edge["to_node"]
            
            if from_node not in adjacency:
                adjacency[from_node] = []
                
            adjacency[from_node].append(to_node)
        
        # Find nodes with no incoming edges (roots)
        incoming_nodes = set()
        for e in edges:
            incoming_nodes.add(e["to_node"])
            
        roots = [node for node in agents if node not in incoming_nodes]
        
        if not roots:
            print("  Could not identify root nodes. Using generic representation.")
            return _print_generic_ascii(agents)
            
        # For simplicity, we'll use the first root node
        if len(roots) > 1:
            print(f"  Multiple root nodes found. Using {roots[0].name} as primary.")
            
        root = roots[0]
        
        # Detect if this is a fan-out fan-in pattern (our parallel example)
        is_parallel = False
        if root in adjacency and len(adjacency[root]) > 1:
            # Check if children all point to the same node
            common_child = None
            for child in adjacency[root]:
                if child in adjacency:
                    for grandchild in adjacency[child]:
                        if common_child is None:
                            common_child = grandchild
                        elif common_child != grandchild:
                            common_child = None
                            break
            
            if common_child is not None:
                is_parallel = True
                parallel_children = adjacency[root]
                final_node = common_child
                
                # Draw parallel workflow
                print("  ┌" + "─" * (len(root.name) + 2) + "┐")
                print(f"  │ {root.name} │")
                print("  └" + "─" * (len(root.name) + 2) + "┘")
                print("       │")
                
                # Draw branches
                branch_line = "       ├"
                for i in range(len(parallel_children)-1):
                    branch_line += "─" * 9 + "┐"
                print(branch_line)
                
                branch_line = "       │"
                for i in range(len(parallel_children)-1):
                    branch_line += " " * 9 + "│"
                print(branch_line)
                
                branch_line = "       ▼"
                for i in range(len(parallel_children)-1):
                    branch_line += " " * 9 + "▼"
                print(branch_line)
                
                # Draw parallel nodes
                tops = []
                bottoms = []
                names = []
                
                for node in parallel_children:
                    name_len = len(node.name) + 2
                    tops.append("  ┌" + "─" * name_len + "┐")
                    names.append(f"  │ {node.name} │")
                    bottoms.append("  └" + "─" * name_len + "┘")
                    
                # Print tops of boxes
                print(" ".join(tops))
                # Print names
                print(" ".join(names))
                # Print bottoms
                print(" ".join(bottoms))
                
                # Connect back
                merge_lines = []
                for i in range(len(parallel_children)):
                    merge_lines.append("       │" + " " * (i*10))
                
                print(merge_lines[0])
                
                merge_line = "       └"
                for i in range(len(parallel_children)-1):
                    merge_line += "─" * 9 + "┘"
                print(merge_line)
                
                print("       │")
                print("       ▼")
                
                # Final node
                name_len = len(final_node.name) + 2
                print("  ┌" + "─" * name_len + "┐")
                print(f"  │ {final_node.name} │")
                print("  └" + "─" * name_len + "┘")
                
                return
        
        # Otherwise, print a simple sequential flow
        _print_sequential_ascii(root, adjacency)
        
    except Exception as e:
        print(f"  Error in ASCII visualization: {e}")
        _print_generic_ascii(agents)

def _print_sequential_ascii(root, adjacency):
    """Print a sequential workflow as ASCII art"""
    current = root
    visited = set()
    
    while current and current not in visited:
        visited.add(current)
        
        name_len = len(current.name) + 2
        print("  ┌" + "─" * name_len + "┐")
        print(f"  │ {current.name} │")
        print("  └" + "─" * name_len + "┘")
        
        # If there are next nodes, continue
        if current in adjacency and adjacency[current]:
            next_node = adjacency[current][0]
            print("       │")
            print("       ▼")
            current = next_node
        else:
            current = None

def _print_generic_ascii(agents):
    """Print a generic representation of the workflow"""
    print("  [Workflow with these agents:]")
    for agent in agents:
        print(f"  - {agent.name}")

# Build the workflow graph
builder = DiGraphBuilder()
builder.add_node(writer).add_node(editor1).add_node(editor2).add_node(final_reviewer)

# Fan-out from writer to editor1 and editor2
builder.add_edge(writer, editor1)
builder.add_edge(writer, editor2)

# Fan-in both editors into final reviewer
builder.add_edge(editor1, final_reviewer)
builder.add_edge(editor2, final_reviewer)

# Build and validate the graph
graph = builder.build()

# Create the flow
flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)

async def main():
    print("\n" + "="*80)
    print("STARTING PARALLEL GRAPHFLOW SEQUENCE")
    print("="*80 + "\n")
    
    print("Task: Write a short paragraph about changing arm-lead to core-lead in tennis stroke.\n")
    
    # Visualize the graph - directly from the builder and graph
    visualize_digraph(builder, graph, output_path="graphflow_parallel_visualization.png")
    
    # Create a dictionary to store messages by source
    messages_by_source = {}
    
    # Run the flow
    print("\nRunning the workflow...\n")
    stream = flow.run_stream(task="Write a short paragraph about changing arm-lead to core-lead in tennis stroke.")
    async for event in stream:
        # Store messages by their source
        if hasattr(event, 'source') and hasattr(event, 'content'):
            if event.source not in ['user', 'DiGraphStopAgent']:
                messages_by_source[event.source] = event.content
                # Show real-time progress
                print(f"--- Agent {event.source} has completed their task ---")
    
    # Display results in a readable format
    print("\n" + "="*80)
    print("WRITER'S DRAFT")
    print("="*80)
    if 'writer' in messages_by_source:
        print(messages_by_source['writer'])
    
    print("\n" + "="*80)
    print("GRAMMAR EDITOR'S REVISIONS")
    print("="*80)
    if 'editor1' in messages_by_source:
        print(messages_by_source['editor1'])
    
    print("\n" + "="*80)
    print("STYLE EDITOR'S REVISIONS")
    print("="*80)
    if 'editor2' in messages_by_source:
        print(messages_by_source['editor2'])
    
    print("\n" + "="*80)
    print("FINAL CONSOLIDATED VERSION")
    print("="*80)
    if 'final_reviewer' in messages_by_source:
        print(messages_by_source['final_reviewer'])
    
    print("\n" + "="*80)
    print("PARALLEL WORKFLOW COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 