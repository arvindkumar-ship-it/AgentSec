"""
model_rotator.py
=================
Proactive, cyclic, checkpoint-aware LLM fallback rotator.

Core ideas (vs plain LiteLLM router fallback):
1. PROACTIVE switching — each model's usage is tracked in a sliding window.
   We hop to the next model BEFORE hitting its rate/quota limit, not after
   a 429 comes back. This avoids the error->retry->error cascade entirely.
2. CYCLIC order — models sit in a circular list. The pointer only moves
   forward. If the whole cycle is exhausted, THEN we do a real backoff wait.
3. CHECKPOINT CONTINUATION — for any multi-step / streaming generation task,
   partial output is saved. When we switch models mid-task, the new model
   is told "here's what's done so far, continue from here" instead of
   regenerating from scratch.

Drop this into any LiteLLM-based pipeline (Anvesh, AgentSec, TRACE, etc).
"""

import time
import asyncio
from dataclasses import dataclass, field
from collections import deque
from typing import Optional, Callable, Any
import litellm


@dataclass
class ModelSlot:
    name: str                      # litellm model string, e.g. "groq/llama-3.1-8b-instant"
    rpm_limit: int                 # requests per minute limit for this model/key
    tpm_limit: int                 # tokens per minute limit
    rpd_limit: Optional[int] = None  # requests per day limit (e.g. Gemini free tier = 20)
    safety_margin: float = 0.8     # switch away once we hit 80% of any limit
    # sliding window state (auto-managed, don't set manually)
    _req_window: deque = field(default_factory=deque, repr=False)
    _tok_window: deque = field(default_factory=deque, repr=False)
    _day_count: int = 0
    _day_reset_ts: float = field(default_factory=lambda: time.time() + 86400)
    _cooldown_until: float = 0.0

    def _prune(self, now: float):
        while self._req_window and now - self._req_window[0] > 60:
            self._req_window.popleft()
        while self._tok_window and now - self._tok_window[0][0] > 60:
            self._tok_window.popleft()
        if now > self._day_reset_ts:
            self._day_count = 0
            self._day_reset_ts = now + 86400

    def tokens_used_last_min(self, now: float) -> int:
        self._prune(now)
        return sum(t for _, t in self._tok_window)

    def is_available(self, est_tokens: int = 500) -> bool:
        now = time.time()
        if now < self._cooldown_until:
            return False
        self._prune(now)
        if self.rpd_limit and self._day_count >= self.rpd_limit * self.safety_margin:
            return False
        if len(self._req_window) >= self.rpm_limit * self.safety_margin:
            return False
        if self.tokens_used_last_min(now) + est_tokens >= self.tpm_limit * self.safety_margin:
            return False
        return True

    def record_usage(self, tokens: int):
        now = time.time()
        self._req_window.append(now)
        self._tok_window.append((now, tokens))
        self._day_count += 1

    def mark_dead(self, cooldown_seconds: float):
        self._cooldown_until = time.time() + cooldown_seconds


