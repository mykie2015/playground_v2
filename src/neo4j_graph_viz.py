import plotly.graph_objects as go
import networkx as nx
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jGraphVisualizer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Neo4j connection settings
        self.uri = os.getenv('NEO4J_URI')
        self.username = os.getenv('NEO4J_USERNAME')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        
        if not all([self.uri, self.username, self.password]):
            raise ValueError("Missing required Neo4j credentials in .env file")
        
        self.driver = None
        self.G = nx.DiGraph()
        
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
            
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
            
    def fetch_graph_data(self, query: str = "MATCH (n)-[r]->(m) RETURN n, r, m"):
        """Fetch graph data from Neo4j"""
        if not self.driver:
            self.connect()
            
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query)
                return list(result)
        except Exception as e:
            logger.error(f"Failed to fetch graph data: {str(e)}")
            raise
            
    def build_network_graph(self, records: List) -> Dict:
        """Build NetworkX graph from Neo4j records"""
        node_labels = {}
        
        for record in records:
            source = record["n"]
            target = record["m"]
            relationship = record["r"]
            
            source_id = source.element_id
            target_id = target.element_id
            
            # Add nodes and edge
            self.G.add_node(source_id)
            self.G.add_node(target_id)
            self.G.add_edge(source_id, target_id, type=relationship.type)
            
            # Store node labels with properties
            source_props = dict(source.items())
            target_props = dict(target.items())
            
            node_labels[source_id] = source_props.get('name', f"Node {source_id}")
            node_labels[target_id] = target_props.get('name', f"Node {target_id}")
            
        return node_labels
            
    def create_visualization(self, node_labels: Dict) -> go.Figure:
        """Create Plotly visualization"""
        # Generate positions using force-directed layout
        pos = nx.spring_layout(self.G, k=1, iterations=50)
        
        # Create edge traces
        edge_traces = []
        for edge in self.G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_type = edge[2].get('type', '')
            
            trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=1, color='#888'),
                hoverinfo='text',
                text=edge_type,
                mode='lines',
                showlegend=False
            )
            edge_traces.append(trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node_labels[node])
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                size=15,
                colorbar=dict(
                    thickness=15,
                    title=dict(
                        text='Node Connections',
                        side='right'
                    ),
                    xanchor='left'
                )
            )
        )
        
        # Color nodes by number of connections
        node_adjacencies = []
        for node in self.G.nodes():
            adjacencies = list(self.G.neighbors(node))
            node_adjacencies.append(len(adjacencies))
            
        node_trace.marker.color = node_adjacencies
        
        # Create figure
        fig = go.Figure(
            data=[*edge_traces, node_trace],
            layout=go.Layout(
                title={
                    'text': 'Neo4j Graph Visualization',
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=24)
                },
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                template='plotly_white',
                height=800,
                width=1000
            )
        )
        
        return fig

def main():
    try:
        # Initialize visualizer
        visualizer = Neo4jGraphVisualizer()
        
        # Fetch data and create visualization
        records = visualizer.fetch_graph_data()
        node_labels = visualizer.build_network_graph(records)
        fig = visualizer.create_visualization(node_labels)
        
        # Show the plot
        fig.show()
        
    except Exception as e:
        logger.error(f"Error in visualization process: {str(e)}")
        raise
    finally:
        # Ensure connection is closed
        if visualizer:
            visualizer.close()

if __name__ == "__main__":
    main() 