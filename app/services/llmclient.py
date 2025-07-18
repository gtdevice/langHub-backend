import logging
from typing import Dict, Any, Type
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def callLLM(
    prompt_template_str: str,
    prompt_args: Dict[str, Any],
    output_schema: Type[BaseModel]
) -> BaseModel:
    """
    Calls the OpenRouter API with a given prompt template and arguments using LangChain.
    Includes a retry mechanism and returns a Pydantic object.
    """
    try:
        llm = ChatOpenAI(
            model=settings.openrouter_model_name,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base=settings.openrouter_api_base,
            max_retries=3,
        )

        parser = PydanticOutputParser(pydantic_object=output_schema)
        prompt_template = ChatPromptTemplate.from_template(
            template=prompt_template_str,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt_template | llm | parser

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