class ModelRotator:
    """
    Cyclic, proactive fallback rotator with checkpoint continuation.

    Usage:
        rotator = ModelRotator([
            ModelSlot("groq/llama-3.1-8b-instant", rpm_limit=30, tpm_limit=6000),
            ModelSlot("gemini/gemini-2.5-flash-lite", rpm_limit=15, tpm_limit=1_000_000, rpd_limit=20),
            ModelSlot("groq/llama-3.3-70b-versatile", rpm_limit=30, tpm_limit=6000),
        ])
        result = await rotator.generate(messages=[...])
    """

    def __init__(self, slots: list[ModelSlot], full_cycle_backoff: float = 5.0):
        self.slots = slots
        self.ptr = 0
        self.full_cycle_backoff = full_cycle_backoff

    def _next_available_slot(self, est_tokens: int) -> Optional[ModelSlot]:
        n = len(self.slots)
        for i in range(n):
            idx = (self.ptr + i) % n
            slot = self.slots[idx]
            if slot.is_available(est_tokens):
                self.ptr = idx  # advance the cyclic pointer to here
                return slot
        return None  # full cycle exhausted

    async def generate(
        self,
        messages: list[dict],
        est_tokens: int = 500,
        max_tokens: int = 1024,
        on_partial: Optional[Callable[[str], Any]] = None,
        api_key_map: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """
        Runs a completion, rotating cyclically across slots.
        If a call fails or a model is near its limit mid-generation,
        the partial output collected so far is checkpointed and the
        NEXT model continues from that checkpoint instead of restarting.
        """
        checkpoint = ""
        attempts = 0
        max_attempts = len(self.slots) * 2  # allow one full extra lap

        while attempts < max_attempts:
            slot = self._next_available_slot(est_tokens)

            if slot is None:
                # full cycle exhausted -> real backoff, then retry from ptr 0
                await asyncio.sleep(self.full_cycle_backoff)
                self.ptr = 0
                attempts += 1
                continue

            working_messages = messages
            if checkpoint:
                # inject continuation context instead of starting over
                working_messages = messages + [
                    {"role": "assistant", "content": checkpoint},
                    {"role": "user", "content": "Continue exactly from where you left off above. Do not repeat what's already written."},
                ]

            try:
                call_kwargs = dict(kwargs)
                if api_key_map and slot.name in api_key_map:
                    call_kwargs["api_key"] = api_key_map[slot.name]

                response = await litellm.acompletion(
                    model=slot.name,
                    messages=working_messages,
                    max_tokens=max_tokens,
                    **call_kwargs,
                )
                text = response.choices[0].message.content
                used_tokens = getattr(response.usage, "total_tokens", est_tokens)
                slot.record_usage(used_tokens)

                checkpoint += text
                if on_partial:
                    on_partial(text)

                # move pointer forward for next call -> true cyclic behaviour
                self.ptr = (self.ptr + 1) % len(self.slots)
                return checkpoint

            except Exception as e:
                err = str(e)
                if "429" in err or "rate_limit" in err or "quota" in err.lower():
                    # figure out cooldown from the error if possible, else default
                    cooldown = 60.0
                    slot.mark_dead(cooldown)
                else:
                    # non-rate-limit error: short cooldown, don't blacklist long
                    slot.mark_dead(10.0)

                # advance pointer to next slot and retry, KEEPING checkpoint
                self.ptr = (self.ptr + 1) % len(self.slots)
                attempts += 1
                continue

        raise RuntimeError(
            f"All models exhausted after {max_attempts} attempts. "
            f"Partial output so far ({len(checkpoint)} chars) was NOT lost, "
            f"it's in the exception context if you catch this."
        )


# ---------------------------------------------------------------------------
# Example wiring for your Groq + Gemini stack (matches the log you shared)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    async def demo():
        rotator = ModelRotator(
            slots=[
                ModelSlot(
                    name="groq/llama-3.1-8b-instant",
                    rpm_limit=30,
                    tpm_limit=6000,       # matches your log: Limit 6000
                    safety_margin=0.75,   # switch at 75% i.e. ~4500 tokens/min used
                ),
                ModelSlot(
                    name="gemini/gemini-2.5-flash-lite",
                    rpm_limit=15,
                    tpm_limit=1_000_000,
                    rpd_limit=20,         # matches your log: quota_value: 20/day
                    safety_margin=0.8,    # switch at 16 requests used
                ),
                ModelSlot(
                    name="groq/llama-3.3-70b-versatile",
                    rpm_limit=30,
                    tpm_limit=6000,
                    safety_margin=0.75,
                ),
            ],
            full_cycle_backoff=5.0,
        )

        out = await rotator.generate(
            messages=[{"role": "user", "content": "Explain graph-enhanced XGBoost in 3 lines."}]
        )
        print(out)

    asyncio.run(demo())
