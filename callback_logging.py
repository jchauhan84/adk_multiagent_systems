import logging

from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext

def log_query_to_model(llm_request: LlmRequest, callback_context: CallbackContext):
    if llm_request.contents and llm_request.contents[-1].role == "user":
        for part in llm_request.contents[-1].parts:
            if part.text:
                logging.info("[query to %s]: %s", callback_context.agent_name, part.text)

def log_model_response(llm_response: LlmResponse, callback_context: CallbackContext):
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info("[response from %s]: %s", callback_context.agent_name, part.text)
            elif part.function_call:
                logging.info("[response call from %s]: %s", callback_context.agent_name, part.function_call.name)