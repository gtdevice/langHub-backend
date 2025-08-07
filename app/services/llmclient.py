import logging
from typing import Dict, Any, Type

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel
from json_repair import repair_json
from langchain.output_parsers import OutputFixingParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
extended_model_name = "openai/gpt-4.1-mini"  # expencive model for reasoning tasks

def wrapper_repair_json(input):
    res = repair_json(input)
    return res

def transform_string(message: AIMessage) -> str:
    """
    Transforms the input string by removing leading and trailing whitespace.
    This is a placeholder for any additional transformations needed.
    """
    cnt = message.content
    return cnt.strip().replace("```json", "").replace("```", "")

async def callLLM(
    prompt_template_str: str,
    prompt_args: Dict[str, Any],
    output_schema: Type[BaseModel],
    extended_model: bool = False
) -> BaseModel:
    """
    Calls the OpenRouter API with a given prompt template and arguments using LangChain.
    Includes a retry mechanism and returns a Pydantic object.
    """
    try:
        llm = ChatOpenAI(
            model=settings.openrouter_model_name if not extended_model else extended_model_name,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base=settings.openrouter_api_base,
            max_retries=3,
        )
        if extended_model:
            logger.info(f"Using extended model: {extended_model_name}")
            tool = {"type": "web_search_preview"}
            llm = llm.bind_tools([tool])

        parser = PydanticOutputParser(pydantic_object=output_schema)
        new_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        prompt_template = ChatPromptTemplate.from_template(
            template=prompt_template_str,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        logger.info(prompt_template.pretty_print())

        chain = prompt_template | llm | transform_string |  RunnableLambda(wrapper_repair_json) | new_parser

        logger.info(f"Calling LLM: model={settings.openrouter_model_name}, template='{prompt_template_str}', args={prompt_args}")
        response = await chain.ainvoke(prompt_args)
        logger.info(f"LLM response: {response}")

        return response

    except OutputParserException as e:
        logger.error(f"Error parsing LLM output: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
