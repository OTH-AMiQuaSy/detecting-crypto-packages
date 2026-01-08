import re
import logging
import ast # instead of json
from mistralai import Mistral

from typing import Dict, List, Protocol, Set, Type
from wsgiref import types
from openai import OpenAI
from ollama import Client as OllamaClient
from gpt4all import GPT4All
from enum import Enum

from google import genai
from google.genai import types

################### Constants ###################
NON_ALNUM = re.compile(r'[^0-9a-zA-Z]+')
# match one json object in curly braces
JSON_OBJECT_ONLY = re.compile(r'\{[^}]*\}', re.DOTALL)
# match one json object in markdown code block
JSON_INLINE_MARKDOWN = re.compile(r"```json((.*?\n)*)```", re.MULTILINE)

class QueryStub (Enum):
    """Enum for query stubs."""
    OLLAMA = "ollama"
    GPT4ALL = "gpt4all"
    OPENAI = "openai"
    GEMINI = "gemini"
    MISTRAL = "mistral"

################### Globals ###################
log = logging.getLogger(__name__)
class_registry: Dict[str, Type] = {}

#### Global function for class registering ####
def normalize(s: str) -> str:
    """Lower-case, turn every non-alnum run into '_', and strip extras."""
    return NON_ALNUM.sub('_', s).strip('_').upper()

def register(cls: Type) -> Type:
    """Decorator: puts class in the registry under its normalized name."""
    class_registry[normalize(cls.__name__)] = cls
    return cls

def get_class(raw: str) -> Type | None:
    """Get a class from the registry by its normalized name."""
    return class_registry.get(normalize(raw))

################### Classes ###################
class ResponseParser:
    attributes: Set[str]
    attributes_list: List[str]
    last_error: str | None = None
    ALIASES: Dict[str, str] = {
        "cryptography_relevance": "cryptographic_relevance",
        "explanation": "justification"
    }

    def __init__(self, attributes: List[str] = None) -> None:
        self.attributes_list = attributes
        self.attributes = set(attributes)

    def get_empty_response(self, package_name: str) -> str:
        attributes_count = len(self.attributes_list)-1
        return f'{package_name}' + ','*attributes_count

    def __call__(self, response: str, package_name: str) -> str:
        ...

    def __try_parse_bool_str(self, value):
        if isinstance(value, bool):
            return str(value)
        value_str = str(value).strip().lower()
        if value_str in ('true', '1', 'yes', 'y', 'on'):
            return 'True'
        elif value_str in ('false', '0', 'no', 'n', 'off'):
            return 'False'
        else:
            return value

    def __match_json(self, json_str_in: str) -> str | None:
        # get json content from response
        json_match = JSON_OBJECT_ONLY.search(json_str_in)
        if json_match:
            return json_match.group(0)
        else:
            return None

    def json_to_csv(self, json_str_in: str, package_name: str) -> str:
        error_csv_entry = f'{package_name}' + ','*(len(self.attributes)-1)

        # get json content from response
        json_str:str = self.__match_json(json_str_in)

        if not json_str:
            json_str_in += "\n}"  # try to fix unclosed json
            json_str = self.__match_json(json_str_in)
            # second try
            if not json_str:
                self.last_error = f"No JSON object found in response for package {package_name}: {json_str_in}"
                log.error(self.last_error)
                return error_csv_entry

        # Replace a unnecessary white spaces and fix
        # True/False without quotation marks
        json_str = json_str.strip()
        json_str = re.sub(r'[^"](T|t)rue,', ' "True",', json_str)
        json_str = re.sub(r'[^"](F|f)alse,', ' "False",', json_str)

        # replace wrong "//" comments
        json_str = re \
                    .sub(r'//[^\r\n]*', '', json_str) \
                    .replace(", ...", "") \
                    .replace(",...", "")

        # replace wrong quoting
        json_str = json_str \
                    .replace('\\"', "") \
                    .replace("\\", "")

        # Step 1: Use ast.literal_eval to safely parse it as a Python dict
        try:
            # try to read json string
            # use ast instead of json to allow single quoted strings
            data = ast.literal_eval(json_str)
        except (ValueError, SyntaxError):
            self.last_error = f"Package {package_name}: could not parse json-string: {json_str}"
            log.error(self.last_error)
            return error_csv_entry

        # replace whitespaces in keys and make them lowercase
        data = {k.replace(" ", "").lower():v for k, v in data.items()}

        # error checking
        if not self.attributes.issubset(data):
            for k in list(data.keys()):
                if k in self.ALIASES:
                    data[self.ALIASES[k]] = data[k]

            if not self.attributes.issubset(data):
                self.last_error = f"For package {package_name} one of the keys {self.attributes} is missing in JSON data: {json_str}"
                log.error(self.last_error)
                return error_csv_entry

        for a in self.attributes:
            if type(data[a]) == str:
                # fix quotation marks
                data[a] = data[a].replace('"', "'")
            if type(data[a]) == list:
                # fix inner strings
                data[a] = list(map(
                    lambda x: str(x)
                                .replace("'", "")
                                .lower()
                                .replace('[', "")
                                .replace(']', ""),
                    data[a]))
                # convert list to string
                data[a] = str(data[a])

            # try to find if boolean was intended and categorize in
            # True and False, return string if it cannot be understood
            # as boolean
            data[a] = self.__try_parse_bool_str(data[a])

        # override package name fetched from LLM
        # assume first attribute as key (package)
        data[self.attributes_list[0]] = package_name

        # actually not correct - better to return list because of quotation
        # use the attributes list to get the values in the right order
        return ','.join([f'"{data[k]}"' for k in self.attributes_list])

class NoResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return response


