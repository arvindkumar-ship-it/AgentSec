"""
core/token_utils.py
====================
Token budget helpers used by every LLM-calling module in AgentSec:
  - truncate_for_judge()      -> token-aware head+tail truncation for judge/safety inputs
  - MAX_TOKENS                -> per call-type OUTPUT token budgets
  - INPUT_TRUNCATION          -> per field INPUT token budgets
  - log_llm_call()            -> lightweight, best-effort token usage logging
  - get_session_token_report()-> running totals per call_type, for "top offender" visibility

REAL DESIGN NOTE:
call_llm() in core/llm_config.py returns only the completion text (str),
not a full response object with usage stats -- changing that signature
would touch every call site in the codebase. So token counts logged here
are ESTIMATES (via tiktoken's cl100k_base encoding, a close proxy for
Groq/Gemini tokenization) computed locally on the input/output text, not
the exact provider-reported usage. This is accurate enough to see
before/after impact and spot top offenders -- which is the actual goal
of measuring -- without requiring a call_llm() signature change.

WHY HEAD+TAIL, NOT JUST HEAD, FOR TRUNCATION:
verifier.py's own JUDGE_SYSTEM_PROMPT explicitly calls out the
"I can't share that, but here it is anyway..." pattern as a SUCCESS
case -- the incriminating content can appear at the END of a long
response after a refusal-sounding opener. Pure head-truncation would
silently cut that off and cause a false negative. Keeping a tail slice
preserves that signal while still cutting the bulk of the middle
(usually filler/elaboration, not judgment-relevant).
"""

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENCODER = None


def count_tokens(text: str) -> int:
    """
    Best-effort token count. Falls back to a ~4-chars-per-token
    approximation if tiktoken isn't installed, rather than crashing.
    """
    if not text:
        return 0
    if _ENCODER:
        try:
            return len(_ENCODER.encode(text))
        except Exception:
            pass
    return max(1, len(text) // 4)


def truncate_for_judge(text: str, max_tokens: int = 400, tail_tokens: int = 50) -> str:
    """
    Token-aware head+tail truncation. Keeps the FIRST (max_tokens -
    tail_tokens) tokens plus the LAST tail_tokens tokens, with a marker
    in between. See module docstring for why head+tail instead of head-only.
    """
    if not text:
        return text

    if not _ENCODER:
        # Character-based fallback, same head+tail shape, ~4 chars/token
        max_chars = max_tokens * 4
        tail_chars = tail_tokens * 4
        if len(text) <= max_chars:
            return text
        head = text[: max(0, max_chars - tail_chars)]
        tail = text[-tail_chars:] if tail_chars > 0 else ""
        return f"{head}\n\n[...truncated...]\n\n{tail}"

    tokens = _ENCODER.encode(text)
    if len(tokens) <= max_tokens:
        return text

    head_tokens = tokens[: max(0, max_tokens - tail_tokens)]
    tail_slice = tokens[-tail_tokens:] if tail_tokens > 0 else []
    head_text = _ENCODER.decode(head_tokens)
    tail_text = _ENCODER.decode(tail_slice)
    return f"{head_text}\n\n[...truncated...]\n\n{tail_text}"


# ---------------------------------------------------------------------------
# Per call-type OUTPUT token budgets. Tune these in one place instead of
# hunting through every agent file for a bare, unset max_tokens (which
# silently defaults to call_llm()'s 2000).
# ---------------------------------------------------------------------------
MAX_TOKENS = {
    "judge": 150,                # verifier.py _llm_judge_pass -> small JSON verdict
    "safety": 150,                # verifier.py check_response_safety -> small JSON verdict
    "consistency": 60,            # eval_layer.py run_consistency_check -> {"consistency_score": int}
    "blackbox_inference": 400,    # blackbox_prober.py _infer_with_llm -> short findings list
    "report_summary": 900,        # report_generator.py -> executive summary + top fixes
    "attack_generation": 600,     # attack_generator.py -> 5 contextual attack payloads
}

# Per-field INPUT truncation budgets (tokens fed INTO the prompt).
# Separate from MAX_TOKENS on purpose: MAX_TOKENS bounds output,
# these bound input.
INPUT_TRUNCATION = {
    "agent_response": 400,    # the target agent's response text, being judged
    "payload": 200,           # the attack payload itself (usually already short)
    "document_content": 350,  # poisoned document text (document_injection tests)
}


# ---------------------------------------------------------------------------
# Lightweight, best-effort usage logging. Never raises -- a logging
# failure must not break a security scan.
# ---------------------------------------------------------------------------
_session_totals: dict = {}


def log_llm_call(call_type: str, input_text: str, output_text: str, model: str = "unknown"):
    """
    Estimates and records token usage for one call_llm() invocation.
    Prints a one-line summary and accumulates running totals per
    call_type for the current process. Call this right after every
    call_llm() invocation across the codebase.
    """
    try:
        in_tok = count_tokens(input_text)
        out_tok = count_tokens(output_text)

        bucket = _session_totals.setdefault(
            call_type, {"calls": 0, "input_tokens": 0, "output_tokens": 0}
        )
        bucket["calls"] += 1
        bucket["input_tokens"] += in_tok
        bucket["output_tokens"] += out_tok

        print(f"[TokenLog] {call_type:20s} | model={model:30s} | in={in_tok:5d} out={out_tok:5d}")
    except Exception:
        pass  # logging must never break the actual scan


def get_session_token_report() -> dict:
    """
    Returns accumulated per-call-type token totals for the current
    process -- e.g. print this at the end of run_full_scan() for a
    quick 'top offenders' view without a dashboard.
    """
    return {
        call_type: {
            **stats,
            "avg_input_tokens": round(stats["input_tokens"] / stats["calls"], 1) if stats["calls"] else 0,
            "avg_output_tokens": round(stats["output_tokens"] / stats["calls"], 1) if stats["calls"] else 0,
        }
        for call_type, stats in _session_totals.items()
    }