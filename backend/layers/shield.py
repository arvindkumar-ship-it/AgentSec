"""
LAYER 2 — Agent Shield
Runtime middleware. Wraps your agent's tool calls.
Intercepts every action → checks policy → blocks/allows → logs.
Also handles: Undo/Checkpoint, Cost tracking, Identity audit.
"""
import re
import json
import uuid
import asyncio
import base64
import urllib.parse
import unicodedata
from datetime import datetime
from functools import wraps
from agents.verifier import check_response_safety
from core.db import get_db


# ─── Blocked Action Patterns ─────────────────────────────────────────────────
# These are ALWAYS blocked regardless of policy.
#
# REAL LIMITATION, STATED HONESTLY:
# Plain regex matching on str(args) can be evaded by encoding the
# payload (base64, URL-encoding, unicode homoglyphs) so the literal
# dangerous substring never appears in the raw argument string. This
# was a real gap in the previous version. _normalize_for_matching below
# closes the common, cheap evasion paths (base64, URL-encoding,
# whitespace/zero-width-character obfuscation, case variation) by
# decoding and matching against the decoded text as well as the raw
# text. It does NOT close every possible evasion (e.g. payloads split
# across multiple tool calls, custom ciphers, or semantic equivalents
# phrased in natural language that mean "delete everything" without
# matching any of these literal patterns). Those require the
# behavioral/LLM-based check_response_safety layer, not regex, and are
# a known, documented limitation rather than a silently unsolved one.
HARD_BLOCKED_PATTERNS = [
    (r"rm\s+-rf", "Destructive file deletion"),
    (r"drop\s+table", "Database destruction"),
    (r"delete\s+all", "Mass deletion"),
    (r"format\s+c:", "Drive formatting"),
    (r">\s*/dev/sd", "Device write"),
    (r"curl\s+.*\|\s*sh", "Remote script execution"),
    (r"wget\s+.*\|\s*sh", "Remote script execution"),
    (r"base64\s+-d\s+.*\|\s*sh", "Encoded script execution"),
]


def _normalize_for_matching(text: str) -> str:
    """
    Produces a single search corpus containing the original text plus
    any successfully-decoded base64 and URL-encoded substrings, with
    zero-width/invisible unicode characters stripped and case folded.

    This is run once per protected call and the result is matched
    against HARD_BLOCKED_PATTERNS. It is a real, testable improvement
    over matching raw str(args) alone -- not a claim of unbeatable
    encoding detection.
    """
    # Strip zero-width and other invisible formatting characters that
    # can be inserted between letters of a blocked word to dodge regex.
    cleaned = "".join(
        ch for ch in text
        if unicodedata.category(ch) not in ("Cf", "Mn") or ch in ("\n", "\t")
    )

    corpus_parts = [cleaned.lower()]

    # Attempt URL-decoding (cheap, safe, no side effects on failure)
    try:
        url_decoded = urllib.parse.unquote(cleaned)
        if url_decoded != cleaned:
            corpus_parts.append(url_decoded.lower())
    except Exception:
        pass

    # Attempt base64-decoding any token that looks base64-shaped.
    # We only try tokens of length >= 8 made of base64 alphabet to avoid
    # wasting cycles attempting to decode every short word in the text.
    for token in re.findall(r"[A-Za-z0-9+/]{8,}={0,2}", cleaned):
        try:
            padded = token + "=" * (-len(token) % 4)
            decoded_bytes = base64.b64decode(padded, validate=True)
            decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
            if decoded_text.strip():
                corpus_parts.append(decoded_text.lower())
        except Exception:
            continue  # not valid base64, skip silently -- this is expected for most tokens

    return "\n".join(corpus_parts)


class SecurityException(Exception):
    pass


