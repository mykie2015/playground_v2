#!/usr/bin/env python3

import yaml
import logging
import requests
import os
from pathlib import Path
import time
import argparse # Added for command-line arguments
import re # Added for filename sanitization
from bs4 import BeautifulSoup # Added for HTML parsing
from trafilatura import extract as trafilatura_extract # Import specific function

# --- Constants ---
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
DEFAULT_TIMEOUT = 20 # Default request timeout in seconds
DEFAULT_LOG_LEVEL = logging.INFO

# Determine script and repo paths relative to the script location
SCRIPT_DIR = Path(__file__).parent.resolve() # Use resolve() for absolute path
REPO_ROOT = SCRIPT_DIR.parent.parent # Assumes script is in src/fetch_webpage

# Define paths using REPO_ROOT *after* it's defined
DEFAULT_CONFIG_PATH = SCRIPT_DIR / 'weblinks.yml'
DEFAULT_LOG_DIR = REPO_ROOT / 'logs'
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / 'fetch_webpage.log'
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'output' / 'fetched_pages' # Added default output dir

# Global logger instance (configured in setup_logging)
logger = logging.getLogger(__name__)


# --- Logging Setup ---

def setup_logging(log_file_path: Path, log_level: int):
    """Configures the global logger instance."""
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplication if called multiple times
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Ensure log directory exists
    try:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Warning: Could not create log directory {log_file_path.parent}: {e}. File logging might fail.")

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except IOError as e:
        print(f"Error setting up file logger at {log_file_path}: {e}. Logging to console only.")

    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    logger.info(f"Logging initialized. Level: {logging.getLevelName(log_level)}, File: {log_file_path}")


# --- Configuration Management ---

def load_config(config_path: Path) -> dict:
    """Loads the YAML configuration file. Creates a default if not found."""
    default_config_content = {'to_be_fetched': [], 'fetched': []} # Simplified default

    if not config_path.exists():
        logger.info(f"Config file not found at {config_path}. Creating default with empty lists.")
        save_config(default_config_content, config_path) # Save the default structure
        return default_config_content

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if config is None:
                logger.warning(f"Config file {config_path} is empty. Using default empty lists.")
                # Overwrite empty file with default structure
                save_config(default_config_content, config_path)
                return default_config_content.copy() # Return a copy

            # Ensure required keys exist and are lists
            if not isinstance(config.get('to_be_fetched'), list):
                logger.warning("Config missing 'to_be_fetched' list or is not a list. Initializing as empty.")
                config['to_be_fetched'] = []
            if not isinstance(config.get('fetched'), list):
                logger.warning("Config missing 'fetched' list or is not a list. Initializing as empty.")
                config['fetched'] = []

            logger.info(f"Config loaded successfully from {config_path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file {config_path}: {e}. Returning empty config.", exc_info=True)
        return {'to_be_fetched': [], 'fetched': []} # Safe default on error
    except Exception as e:
        logger.error(f"An unexpected error occurred loading config {config_path}: {e}. Returning empty config.", exc_info=True)
        return {'to_be_fetched': [], 'fetched': []} # Safe default on error


def save_config(config: dict, config_path: Path):
    """Saves the configuration to the specified YAML file."""
    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        logger.debug(f"Config saved successfully to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config file {config_path}: {e}", exc_info=True)


# --- Fetching Logic ---

def fetch_url(url: str, timeout: int, user_agent: str) -> tuple[bool, str | None]:
    """Fetches a given URL. Returns (success_status, content_string_or_None)."""
    logger.debug(f"Attempting to fetch: {url}")
    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        # Attempt to decode content, fall back if needed
        try:
            content = response.content.decode(response.encoding or 'utf-8', errors='replace')
        except (LookupError, TypeError):
             # Fallback if encoding is invalid or not found
             content = response.text # requests tries its best

        logger.info(f"Successfully fetched {url} (Status: {response.status_code}, Size: {len(response.content)} bytes)")
        return True, content
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout error fetching {url} after {timeout} seconds")
        return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {url}: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
        return False, None

