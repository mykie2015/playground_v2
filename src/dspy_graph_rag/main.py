import dspy
import os
import argparse
from dotenv import load_dotenv

from src.dspy_graph_rag.rag_pipeline import GraphRAG, get_neo4j_driver
from src.dspy_graph_rag.data_loader import load_sample_data  # Optional: For loading data if needed
from src.dspy_graph_rag.logging_utils import setup_logger

logger = setup_logger('main')

def main(question, load_data):
    """Sets up DSPy, connects to Neo4j, runs the RAG pipeline, and prints the answer."""
    logger.info("Starting RAG pipeline application")
    
    # Load environment variables
    load_dotenv(override=True)  # Force override any existing env vars
    logger.debug("Environment variables loaded")
    
    # 1. Configure DSPy LM (using OpenAI)
    logger.info("Configuring DSPy language model")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_base = os.getenv("OPENAI_API_BASE")
    llm_model = os.environ.get("LLM_MODEL")  # Use os.environ instead of os.getenv
    
    # Debug log all relevant environment variables
    logger.debug("Environment variables loaded from .env:")
    logger.debug(f"OPENAI_API_BASE: {openai_api_base}")
    logger.debug(f"LLM_MODEL: {llm_model}")
    
    # Ensure LLM_MODEL is set, otherwise use default
    if not llm_model:
        llm_model = 'gpt-3.5-turbo'
        logger.warning(f"LLM_MODEL not found in environment, using default: {llm_model}")
    else:
        logger.info(f"Using configured model: {llm_model}")

    if not openai_api_key:
        logger.error("OpenAI API key not found in .env file")
        return

    try:
        # Pass api_base if it exists
        openai_kwargs = {"api_key": openai_api_key}
        if openai_api_base:
            openai_kwargs["api_base"] = openai_api_base
            logger.debug(f"Using OpenAI API Base: {openai_api_base}")

        logger.debug(f"Attempting to initialize LLM with model: {llm_model}")
        lm = dspy.LM("openai/" + llm_model, **openai_kwargs)
        dspy.configure(lm=lm)
        logger.info(f"DSPy successfully configured with OpenAI model: {llm_model}")
    except Exception as e:
        logger.error(f"Failed to configure DSPy LM: {e}")
        logger.debug(f"Failed configuration details - model: {llm_model}, api_base: {openai_api_base}")
        return

    # 2. Initialize Neo4j Driver
    logger.info("Initializing Neo4j connection")
    neo4j_driver = None
    try:
        neo4j_driver = get_neo4j_driver()
    except ValueError as e:
        logger.error(str(e))
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred connecting to Neo4j: {e}")
        return

    # 3. Load Sample Data (Optional)
    if load_data:
        logger.info("Loading sample data into Neo4j")
        try:
            load_sample_data(neo4j_driver)
            logger.info("Sample data loaded successfully")
            print("\nℹ️  Knowledge graph data loaded successfully. Ready to answer questions about DSPy and RAG approaches.")
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
    else:
        logger.info("Running without loading data (use --load-data flag to load/refresh knowledge graph data)")
        print("\n⚠️  Running without loading data. If you get no results, try running with --load-data flag.")

    # 4. Initialize and Run the RAG Pipeline
    logger.info("Initializing RAG pipeline")
    rag_pipeline = GraphRAG(neo4j_driver=neo4j_driver, k=3) # k=3 context nodes

    logger.info(f"Processing question: {question}")
    try:
        response = rag_pipeline(question)
        logger.info("Successfully generated response")
        logger.debug(f"Full response: {response}")
        print(f"\nQuestion: {question}")
        print(f"\nAnswer:\n{response.answer}")

    except Exception as e:
        logger.error(f"Error during RAG pipeline execution: {e}")
        logger.debug("Attempting to inspect LM history for debugging")
        try:
            lm.inspect_history(n=1)
        except Exception as inspect_e:
            logger.error(f"Could not inspect history: {inspect_e}")

    # 5. Close Neo4j connection
    if neo4j_driver:
        neo4j_driver.close()
        logger.info("Neo4j connection closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a DSPy Graph RAG pipeline with Neo4j.")
    parser.add_argument(
        "-q",
        "--question",
        type=str,
        default="What are the key differences between DSPy RAG and traditional RAG approaches?",
        help="The question to ask the RAG pipeline."
    )
    parser.add_argument(
        "--load-data",
        action="store_true",
        help="Clear existing Neo4j data and load sample data before running."
    )
    args = parser.parse_args()

    main(args.question, args.load_data) 