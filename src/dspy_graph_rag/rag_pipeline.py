import dspy
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from src.dspy_graph_rag.logging_utils import setup_logger

logger = setup_logger('rag_pipeline')

# --- Neo4j Retriever Module ---

class Neo4jRetriever(dspy.Retrieve):
    def __init__(self, neo4j_driver, k=3):
        logger.info(f"Initializing Neo4jRetriever with k={k}")
        self._neo4j_driver = neo4j_driver
        self._k = k
        super().__init__()

    def forward(self, query_or_queries, k=None):
        """Search Neo4j for relevant nodes based on the query."""
        logger.info(f"Starting retrieval for query: {query_or_queries}")
        k = k if k is not None else self._k
        queries = [
            query_or_queries
        ] if isinstance(query_or_queries, str) else query_or_queries
        logger.debug(f"Processing {len(queries)} queries with k={k}")

        results = []
        with self._neo4j_driver.session() as session:
            for idx, query in enumerate(queries, 1):
                # Clean the query - remove common question words and punctuation
                clean_query = query.lower().replace("what is", "").replace("what are", "").replace("how does", "").replace("?", "").strip()
                logger.debug(f"Processing query {idx}/{len(queries)}: {query}")
                logger.debug(f"Cleaned query: {clean_query}")
                
                # More sophisticated Cypher query with multiple matching strategies
                cypher_query = """
                MATCH (c:Concept)
                WHERE 
                    // Direct matches in name or text
                    toLower(c.name) CONTAINS toLower($query_text)
                    OR toLower(c.text) CONTAINS toLower($query_text)
                    // Matches with cleaned query
                    OR toLower(c.name) CONTAINS toLower($clean_query)
                    OR toLower(c.text) CONTAINS toLower($clean_query)
                    // Additional matches for specific keywords
                    OR (
                        toLower($query_text) CONTAINS 'dspy' AND 
                        (toLower(c.name) CONTAINS 'dspy' OR toLower(c.text) CONTAINS 'dspy')
                    )
                    OR (
                        toLower($query_text) CONTAINS 'rag' AND 
                        (toLower(c.name) CONTAINS 'rag' OR toLower(c.text) CONTAINS 'rag')
                    )
                WITH c, 
                    // Calculate relevance score based on matches
                    CASE 
                        WHEN toLower(c.name) CONTAINS toLower($query_text) THEN 3
                        WHEN toLower(c.text) CONTAINS toLower($query_text) THEN 2
                        WHEN toLower(c.name) CONTAINS toLower($clean_query) THEN 2
                        WHEN toLower(c.text) CONTAINS toLower($clean_query) THEN 1
                        ELSE 0
                    END as relevance
                // Optional: Also get connected nodes for more context
                OPTIONAL MATCH (c)-[r]-(related:Concept)
                WHERE type(r) IN ['DIFFERS_FROM', 'IMPROVES_UPON', 'PROVIDES', 'IMPLEMENTS']
                WITH c, relevance, collect(DISTINCT related.name) as related_concepts
                RETURN 
                    CASE
                        WHEN size(related_concepts) > 0
                        THEN c.name + ' (related: ' + substring(reduce(s = '', n IN related_concepts | s + ', ' + n), 2) + '): ' + c.text
                        ELSE c.name + ': ' + c.text
                    END as result,
                    relevance
                ORDER BY relevance DESC
                LIMIT $limit
                """
                params = {
                    "query_text": query,
                    "clean_query": clean_query,
                    "limit": k
                }
                
                # Log the full query and parameters
                logger.debug("Executing Cypher query:")
                logger.debug(f"Query:\n{cypher_query}")
                logger.debug(f"Parameters: {params}")
                
                try:
                    records = session.run(cypher_query, params)
                    # Create passages using text field instead of Passage class
                    query_results = [{"text": record["result"]} for record in records]
                    logger.debug(f"Found {len(query_results)} results for query: {query}")
                    if query_results:
                        logger.debug("Retrieved passages:")
                        for i, result in enumerate(query_results, 1):
                            logger.debug(f"  {i}. {result['text']}")
                    else:
                        logger.warning(f"No results found for query: {query}")
                        logger.debug("Trying fallback query for broader matches...")
                        # Fallback query to find any remotely related concepts
                        fallback_query = """
                        MATCH (c:Concept)
                        WHERE ANY(word IN split(toLower($clean_query), ' ')
                            WHERE toLower(c.name) CONTAINS word
                            OR toLower(c.text) CONTAINS word)
                        RETURN c.name + ': ' + c.text as result
                        LIMIT $limit
                        """
                        fallback_results = session.run(fallback_query, params)
                        query_results = [{"text": record["result"]} for record in fallback_results]
                        if query_results:
                            logger.debug(f"Found {len(query_results)} results with fallback query")
                            for i, result in enumerate(query_results, 1):
                                logger.debug(f"  {i}. {result['text']}")
                    results.extend(query_results)
                except Exception as e:
                    logger.error(f"Error executing Neo4j query: {e}")
                    raise

        logger.info(f"Retrieval complete. Total results: {len(results)}")
        return results

# --- DSPy Signature and Module ---

class GraphQA(dspy.Signature):
    """Answer questions based on retrieved context from a knowledge graph."""
    context = dspy.InputField(desc="List of passages containing relevant facts from the knowledge graph")
    question = dspy.InputField(desc="The question to answer")
    answer = dspy.OutputField(desc="Detailed, graph-informed response based on the provided context")

class GraphRAG(dspy.Module):
    def __init__(self, neo4j_driver, k=3):
        logger.info(f"Initializing GraphRAG with k={k}")
        super().__init__()
        self.retrieve = Neo4jRetriever(neo4j_driver=neo4j_driver, k=k)
        self.generate = dspy.ChainOfThought(GraphQA)
        logger.debug("GraphRAG initialization complete")

    def forward(self, question):
        logger.info(f"Processing question: {question}")
        
        # Retrieve relevant passages
        logger.debug("Starting context retrieval")
        context = self.retrieve(question)
        logger.debug(f"Retrieved {len(context)} passages for context")
        
        if not context:
            logger.warning("No context found in knowledge graph")
            return dspy.Prediction(
                context=[],
                question=question,
                answer="I apologize, but I couldn't find any relevant information in the knowledge graph to answer your question. "
                      "Please make sure the knowledge graph has been loaded with data (use --load-data flag) and try asking about DSPy, "
                      "traditional RAG approaches, or their comparisons."
            )
        
        # Generate answer
        logger.debug("Generating answer using ChainOfThought")
        try:
            prediction = self.generate(context=context, question=question)
            logger.info("Successfully generated answer")
            logger.debug(f"Generated answer: {prediction.answer}")
            return prediction
        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            raise

# --- Helper function to initialize Neo4j Driver ---

def get_neo4j_driver():
    """Initializes and returns the Neo4j driver."""
    logger.info("Initializing Neo4j driver")
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        logger.error("Neo4j credentials not found in .env file")
        raise ValueError("Neo4j credentials not found in .env file.")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("Successfully connected to Neo4j for RAG pipeline")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise 