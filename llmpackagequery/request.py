import sys
import csv
import logging

from time import time, sleep
from typing import List, Set

from openai import OpenAI
from writer import CSVResultsWriter
from ollama import Client as OllamaClient
from google import genai
from google.genai import errors

from gpt4all import GPT4All
from query import QueryStub, QueryHandlerCallable, TemplateBasedPromptGenerator, get_class

from mistralai import Mistral

log = logging.getLogger(__name__)

PACKAGE_LOG_ITERATIONS = 10

class RequestManger:
    _query_handler: QueryHandlerCallable
    _package_file_in: str
    _package_file_out: str
    _query_restriction: int

    RETRY_COUNT:int = 3

    def __init__(self,
                 query_handler: QueryHandlerCallable,
                 package_file_in: str,
                 package_file_out: str,
                 query_restriction: int = sys.maxsize,
                 log_iterations: int = PACKAGE_LOG_ITERATIONS) -> None:

        self._query_handler = query_handler
        self._package_file_in = package_file_in
        self._package_file_out = package_file_out
        self._query_restriction = query_restriction

        self.log_iterations = log_iterations

    def run(self):
        # Read the package list from the CSV file
        # query the GPT API using the package names
        # and write the results to the CSV file
        with open(self._package_file_in, mode='r') as file_read:
            with open(self._package_file_out, mode='w', newline='') as file_write:
                package_reader = csv.reader(file_read, delimiter=',', quotechar='"')
                next(package_reader) # Skip the header

                # get list to ensure the correct order of the attributes
                write_attributes: Set[str] = self._query_handler.response_parser.attributes_list

                with CSVResultsWriter(
                        file_dst=file_write,
                        package_header=write_attributes) as writer:
                    # start the timer
                    start_time = time()

                    # iterate over the packages
                    for idx, row in enumerate(package_reader):
                        request_start_time = time()

                        # execute query and write the results to the CSV file
                        results = self.do_request(package_name=row[0], # Package Name
                                            package_description=row[2], # Package Version
                                            package_tree=row[3], # Package Description
                                            query_handler=self._query_handler)
                        writer.write_results(results)

                        if self._query_restriction <= idx + 1:
                            log.info(f"Stopping the package request at index {idx}.")
                            self._log_progress(idx, start_time, request_start_time, force_log=True)
                            break

                        self._log_progress(idx, start_time, request_start_time)

    def _log_progress(self,
                      idx: int,
                      start_time: float,
                      request_start_time: float,
                      force_log: bool = False) -> None:
        # Log the progress
        if idx % self.log_iterations == 0 or force_log:
            time_current = time()
            log.info(f"{self.log_iterations} requests: {time_current - request_start_time:,.2f}; " \
                     f"overall: {time_current - start_time:,.2f}, Current index: {idx}")
            log.info("-"*30)

    def do_request(self, package_name: str,
               package_description: str,
               package_tree: str,
               query_handler: QueryHandlerCallable) -> str:

        # create question
        question = query_handler.generate_question_for_package(
            name=package_name,
            description=package_description,
            dependencies=package_tree)

        # ask the question
        attempt = 0
        response = None
        parsed_response = None
        while attempt < self.RETRY_COUNT:
            try:
                attempt += 1
                response = query_handler(question)
            except errors.ServerError as e:
                pause_time = 2 ** attempt
                log.warning(f"Server error on attempt {attempt} for package {package_name}: {e}")
                log.warning(f"Pausing for {pause_time} seconds before retrying...")
                sleep(pause_time)
                continue

            parsed_response = query_handler.parse_response(response, package_name)

            # if parser did not set an error, we are done
            if query_handler.response_parser.last_error is None:
                break

            log.warning(f"Parse attempt {attempt} failed for package {package_name} executing retry...")

        if parsed_response is None:
            log.error(f"Could not parse response for package {package_name}: {response}")
            # create empty response for package name and for remaining attributes
            parsed_response = query_handler.response_parser.get_empty_response(package_name)

        # parse the response and return
        return parsed_response

def execute(
        query_stub: str,
        llm_model: str,
        prompt_template_file: str,
        csv_file_out: str,
        attributes: List[str],
        base_package_list: str,
        api_key: str,
        host: str,
        query_restriction: int = sys.maxsize) -> None:

    # translate string to class for parser
    response_parser_class = get_class(llm_model+"ResponseParser")

    # set default parameters for the query handler
    query_handler_parameters = {
        "prompt_generator": TemplateBasedPromptGenerator(
            full_template_path=prompt_template_file),
        "response_parser": response_parser_class(attributes=attributes)
    }

    # set parameters for the respective query handler
    if query_stub == QueryStub.OLLAMA.value:
        # set ollama parameters
        query_handler_parameters["client"] = \
            OllamaClient(host=host)
        query_handler_parameters["model_name"] = llm_model
    elif query_stub == QueryStub.OPENAI.value:
        # pass api key and use default host
        query_handler_parameters["client"] = \
            OpenAI(api_key=api_key)
        query_handler_parameters["model_name"] = llm_model
    elif query_stub == QueryStub.GPT4ALL.value:
        # set gpt4all parameters
        query_handler_parameters["model"] = \
            GPT4All(f"{llm_model}.gguf", device="cuda")
    elif query_stub == QueryStub.GEMINI.value:
        # pass api key and use default host
        query_handler_parameters["client"] = \
            genai.Client(api_key=api_key)
        query_handler_parameters["model_name"] = llm_model
    elif query_stub == QueryStub.MISTRAL.value:
        # pass api key and use default host
        query_handler_parameters["client"] = \
            Mistral(api_key=api_key)
        query_handler_parameters["model_name"] = llm_model

    # get class which handles the query
    query_handler_class = get_class(query_stub+"QueryHandler")
    # instantiate the class with the given parameters
    query_handler: QueryHandlerCallable = \
        query_handler_class(**query_handler_parameters)

    log.info("Starting requests ...")
    request_manger = RequestManger(
        query_handler=query_handler,
        package_file_in=base_package_list,
        package_file_out=csv_file_out,
        query_restriction=query_restriction)

    request_manger.run()