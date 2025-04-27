import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from src.dspy_graph_rag.logging_utils import setup_logger

logger = setup_logger('data_loader')

def load_sample_data(driver):
    """Loads sample data into Neo4j."""
    with driver.session() as session:
        # Clear existing data
        logger.info("Clearing existing Neo4j data")
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create sample nodes and relationships
        logger.info("Loading DSPy and RAG patterns data")
        cypher_query = """
        // Core DSPy Concepts
        CREATE (dspy:Concept {name: 'DSPy', text: 'A framework for programming with language models (LMs) that separates model prompting from execution, enabling systematic prompt development and optimization.'})
        CREATE (signature:Concept {name: 'DSPy Signature', text: 'A class that defines the expected inputs and outputs of a language model operation, making the interface explicit and type-safe.'})
        CREATE (module:Concept {name: 'DSPy Module', text: 'A composable unit in DSPy that encapsulates a specific LM operation, can be chained with other modules to create complex workflows.'})
        CREATE (teleprompter:Concept {name: 'Teleprompter', text: 'DSPy\\'s optimization system that automatically improves prompts based on training data and metric optimization.'})
        
        // DSPy RAG Components
        CREATE (dspyRetriever:Concept {name: 'DSPy Retriever', text: 'A DSPy module that handles document retrieval, can be customized with different backends like vector stores or knowledge graphs.'})
        CREATE (chainOfThought:Concept {name: 'ChainOfThought', text: 'A DSPy pattern that implements step-by-step reasoning, making the model\\'s thought process explicit and more reliable.'})
        CREATE (predictor:Concept {name: 'DSPy Predictor', text: 'Base class for modules that make predictions, can be extended for specific tasks like question answering or summarization.'})
        
        // Traditional RAG Concepts
        CREATE (tradRag:Concept {name: 'Traditional RAG', text: 'Classic Retrieval-Augmented Generation approach using direct prompting with retrieved context, typically implemented with string templates.'})
        CREATE (promptEng:Concept {name: 'Prompt Engineering', text: 'Manual process of crafting and refining prompts to improve LM performance, often requiring significant trial and error.'})
        CREATE (contextWindow:Concept {name: 'Context Window', text: 'The maximum amount of text that can be processed by an LM at once, affecting how much retrieved content can be included.'})
        
        // Comparison Points
        CREATE (modular:Concept {name: 'Modularity', text: 'DSPy\\'s approach of breaking down complex LM tasks into composable modules, versus traditional monolithic prompts.'})
        CREATE (optimization:Concept {name: 'Optimization Approach', text: 'DSPy uses systematic optimization with Teleprompter, while traditional RAG relies more on manual prompt tuning.'})
        CREATE (retrieval:Concept {name: 'Retrieval Strategy', text: 'DSPy allows for sophisticated retrieval patterns with custom retrievers, while traditional RAG often uses simpler vector similarity.'})
        CREATE (maintenance:Concept {name: 'Maintenance', text: 'DSPy\\'s modular approach makes systems easier to maintain and modify, compared to traditional RAG\\'s intertwined prompts and logic.'})
        CREATE (debugging:Concept {name: 'Debugging Capability', text: 'DSPy provides better debugging tools and transparency through its module system, making it easier to identify and fix issues.'})
        
        // Create relationships
        MERGE (dspy)-[:PROVIDES]->(signature)
        MERGE (dspy)-[:PROVIDES]->(module)
        MERGE (dspy)-[:INCLUDES]->(teleprompter)
        
        MERGE (module)-[:IMPLEMENTS]->(dspyRetriever)
        MERGE (module)-[:IMPLEMENTS]->(chainOfThought)
        MERGE (module)-[:EXTENDS]->(predictor)
        
        MERGE (dspyRetriever)-[:IMPROVES]->(retrieval)
        MERGE (chainOfThought)-[:ENHANCES]->(debugging)
        
        MERGE (tradRag)-[:USES]->(promptEng)
        MERGE (tradRag)-[:CONSTRAINED_BY]->(contextWindow)
        
        MERGE (dspy)-[:ENABLES]->(modular)
        MERGE (teleprompter)-[:ENABLES]->(optimization)
        
        MERGE (modular)-[:IMPROVES]->(maintenance)
        MERGE (modular)-[:FACILITATES]->(debugging)
        
        MERGE (promptEng)-[:AFFECTS]->(maintenance)
        MERGE (promptEng)-[:COMPLICATES]->(debugging)
        
        // Comparison edges
        MERGE (dspy)-[:DIFFERS_FROM]->(tradRag)
        MERGE (dspyRetriever)-[:DIFFERS_FROM]->(retrieval)
        MERGE (teleprompter)-[:IMPROVES_UPON]->(promptEng)
        """
        logger.debug(f"Executing data creation query:\n{cypher_query}")
        session.run(cypher_query)
        
        # Verify data was loaded
        count_query = "MATCH (n:Concept) RETURN count(n) as count"
        result = session.run(count_query).single()
        node_count = result["count"]
        logger.info(f"Successfully loaded {node_count} concept nodes")
        
        # Count relationships
        rel_query = "MATCH ()-[r]->() RETURN count(r) as count"
        result = session.run(rel_query).single()
        rel_count = result["count"]
        logger.info(f"Created {rel_count} relationships")
        
        # Test specific query about DSPy vs Traditional RAG
        test_query = """
        MATCH (c:Concept)
        WHERE toLower(c.name) CONTAINS 'dspy' 
           OR toLower(c.name) CONTAINS 'rag'
           OR toLower(c.text) CONTAINS 'dspy'
           OR toLower(c.text) CONTAINS 'rag'
        RETURN c.name, c.text
        """
        logger.debug("Testing retrieval for DSPy and RAG concepts:")
        results = list(session.run(test_query))
        for record in results:
            logger.debug(f"Found: {record['c.name']}")
            
        # Test the actual query that will be used
        default_query = "What are the key differences between DSPy RAG and traditional RAG approaches?"
        test_retrieval = """
        MATCH (c:Concept)
        WHERE toLower(c.name) CONTAINS toLower($query_text)
           OR toLower(c.text) CONTAINS toLower($query_text)
        RETURN c.name + ': ' + c.text AS result
        LIMIT 3
        """
        logger.debug(f"Testing default question: {default_query}")
        test_results = list(session.run(test_retrieval, {"query_text": default_query}))
        logger.debug(f"Found {len(test_results)} results for default query")
        for record in test_results:
            logger.debug(f"Result: {record['result']}")

def main():
    """Connects to Neo4j and loads data."""
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        logger.error("Neo4j credentials not found in .env file")
        return

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("Successfully connected to Neo4j")
        load_sample_data(driver)
        driver.close()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Failed to connect or load data: {e}")

if __name__ == "__main__":
    main() 