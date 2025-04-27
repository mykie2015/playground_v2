from flask import Flask, render_template, jsonify, send_from_directory
from neo4j_graph_viz import Neo4jGraphVisualizer
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with explicit template and static folders
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
app.config['JSON_SORT_KEYS'] = False

# Initialize the visualizer
visualizer = None

def init_visualizer():
    global visualizer
    if visualizer is None:
        try:
            visualizer = Neo4jGraphVisualizer()
            logger.info("Neo4j visualizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j visualizer: {str(e)}")
            raise

@app.route('/')
def index():
    try:
        # Initialize visualizer before rendering template
        init_visualizer()
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/graph')
def get_graph_data():
    try:
        init_visualizer()
        # Fetch and process graph data
        records = visualizer.fetch_graph_data()
        node_labels = visualizer.build_network_graph(records)
        fig = visualizer.create_visualization(node_labels)
        
        # Convert the figure to JSON for the frontend
        graph_json = json.loads(fig.to_json())
        return jsonify(graph_json)
    except Exception as e:
        logger.error(f"Error getting graph data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Initialize on startup
        init_visualizer()
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise 