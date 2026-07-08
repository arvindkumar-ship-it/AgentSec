# import litellm
# from config import settings

# litellm.set_verbose = False


# async def call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
#     """
#     LiteLLM fallback chain: Groq → Gemini
#     Groq fails → silently falls to Gemini.
#     """
#     providers = [
#         ("groq/llama-3.1-8b-instant", settings.GROQ_API_KEY),
#         ("gemini/gemini-2.5-flash-lite", settings.GEMINI_API_KEY),
#     ]

#     last_error = None
#     for model, api_key in providers:
#         try:
#             response = await litellm.acompletion(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 api_key=api_key,
#             )
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             last_error = e
#             continue

#     raise Exception(f"All LLM providers failed. Last error: {last_error}")








# import litellm
# from config import settings
# from .model_rotator import ModelRotator, ModelSlot

# litellm.set_verbose = False

# # ---------------------------------------------------------------------------
# # Cyclic, proactive fallback rotator: Groq (8b) -> Gemini -> Groq (70b) -> ...
# # Switches BEFORE hitting rate/quota limits, not after a 429.
# # ---------------------------------------------------------------------------
# _rotator = ModelRotator(
#     slots=[
#         ModelSlot(
#             name="groq/llama-3.1-8b-instant",
#             rpm_limit=30,
#             tpm_limit=6000,        # matches Groq free-tier org limit from logs
#             safety_margin=0.75,    # hop away at ~75% usage, before 429
#         ),
#         ModelSlot(
#             name="gemini/gemini-2.5-flash-lite",
#             rpm_limit=15,
#             tpm_limit=1_000_000,
#             rpd_limit=20,           # matches Gemini free-tier daily quota
#             safety_margin=0.8,
#         ),
#         ModelSlot(
#             name="groq/llama-3.3-70b-versatile",
#             rpm_limit=30,
#             tpm_limit=6000,
#             safety_margin=0.75,
#         ),
#     ],
#     full_cycle_backoff=5.0,
# )

# # api_key per model, since ModelRotator doesn't know about your settings module
# _API_KEYS = {
#     "groq/llama-3.1-8b-instant": settings.GROQ_API_KEY,
#     "gemini/gemini-2.5-flash-lite": settings.GEMINI_API_KEY,
#     "groq/llama-3.3-70b-versatile": settings.GROQ_API_KEY,
# }


# async def call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
#     """
#     Cyclic proactive fallback chain: Groq(8b) -> Gemini -> Groq(70b) -> back to Groq(8b)...
#     Each model's usage is tracked in a sliding window; we rotate to the next
#     model BEFORE hitting its limit, so a 429 cascade like the one in your
#     logs shouldn't happen anymore. If a call does fail mid-way, partial
#     output is checkpointed and the next model continues from there instead
#     of starting over.
#     """
#     return await _rotator.generate(
#         messages=messages,
#         max_tokens=max_tokens,
#         temperature=temperature,
#         est_tokens=min(max_tokens, 1500),
#         api_key_map=_API_KEYS,
#     )

# import litellm
# from config import settings
# from .model_rotator import ModelRotator, ModelSlot

# litellm.set_verbose = False

# # ---------------------------------------------------------------------------
# # Cyclic, proactive fallback rotator: Groq (8b) -> Groq (70b) -> back to 8b...
# # Switches BEFORE hitting rate/quota limits, not after a 429.
# # Gemini removed: free tier daily quota (20/day) too low to be usable.
# # ---------------------------------------------------------------------------
# _rotator = ModelRotator(
#     slots=[
#         ModelSlot(
#             name="groq/llama-3.1-8b-instant",
#             rpm_limit=30,
#             tpm_limit=6000,        # matches Groq free-tier org limit from logs
#             safety_margin=0.75,    # hop away at ~75% usage, before 429
#         ),
#         ModelSlot(
#             name="groq/llama-3.3-70b-versatile",
#             rpm_limit=30,
#             tpm_limit=6000,
#             safety_margin=0.75,
#         ),
#     ],
#     full_cycle_backoff=5.0,
# )

# _API_KEYS = {
#     "groq/llama-3.1-8b-instant": settings.GROQ_API_KEY,
#     "groq/llama-3.3-70b-versatile": settings.GROQ_API_KEY,
# }


# async def call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
#     """
#     Cyclic proactive fallback chain: Groq(8b) -> Groq(70b) -> back to Groq(8b)...
#     """
#     return await _rotator.generate(
#         messages=messages,
#         max_tokens=max_tokens,
#         temperature=temperature,
#         est_tokens=min(max_tokens, 1500),
#         api_key_map=_API_KEYS,
#     )




import litellm
from config import settings
from .model_rotator import ModelRotator, ModelSlot

litellm.set_verbose = False

# ---------------------------------------------------------------------------
# Cyclic, proactive fallback rotator: Groq (8b) -> Groq (70b) -> back to 8b...
# Switches BEFORE hitting rate/quota limits, not after a 429.
#
# Gemini (gemini-2.5-flash-lite) was removed from this rotation: its free
# tier daily quota is 20 requests/day per project/model, which a scanner
# doing dozens of judge calls per run exhausts almost immediately. Once
# exhausted, the quota does not reset on server restart (it's tracked
# server-side by Google, not by our in-memory usage counters), so it kept
# producing 429 cascades even after a restart. If Gemini is reintroduced
# later, it must be paired with a hard daily blacklist keyed off actual
# 429/quota errors -- not just a local rpd_limit counter -- since the
# local counter has no way to know the remote quota was already used up
# in a previous process.
#
# Single source of truth: model name + limits live ONLY in _MODEL_CONFIG.
# Do not hardcode model name strings anywhere else in this file.
# ---------------------------------------------------------------------------
_MODEL_CONFIG = {
    "groq/llama-3.1-8b-instant": {
        "api_key": settings.GROQ_API_KEY,
        "rpm_limit": 30,
        "tpm_limit": 6000,      # matches Groq free-tier org limit
        "safety_margin": 0.75,  # hop away at ~75% usage, before 429
    },
    "groq/llama-3.3-70b-versatile": {
        "api_key": settings.GROQ_API_KEY,
        "rpm_limit": 30,
        "tpm_limit": 6000,
        "safety_margin": 0.75,
    },
}

_rotator = ModelRotator(
    slots=[
        ModelSlot(name=name, **{k: v for k, v in cfg.items() if k != "api_key"})
        for name, cfg in _MODEL_CONFIG.items()
    ],
    full_cycle_backoff=5.0,
)

_API_KEYS = {name: cfg["api_key"] for name, cfg in _MODEL_CONFIG.items()}


async def call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
    """
    Cyclic proactive fallback chain across Groq models: 8b -> 70b -> 8b...

    Each model's usage is tracked in a sliding window inside ModelRotator;
    we rotate to the next model BEFORE hitting its limit, so a 429 cascade
    shouldn't happen under normal operation.

    NOTE: if one model fails mid-call, the next model retries the SAME
    prompt from scratch. There is no token-level continuation of a
    partial completion across models -- that is not something the
    underlying API supports without explicitly re-injecting partial
    output into the prompt, which this rotator does not currently do.

    Raises an Exception (with the last underlying error attached) if
    every provider in the rotation fails.
    """
    try:
        return await _rotator.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            api_key_map=_API_KEYS,
        )
    except Exception as e:
        raise Exception(f"call_llm failed after exhausting all providers: {e}") from e