"""
AgentSec Client — Drop this file into any project to use Shield from your agent.
Usage:
    from agentsec_client import AgentShieldClient
    shield = AgentShieldClient(agent_id="my-agent", api_url="http://localhost:8000")
    result = shield.check_outbound(response_text)
"""
import httpx


class AgentShieldClient:
    def __init__(self, agent_id: str, api_url: str = "http://localhost:8000"):
        self.agent_id = agent_id
        self.api_url = api_url.rstrip("/")

    def check_outbound(self, response_text: str) -> dict:
        """Check if agent response is safe before sending to user."""
        try:
            r = httpx.post(
                f"{self.api_url}/shield/check-outbound",
                json={"agent_id": self.agent_id, "response_text": response_text},
                timeout=15.0
            )
            return r.json()
        except Exception as e:
            # Fail open (allow) if Shield is unreachable
            return {"safe": True, "response": response_text, "action": "ALLOW", "error": str(e)}

    def get_logs(self, hours: int = 24) -> list:
        try:
            r = httpx.get(f"{self.api_url}/shield/logs/{self.agent_id}?hours={hours}", timeout=10.0)
            return r.json().get("logs", [])
        except Exception:
            return []

    def get_checkpoints(self) -> list:
        try:
            r = httpx.get(f"{self.api_url}/shield/checkpoints/{self.agent_id}", timeout=10.0)
            return r.json().get("checkpoints", [])
        except Exception:
            return []

    def revert(self, checkpoint_id: str) -> dict:
        try:
            r = httpx.post(
                f"{self.api_url}/shield/revert",
                json={"agent_id": self.agent_id, "checkpoint_id": checkpoint_id},
                timeout=10.0
            )
            return r.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