# --- Content Saving ---

def sanitize_filename(url: str) -> str:
    """Creates a safe filename from a URL."""
    # Remove scheme (http, https)
    if url.startswith('https://'):
        name = url[len('https://'):]
    elif url.startswith('http://'):
        name = url[len('http://'):]
    else:
        name = url

    # Replace common invalid characters
    name = name.replace('/', '_').replace(':', '-').replace('?', '').replace('=', '').replace('&', '')
    # Remove potentially problematic trailing characters
    name = name.strip('._- ')
    # Limit length
    name = name[:100] # Limit filename length
    # Final basic sanitization (allow alphanumeric, underscore, hyphen)
    name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)
    if not name:
        name = "default_page"
    return name + ".md" # Keep .md extension

def extract_main_content(html_content: str) -> str:
    """Extracts the main textual content from HTML using Trafilatura."""
    # Use trafilatura to extract the main content
    # include_comments=False, include_tables=True are options if needed
    extracted_text = trafilatura_extract(html_content)

    if not extracted_text:
        logger.warning("Trafilatura could not extract main content. Returning empty string.")
        return ""

    logger.debug(f"Successfully extracted content using Trafilatura (length: {len(extracted_text)})")
    return extracted_text # Trafilatura returns plain text

def save_content_as_markdown(html_content: str, url: str, base_output_dir: Path):
    """Extracts text using Trafilatura and saves it into a date-organized Markdown file."""
    try:
        today_str = time.strftime("%Y-%m-%d")
        output_path_dated = base_output_dir / today_str
        output_path_dated.mkdir(parents=True, exist_ok=True)

        filename = sanitize_filename(url) # Generates .md
        file_path = output_path_dated / filename

        # Extract main text content using the updated function
        extracted_text = extract_main_content(html_content)

        if not extracted_text:
             logger.warning(f"Extracted text was empty for {url}. Saving minimal info.")
             extracted_text = "[Could not extract main content using Trafilatura]"

        # Simple Markdown structure with extracted text
        # Keep minimal headers for context
        markdown_content = f"# Content from: {url}\n\nSource URL: `{url}`\nFetched on: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n---\n\n{extracted_text}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Saved extracted text (via Trafilatura) for {url} to {file_path}")
    except OSError as e:
        logger.error(f"Error creating directory or writing file for {url} at {file_path}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error saving content for {url}: {e}", exc_info=True)


# --- Argument Parsing ---

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch webpages listed in a YAML configuration file.")

    parser.add_argument(
        '-c', '--config',
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to the YAML configuration file (default: {DEFAULT_CONFIG_PATH})"
    )
    parser.add_argument(
        '-l', '--log-file',
        type=Path,
        default=DEFAULT_LOG_FILE,
        help=f"Path to the log file (default: {DEFAULT_LOG_FILE})"
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default=logging.getLevelName(DEFAULT_LOG_LEVEL),
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=f"Set the logging level (default: {logging.getLevelName(DEFAULT_LOG_LEVEL)})"
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        '-ua', '--user-agent',
        type=str,
        default=DEFAULT_USER_AGENT,
        help="User-Agent string for requests"
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Base directory to save fetched content (default: {DEFAULT_OUTPUT_DIR})"
    )
    # Example for future extension: adding retries
    # parser.add_argument('--retries', type=int, default=0, help="Number of retries on failure (default: 0)")

    args = parser.parse_args()

    # Convert log level string to logging constant
    args.log_level = getattr(logging, args.log_level.upper(), DEFAULT_LOG_LEVEL)

    return args


# --- Main Execution ---

