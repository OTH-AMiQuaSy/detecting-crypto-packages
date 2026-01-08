import os

# Constants
OLLAMA_HOST = 'https://replace-with-olama-host.de:11434/'
QUERY_TEMPLATE_PATH = "./query_templates"
CSV_BASE_PATH = "./csv"
LOGS_BASE_PATH = "./logs"
CSV_FILE = "{csv_base_path}/{os}_{llm_model}{timestamp_string}{template_alternative}.csv" # replaced during iteration
QUERY_TEMPLATE_FILE = "{query_template_path}/{os}_{llm_model}{template_alternative}.tpl" # replaced during iteration
ERROR_FILE_PATH = "{logs_base_path}/error-{os}_{llm_model}{timestamp_string}{template_alternative}.log" # replaced during iteration


# Load environment variables if they exist or use default values from above
OLLAMA_HOST = os.getenv('OLLAMA_HOST', OLLAMA_HOST)
QUERY_TEMPLATE_PATH = os.getenv('QUERY_TEMPLATE_PATH', QUERY_TEMPLATE_PATH)
CSV_BASE_PATH = os.getenv('CSV_BASE_PATH', CSV_BASE_PATH)
LOGS_BASE_PATH = os.getenv('LOGS_BASE_PATH', LOGS_BASE_PATH)
BASE_PACKAGE_LIST = os.getenv('BASE_PACKAGE_LIST', None)
CSV_FILE = os.getenv('CSV_FILE', CSV_FILE)
QUERY_TEMPLATE_FILE = os.getenv('QUERY_TEMPLATE_FILE', QUERY_TEMPLATE_FILE)
ERROR_FILE_PATH = os.getenv('ERROR_FILE_PATH', ERROR_FILE_PATH)