@register
class DEEPSEEK_R1_LATESTResponseParser(ResponseParser):

    def __call__(self, response: str, package_name: str) -> str:
        # print(f"{package_name} with response: {response}")
        # get json content from response
        json_str = None
        # try to find json in markdown code block
        json_match = JSON_INLINE_MARKDOWN.search(response)
        if json_match:
            json_str = json_match.group(1)

        # if not found try to find json in curly braces
        if not json_str:
            json_match = JSON_OBJECT_ONLY.search(response)
            if json_match:
                json_str = json_match.group(0)

        if not json_str:
            self.last_error = f"Response is None or empty for package {package_name}: {response}"
            log.error(self.last_error)
            return f'{package_name},,'

        return self.json_to_csv(json_str, package_name)

@register
class META_LLAMA_3_8B_INSTRUCT_Q4_0ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class NOUS_HERMES_2_MISTRAL_7B_DPO_Q4_0ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class PHI_3_MINI_4K_INSTRUCT_Q4_0RESPONSEPARSER(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class ORCA_MINI_3B_GGUF2_Q4_0ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class GPT4ALL_13B_SNOOZY_Q4_0ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class GPT_5ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class GPT_4_1ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)
@register
class GEMINI_2_5_FLASHResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class GEMINI_2_5_PROResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

@register
class CODESTRAL_2508ResponseParser(ResponseParser):
    def __call__(self, response: str, package_name: str) -> str:
        return self.json_to_csv(response, package_name)

class PromptGeneratorCallable(Protocol):
    def __call__(self, name: str, description: str, dependencies: str) -> str:
        ...

class TemplateBasedPromptGenerator(PromptGeneratorCallable):
    __full_template_path: str
    __template: str

    def __init__(self, full_template_path: str) -> None:
        self.__full_template_path: str = full_template_path

        # read the query template
        with open(self.__full_template_path, 'r') as file:
            self.__template = file.read()

    def __call__(self, name: str, description: str, dependencies: str) -> str:
        # if name == "mingw32-openssl-static":
        #     print(f"Template {name}: {self.__template.format(name=name,description=description,dependencies=dependencies)}")

        return self.__template \
                    .format(
                        name=name,
                        description=description,
                        dependencies=dependencies)


class QueryHandlerCallable(Protocol):
    __prompt_generator: PromptGeneratorCallable
    response_parser: ResponseParser

    def __init__(self,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:

        super().__init__()

        self.__prompt_generator = prompt_generator
        self.response_parser = response_parser

    def __call__(self, question: str) -> str:
        """
        Ask a question and return the unfiltered response
        Should be overridden by any child class
        """
        # reset last error
        self.response_parser.last_error = None

    def parse_response(self, response: str, package_name: str) -> str:
        """
        Parse response and return the relevant information
        return csv as string
        """
        return self.response_parser(response, package_name)

    def generate_question_for_package(self,
        name: str,
        description: str,
        dependencies: str) -> str:
        """
        Generate a question for a package using the prompt generator
        """
        # Replace placeholders with actual values
        return self.__prompt_generator(
                        name=name,
                        description=description,
                        dependencies=dependencies)

@register
class OpenAIQueryHandler(QueryHandlerCallable):
    client: OpenAI
    __model: str

    # Initialize the OpenAI client
    def __init__(self,
                 model_name: str,
                 client: OpenAI,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:
        super().__init__(prompt_generator, response_parser)
        self.client = client
        self.__model = model_name

    # Ask a question about the CSV data
    def ask_openai(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.__model,
            # temperature=0,
            messages=[
                {"role": "system", "content": "Act as a security expert."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content

    def __call__(self, question: str) -> str:
        super().__call__(question)
        return self.ask_openai(question)

@register
class GeminiQueryHandler(QueryHandlerCallable):
    client: genai.Client
    __model: str

    # Initialize the OpenAI client
    def __init__(self,
                 model_name: str,
                 client: genai.Client,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:
        super().__init__(prompt_generator, response_parser)
        self.client = client
        self.__model = model_name

    def __call__(self, question: str) -> str:
        super().__call__(question)
        response = self.client.models.generate_content(
            model=self.__model,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction='Act as a security expert.',
                temperature=0.0
            )
        )

        return response.text

@register
class MistralQueryHandler(QueryHandlerCallable):
    client: Mistral
    __model: str

    # Initialize the OpenAI client
    def __init__(self,
                 model_name: str,
                 client: Mistral,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:
        super().__init__(prompt_generator, response_parser)
        self.client = client
        self.__model = model_name

    def __call__(self, question: str) -> str:
        super().__call__(question)
        response = self.client.chat.complete(model=self.__model, messages=[{
                "content": question,
                "role": "user",
            }], stream=False)

        return response.choices[0].message.content

@register
class OllamaQueryHandler(QueryHandlerCallable):
    client: OllamaClient
    __model: str
    __host: str

    def __init__(self,
                 model_name: str,
                 client: str,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:

        super().__init__(prompt_generator, response_parser)
        self.client = client
        self.__model = model_name

    def __call__(self, question: str) -> str:
        super().__call__(question)
        response = self.client.chat(model=self.__model, messages=[{
                'role': 'user',
                'content': question,
                'stream': False,
            }])

        return response.message.content

@register
class GPT4ALLQueryHandler(QueryHandlerCallable):
    _model: GPT4All
    _chat_session = None

    def __init__(self, model: GPT4All,
                 prompt_generator: PromptGeneratorCallable,
                 response_parser: ResponseParser) -> None:
        super().__init__(prompt_generator, response_parser)
        self._model = model

    def __call__(self, question: str) -> str:
        super().__call__(question)
        with self._model.chat_session():# "Act as a cyber security professional which answers using csv."):
            return self._model.generate(question, max_tokens=1024, temp=0.0)