def main():
    """Main execution logic."""
    args = parse_arguments()

    # Setup logging based on arguments *before* any logging calls
    setup_logging(args.log_file, args.log_level)

    logger.info("--- Starting webpage fetch process ---")
    logger.info(f"Using configuration file: {args.config}")
    logger.info(f"Using log file: {args.log_file}")
    logger.info(f"Request timeout: {args.timeout}s")
    logger.info(f"User-Agent: {args.user_agent}")
    logger.info(f"Output directory for fetched content: {args.output_dir}")

    start_time = time.time()
    config = load_config(args.config)

    if not config or 'to_be_fetched' not in config or 'fetched' not in config:
        logger.error("Exiting: Failed to load or initialize a valid configuration.")
        return

    # Get references to the lists within the loaded config dict
    to_be_fetched_list = config['to_be_fetched']
    fetched_list = config['fetched']
    initial_count = len(to_be_fetched_list)

    if not to_be_fetched_list:
        logger.info("No URLs found in 'to_be_fetched' list. Nothing to do.")
    else:
        logger.info(f"Found {initial_count} URLs in 'to_be_fetched' list.")

    config_updated = False
    success_count = 0
    fail_count = 0
    newly_fetched = [] # URLs successfully fetched in this run

    # Iterate using index for safe removal from the list being processed
    i = 0
    while i < len(to_be_fetched_list):
        url = to_be_fetched_list[i]

        # Basic URL validation
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            logger.warning(f"Skipping invalid or non-HTTP(S) URL in 'to_be_fetched': {url}")
            to_be_fetched_list.pop(i) # Remove invalid entry
            config_updated = True
            # Do not increment i, as list size decreased
            continue

        # Check if already fetched (e.g., from a previous run or duplicate entry)
        if url in fetched_list:
            logger.info(f"Skipping URL already present in 'fetched' list: {url}")
            # Ensure consistency: Remove from 'to_be_fetched' if it's there
            to_be_fetched_list.pop(i)
            logger.debug(f"Removed duplicate {url} from 'to_be_fetched' list.")
            config_updated = True
            # Do not increment i
            continue

        logger.info(f"Processing URL: {url}")
        fetch_successful, content = fetch_url(url, args.timeout, args.user_agent)

        if fetch_successful and content is not None:
            # Save extracted markdown content on success
            save_content_as_markdown(content, url, args.output_dir) # Changed back function call

            # Mark for moving to fetched list
            newly_fetched.append(url)
            success_count += 1
            to_be_fetched_list.pop(i) # Remove from to_be_fetched
            config_updated = True
            # Do not increment i (list size changed)
        else:
            # Fetch failed, keep in to_be_fetched
            fail_count += 1
            i += 1 # Increment i only on failure

        # Optional delay
        # time.sleep(0.5)

    # Add all newly fetched URLs to the 'fetched' list (avoiding duplicates)
    if newly_fetched:
        added_count = 0
        for url in newly_fetched:
            if url not in fetched_list:
                fetched_list.append(url)
                added_count +=1
        if added_count > 0:
             logger.info(f"Added {added_count} newly fetched URLs to the 'fetched' list.")
             config_updated = True # Ensure config is saved if fetched list was modified

    # Save config only if changes were made during the run
    if config_updated:
        logger.info("Saving updated configuration file.")
        save_config(config, args.config)
    else:
        logger.info("No changes made to the configuration file this run.")

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"--- Webpage fetch process finished ---")
    logger.info(f"Attempted to process {initial_count} URLs from the initial list in {duration:.2f} seconds.")
    logger.info(f"Successfully fetched: {success_count}, Failed: {fail_count}")
    # Reload config to get the absolute latest state for final reporting
    final_config = load_config(args.config)
    remaining_count = len(final_config.get('to_be_fetched', []))
    total_fetched_count = len(final_config.get('fetched', []))
    logger.info(f"URLs currently in 'to_be_fetched': {remaining_count}")
    logger.info(f"Total URLs in 'fetched': {total_fetched_count}")


if __name__ == "__main__":
    # Dependency check updated
    try:
        import yaml
        import requests
        import trafilatura # Check if trafilatura is available
    except ImportError as e:
        print(f"Error: Missing required package(s) ({e.name}). Please install them.")
        print("You can typically install them using: pip install -r requirements.txt")
        exit(1)

    main()
