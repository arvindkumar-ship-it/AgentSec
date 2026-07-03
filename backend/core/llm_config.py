import litellm
from config import settings

litellm.set_verbose = False


async def call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
    """
    LiteLLM fallback chain: Groq → Gemini
    Groq fails → silently falls to Gemini.
    """
    providers = [
        ("groq/llama-3.3-70b-versatile", settings.GROQ_API_KEY),
        ("gemini/gemini-1.5-flash", settings.GEMINI_API_KEY),
    ]

    last_error = None
    for model, api_key in providers:
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"All LLM providers failed. Last error: {last_error}")
