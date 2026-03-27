from google.adk.plugins import BasePlugin
from google.adk.models import LlmResponse
from google.genai import types

class Graceful429Plugin(BasePlugin):
    """Intercepts local failures to Vertex AI and handles them globally."""

    def __init__(self,name: str,fallback_text: str | dict):
        super().__init__(name)
        self.fallback_text = fallback_text
    
    def _get_fallback_text(self,request_contents) -> str:
        """Determines the fallback text to return based on the type of fallback_text provided."""
        if isinstance(self.fallback_text, str):
            return self.fallback_text
        
        # Convert the request object/dict/args to a lowercase strings for easy keyword hunting.
        request_str = str(request_contents).lower()

        best_keyword = None
        best_index = -1

        for keyword,response in self.fallback_text.items():
            if keyword == "default":
                continue
            idx = req_str.rfind(keyword.lower())
            if idx > best_index:
                best_index = idx
                best_keyword = keyword
        if best_keyword:
            return self.fallback_text[best_keyword]
        
        #if no keywords are matched,return the default if provided
        return self.fallback_text.get("default","**[System]** Quota exhausted. Please try again later.")
    
    async def on_model_error(
            self,
            *,
            agent,
            model.
            input,
            error,
    )-> LlmResponse | None:
        """Standard ADK hook for intercepting errors from the model. If the error is a 429, we return a fallback response instead of propagating the error."""
        if "RESOURCE_EXHAUSTED" in str(error) or "QUOTA_EXCEEDED" in str(error) or "429" in str(error):
            print(f"\n[Graceful429Plugin] Caught a quota exhaustion error from the model: {error}. Returning a graceful fallback response instead of propagating the error.\n")
            fallback = self._get_fallback_text(input)
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=fallback)]
                )
            )
        return None
    
    def apply_test_failover(self,agent):
        """Surgically patches the agent's model to simulate 429 errors."""
        async def forced_429_failover(*args,**kwargs):
            try:
                raise Exception("Simulated 429 error for testing Graceful429Plugin failover.")