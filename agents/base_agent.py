from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_type: str, ai_router_url: str):
        self.agent_type = agent_type
        self.ai_router_url = ai_router_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic"""
        pass
    
    async def chat(self, messages: List[Dict[str, str]], model: str = None, provider: str = None) -> str:
        """Send chat request to AI router"""
        try:
            response = await self.client.post(
                f"{self.ai_router_url}/api/chat",
                json={
                    "messages": messages,
                    "model": model,
                    "provider": provider,
                    "temperature": 0.7,
                    "maxTokens": 4096,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", "")
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    async def analyze_with_ai(self, prompt: str, context: Dict[str, Any]) -> str:
        """Analyze data using AI"""
        messages = [
            {
                "role": "system",
                "content": f"You are a {self.agent_type} agent specialized in cybersecurity intelligence analysis."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nContext: {context}"
            }
        ]
        return await self.chat(messages)
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent action"""
        logger.info(f"[{self.agent_type}] {action}", extra=details)
    
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()