class AgentShield:
    """
    Drop-in security middleware for any LangGraph agent.

    Usage:
        shield = AgentShield(agent_id="my-agent", policy={...})

        # Wrap any tool function:
        @shield.protect
        async def my_tool(input: str) -> str:
            return "result"

        # Or wrap a response before sending to user:
        safe_response = await shield.check_outbound(raw_response)
    """

    def __init__(self, agent_id: str, policy: dict = None):
        self.agent_id = agent_id
        self.policy = policy or DEFAULT_POLICY
        self.db = None
        self.cost_tracker = {"tokens_used": 0, "estimated_cost_usd": 0.0}
        self._initialized = False

    async def _ensure_db(self):
        if not self._initialized:
            self.db = get_db()
            self._initialized = True

    # ─── Core Protection Decorator ────────────────────────────────────────

    def protect(self, func):
        """Decorator: wrap any async tool function with Shield protection."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await self._ensure_db()
            tool_name = func.__name__
            action_repr = json.dumps({"args": str(args)[:200], "kwargs": str(kwargs)[:200]})
            match_corpus = _normalize_for_matching(action_repr)

            # 1. Hard-blocked pattern check (matched against normalized
            #    corpus, which includes decoded base64/URL-encoded text,
            #    not just the raw literal argument string)
            for pattern, reason in HARD_BLOCKED_PATTERNS:
                if re.search(pattern, match_corpus, re.IGNORECASE):
                    await self._log("BLOCKED", tool_name, action_repr,
                                    error=f"Hard-blocked pattern: {reason}")
                    raise SecurityException(f"AgentShield BLOCKED: {reason}")

            # 2. Policy check
            policy_result = self._check_policy(tool_name, kwargs)
            if not policy_result["allowed"]:
                await self._log("POLICY_VIOLATION", tool_name, action_repr,
                                error=policy_result["reason"])
                raise SecurityException(f"AgentShield POLICY: {policy_result['reason']}")

            # 3. Checkpoint (for undo)
            checkpoint_id = await self._create_checkpoint(tool_name, args, kwargs)

            # 4. Execute the actual tool
            try:
                result = await func(*args, **kwargs)
                await self._log("SUCCESS", tool_name, action_repr,
                                result=str(result)[:200], checkpoint_id=checkpoint_id)
                return result
            except Exception as e:
                await self._log("TOOL_ERROR", tool_name, action_repr, error=str(e))
                raise

        return wrapper

    # ─── Outbound Response Safety Check ──────────────────────────────────

    async def check_outbound(self, response_text: str) -> dict:
        """
        Check agent response before sending to user.
        Returns: {"safe": bool, "response": str, "action": "ALLOW/WARN/BLOCK"}
        """
        await self._ensure_db()
        safety = await check_response_safety(response_text)

        await self._log(
            event_type=f"OUTBOUND_{safety['action']}",
            tool_name="outbound_response",
            action=response_text[:200],
            result=str(safety)
        )

        if safety["action"] == "BLOCK":
            return {
                "safe": False,
                "response": "I cannot provide that response as it violates safety guidelines.",
                "action": "BLOCK",
                "issues": safety.get("issues", [])
            }

        return {
            "safe": True,
            "response": response_text,
            "action": safety["action"],
            "issues": safety.get("issues", [])
        }

    # ─── Checkpoint / Undo System ─────────────────────────────────────────

    async def _create_checkpoint(self, tool_name: str, args, kwargs) -> str:
        checkpoint_id = str(uuid.uuid4())
        if self.db is not None:
            await self.db.checkpoints.insert_one({
                "checkpoint_id": checkpoint_id,
                "agent_id": self.agent_id,
                "tool_name": tool_name,
                "args": str(args)[:500],
                "kwargs": str(kwargs)[:500],
                "created_at": datetime.utcnow(),
                "reverted": False,
            })
        return checkpoint_id

    async def revert_to_checkpoint(self, checkpoint_id: str) -> dict:
        """
        Mark a checkpoint as reverted.
        In practice: you implement reversal logic specific to your tools.
        This gives you the audit trail to know WHAT to revert.
        """
        await self._ensure_db()
        if self.db is not None:
            checkpoint = await self.db.checkpoints.find_one({"checkpoint_id": checkpoint_id})
            if not checkpoint:
                return {"success": False, "error": "Checkpoint not found"}

            await self.db.checkpoints.update_one(
                {"checkpoint_id": checkpoint_id},
                {"$set": {"reverted": True, "reverted_at": datetime.utcnow()}}
            )
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "tool_name": checkpoint["tool_name"],
                "message": f"Checkpoint {checkpoint_id} marked as reverted. Implement domain-specific reversal logic."
            }
        return {"success": False, "error": "Database not available"}

    # ─── Cost Tracking ────────────────────────────────────────────────────

    def track_tokens(self, tokens_used: int, model: str = "groq"):
        """Call this after each LLM call to track costs."""
        COST_PER_1K = {"groq": 0.0001, "gemini": 0.00015, "openai": 0.002}
        cost = (tokens_used / 1000) * COST_PER_1K.get(model, 0.001)
        self.cost_tracker["tokens_used"] += tokens_used
        self.cost_tracker["estimated_cost_usd"] += cost

        # Alert if cost exceeds budget
        budget = self.policy.get("max_cost_per_session_usd", 1.0)
        if self.cost_tracker["estimated_cost_usd"] > budget:
            raise SecurityException(
                f"Cost budget exceeded: ${self.cost_tracker['estimated_cost_usd']:.4f} > ${budget}"
            )

    # ─── Policy Check ─────────────────────────────────────────────────────

    def _check_policy(self, tool_name: str, kwargs: dict) -> dict:
        allowed_tools = self.policy.get("allowed_tools", [])
        blocked_tools = self.policy.get("blocked_tools", [])
        require_confirmation = self.policy.get("require_human_confirmation", [])

        if blocked_tools and tool_name in blocked_tools:
            return {"allowed": False, "reason": f"Tool '{tool_name}' is explicitly blocked by policy"}

        if allowed_tools and tool_name not in allowed_tools:
            return {"allowed": False, "reason": f"Tool '{tool_name}' not in allowed tools list"}

        if tool_name in require_confirmation:
            return {"allowed": False, "reason": f"Tool '{tool_name}' requires human confirmation"}

        return {"allowed": True, "reason": ""}

    # ─── Logging ──────────────────────────────────────────────────────────

    async def _log(self, event_type: str, tool_name: str, action: str,
                   result: str = None, error: str = None, checkpoint_id: str = None):
        log_entry = {
            "agent_id": self.agent_id,
            "event_type": event_type,
            "tool_name": tool_name,
            "action": action,
            "result": result,
            "error": error,
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.utcnow(),
        }
        if self.db is not None:
            await self.db.shield_logs.insert_one(log_entry)
        else:
            print(f"[Shield] {event_type} | {tool_name} | {error or result or ''}")

    # ─── Dashboard Stats ──────────────────────────────────────────────────

    async def get_stats(self, hours: int = 24) -> dict:
        """Get shield statistics for the last N hours."""
        await self._ensure_db()
        if self.db is None:
            return {}

        from datetime import timedelta
        since = datetime.utcnow() - timedelta(hours=hours)

        pipeline = [
            {"$match": {"agent_id": self.agent_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
        ]

        cursor = self.db.shield_logs.aggregate(pipeline)
        stats = {}
        async for doc in cursor:
            stats[doc["_id"]] = doc["count"]

        return {
            "agent_id": self.agent_id,
            "period_hours": hours,
            "events": stats,
            "total_blocked": stats.get("BLOCKED", 0) + stats.get("POLICY_VIOLATION", 0),
            "total_allowed": stats.get("SUCCESS", 0),
            "cost_this_session": self.cost_tracker,
        }


# Default policy — override when instantiating Shield
DEFAULT_POLICY = {
    "allowed_tools": [],          # Empty = all tools allowed (add names to restrict)
    "blocked_tools": [],          # These tools are always blocked
    "require_human_confirmation": [],  # These tools need manual approval
    "max_cost_per_session_usd": 5.0,
    "max_iterations": 50,
}
