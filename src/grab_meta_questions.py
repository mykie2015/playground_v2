import os
import openai
from dotenv import load_dotenv
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o") # Default to gpt-4o if not set
INPUT_DIR = "docs/neo4j_graph"
OUTPUT_FILE = "doc/meta_questions.md"
# --- End Configuration ---

# Ensure output directory exists (though we created it earlier)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_meta_questions(client, file_content, filename):
    """
    Uses the OpenAI API to generate meta-questions for the given text content.
    """
    prompt = f"""
    Read the following document content from the file '{filename}'.
    Based *only* on the information present in this document, generate a concise list of 3-5 high-level questions that this document aims to answer or address.
    Phrase the questions clearly and focus on the main topics or themes discussed.
    Do not ask questions about information not present in the text.
    Format the output as a bulleted list.

    Document Content:
    ---
    {file_content[:8000]}
    ---

    Meta-Questions:
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant skilled at summarizing document content into high-level questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Lower temperature for more focused output
            max_tokens=150
        )
        questions = response.choices[0].message.content.strip()
        # Basic validation/cleanup
        if not questions.startswith(("*", "-")):
             # Try to add bullet points if missing, simple heuristic
             questions = "\n".join([f"- {q.strip()}" for q in questions.splitlines() if q.strip()])
             if not questions:
                 questions = "- No specific questions could be generated."

        return questions
    except openai.APIError as e:
        logging.error(f"OpenAI API error while processing {filename}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing {filename}: {e}")
    return "- Error generating questions for this document."


def main():
    """
    Main function to orchestrate the process.
    """
    if not API_KEY:
        logging.error("OPENAI_API_KEY not found in .env file.")
        return
    if not API_BASE:
        logging.warning("OPENAI_API_BASE not found in .env file. Using default OpenAI endpoint.")
        # If API_BASE is crucial and missing, you might want to exit instead:
        # logging.error("OPENAI_API_BASE not found in .env file.")
        # return
        client = openai.OpenAI(api_key=API_KEY)
    else:
        client = openai.OpenAI(api_key=API_KEY, base_url=API_BASE)


    # Check if input directory exists
    if not os.path.isdir(INPUT_DIR):
        logging.error(f"Input directory not found: {INPUT_DIR}")
        return

    # Find all markdown files
    md_files = glob.glob(os.path.join(INPUT_DIR, "*.md"))

    if not md_files:
        logging.warning(f"No markdown files found in {INPUT_DIR}")
        return

    logging.info(f"Found {len(md_files)} markdown files in {INPUT_DIR}.")

    # Clear the output file or create it
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write(f"# Meta-Questions from Documents in {INPUT_DIR}\n\n")

    total_files = len(md_files)
    processed_count = 0

    # Process each file
    for md_file_path in md_files:
        filename = os.path.basename(md_file_path)
        logging.info(f"Processing file: {filename} ({processed_count + 1}/{total_files})")
        try:
            with open(md_file_path, "r", encoding="utf-8") as infile:
                content = infile.read()

            if not content.strip():
                logging.warning(f"File {filename} is empty. Skipping.")
                questions = "- Document is empty."
            else:
                questions = get_meta_questions(client, content, filename)

            # Append results to the output file
            with open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:
                outfile.write(f"## {filename}\n\n")
                outfile.write(f"{questions}\n\n")
                outfile.write("---\n\n") # Add a separator

            processed_count += 1
            logging.info(f"Finished processing {filename}. Questions added to {OUTPUT_FILE}")

        except FileNotFoundError:
            logging.error(f"File not found during processing: {md_file_path}")
        except Exception as e:
            logging.error(f"Failed to process file {filename}: {e}")

    logging.info(f"Processing complete. Meta-questions saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
