'''
LLM Factory

all in one LLM provider factory

reference: 
- https://python.langchain.com/docs/integrations/chat/
'''
import os
from dotenv import load_dotenv

from langchain_ollama.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_deepseek import ChatDeepSeek


env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path, override=True)


class LLM_Provider:
    """
    LLM Provider Factory

    Supported providers:
        - ollama:      (local, open source)
        - anthropic:   (Claude)
        - openai:      (OpenAI API)
        - azure:       (Azure OpenAI)
        - google:      (Google Generative AI)
        - deepseek:    (DeepSeek)
        - mistral:     (Mistral AI)

    Args:
        model (str): Model name or deployment (see provider docs)
        provider (str): Provider name
        base_url (str, optional): Custom endpoint (if supported)
        api_key (str, optional): API key (if not set in env)

    Raises:
        ValueError: If required credentials/config are missing or provider is not supported.
    """
    def __init__(self, model: str, provider: str, base_url: str = None, api_key: str = None):
        """
        Initialize the LLM_Provider with the specified model and provider.
        Args:
            model (str): Model name or deployment (see provider docs)
            provider (str): Provider name
            base_url (str, optional): Custom endpoint (if supported)
            api_key (str, optional): API key (if not set in env)
        Raises:
            ValueError: If required credentials/config are missing or provider is not supported.
        """
        self.model_name = model
        self.provider = provider.lower()
        self.base_url = base_url
        self.api_key = api_key

        # Initialize the LLM provider
        if self.provider == "ollama":
            self.model = ChatOllama(
                model=self.model_name,
                base_url=self.base_url
            )
        elif self.provider == "anthropic":
            if not self.api_key:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key not found. Set api_key or ANTHROPIC_API_KEY.")
            self.model = ChatAnthropic(
                api_key=self.api_key,
                model=self.model_name
            )
        elif self.provider == "openai":
            if not self.api_key:
                self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set api_key or OPENAI_API_KEY.")
            openai_endpoint = self.base_url or os.getenv("OPENAI_ENDPOINT")
            self.model = ChatOpenAI(
                api_key=self.api_key,
                model=self.model_name,
                base_url=openai_endpoint
            )
        elif self.provider == "azure":
            if not self.api_key:
                self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("Azure OpenAI API key not found. Set api_key or AZURE_OPENAI_API_KEY.")
            azure_endpoint = self.base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", self.model_name)
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
            if not azure_endpoint:
                raise ValueError("Azure OpenAI endpoint not found. Set base_url or AZURE_OPENAI_ENDPOINT.")
            self.model = AzureChatOpenAI(
                api_key=self.api_key,
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                api_version=api_version,
                model=self.model_name
            )
        elif self.provider == "google":
            if not self.api_key:
                self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("Google API key not found. Set api_key or GOOGLE_API_KEY.")
            self.model = ChatGoogleGenerativeAI(
                google_api_key=self.api_key,
                model=self.model_name
            )
        elif self.provider == "deepseek":
            if not self.api_key:
                self.api_key = os.getenv("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError("DeepSeek API key not found. Set api_key or DEEPSEEK_API_KEY.")
            deepseek_endpoint = self.base_url or os.getenv("DEEPSEEK_ENDPOINT")
            self.model = ChatDeepSeek(
                api_key=self.api_key,
                model=self.model_name,
                base_url=deepseek_endpoint
            )
        elif self.provider == "mistral":
            if not self.api_key:
                self.api_key = os.getenv("MISTRAL_API_KEY")
            if not self.api_key:
                raise ValueError("Mistral API key not found. Set api_key or MISTRAL_API_KEY.")
            mistral_endpoint = self.base_url or os.getenv("MISTRAL_ENDPOINT")
            self.model = ChatMistralAI(
                api_key=self.api_key,
                model=self.model_name,
                base_url=mistral_endpoint
            )
        else:
            raise ValueError(f"Provider '{self.provider}' not supported.")


    def invoke_chat(self, prompt: str) -> str:
        """
        Chat with the LLM provider.
        Args:
            prompt (str): Input prompt.
        Returns:
            str: LLM response.
        """
        try:
            result = self.model.invoke(prompt)
            return getattr(result, "content", str(result))
        except Exception as exc:
            return f"[LLM invocation error: {exc}]"

    def stream_chat(self, prompt: str):
        """
        Stream chat with the LLM provider.
        Args:
            prompt (str): Input prompt.
        Returns:
            Generator or stream object from the provider.
        """
        try:
            return self.model.stream(prompt)
        except Exception as exc:
            yield f"[LLM streaming error: {exc}]"


if __name__ == '__main__':
    """
    Example usage and basic test for LLM_Provider.
    Uncomment and configure as needed for local testing.
    """
    # Example for Google Generative AI
    google_api_key = os.getenv("GOOGLE_API_KEY")
    print("Google API Key:", "[REDACTED]" if google_api_key else "Not Found")
    # input("Press Enter to continue...")
    if google_api_key:
        llm_google = LLM_Provider(
            model="gemini-2.0-flash-exp",
            provider="google",
            api_key=google_api_key
        )
        print("Google Generative AI Response:", llm_google.invoke_chat("Hello, how are you? Do you know who I am?"))
    else:
        print("No Google API Key found. Please set GOOGLE_API_KEY in your environment.")