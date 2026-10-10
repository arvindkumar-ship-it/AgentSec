"""
AgentSec Client — Drop this file into any project to use Shield from your agent.
Usage:
    from agentsec_client import AgentShieldClient
    shield = AgentShieldClient(agent_id="my-agent", api_url="http://localhost:8000")
    result = shield.check_outbound(response_text)
"""
import httpx


class AgentShieldClient:
    def __init__(self, agent_id: str, api_url: str = "http://localhost:8000", access_token: str | None = None):
        self.agent_id = agent_id
        self.api_url = api_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    def _request(self, method: str, path: str, **kwargs):
        response = httpx.request(method, f"{self.api_url}{path}", headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def check_outbound(self, response_text: str) -> dict:
        """Check if agent response is safe before sending to user."""
        try:
            result = self._request("POST", "/shield/check-outbound",
                json={"agent_id": self.agent_id, "response_text": response_text},
                timeout=15.0
            )
            if (not isinstance(result, dict) or type(result.get("safe")) is not bool
                    or result.get("action") not in {"ALLOW", "WARN", "BLOCK"}
                    or result["safe"] != (result["action"] != "BLOCK")):
                raise ValueError("Invalid Shield decision")
            return result
        except Exception as e:
            return {"safe": False, "response": "Response withheld: Shield verification unavailable.",
                    "action": "BLOCK", "error": type(e).__name__}

    def get_logs(self, hours: int = 24) -> list:
        try:
            return self._request("GET", f"/shield/logs/{self.agent_id}", params={"hours": hours}, timeout=10.0).get("logs", [])
        except Exception:
            return []

    def get_checkpoints(self) -> list:
        try:
            return self._request("GET", f"/shield/checkpoints/{self.agent_id}", timeout=10.0).get("checkpoints", [])
        except Exception:
            return []

    def revert(self, checkpoint_id: str) -> dict:
        try:
            return self._request("POST", "/shield/revert",
                json={"agent_id": self.agent_id, "checkpoint_id": checkpoint_id},
                timeout=10.0
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
