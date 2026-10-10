"""
Accenture GridOS™ - Enterprise LLM & Gemini Client
Handles environment variables (.env), Google Generative Language REST integration,
model selection, token streaming, and resilient offline fallbacks.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

def load_env_file(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Parses key-value pairs from .env into os.environ without requiring external packages.
    """
    if env_path is None:
        # Search in current directory, parent directory, and project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [
            os.path.join(base_dir, ".env"),
            os.path.join(os.getcwd(), ".env"),
            os.path.abspath(".env")
        ]
        for c in candidates:
            if os.path.exists(c):
                env_path = c
                break

    env_vars: Dict[str, str] = {}
    if env_path and os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        env_vars[k] = v
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            logger.warning(f"Failed to read .env file at {env_path}: {e}")
    return env_vars

# Load .env immediately on module import
_loaded_env = load_env_file()


class GeminiClient:
    """
    Client for Google Gemini REST API (v1beta).
    Fully independent of external SDKs, using Python standard library urllib.
    """

    DEFAULT_MODELS = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemma-4-26b-a4b-it",
        "gemini-pro"
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        load_env_file()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.is_configured = bool(self.api_key and len(self.api_key) > 10)

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        timeout: int = 8
    ) -> Dict[str, Any]:
        """
        Sends a prompt to the Gemini API and returns structured text response.
        If offline or quota exceeded, returns a fallback payload with error detail.
        """
        if not self.is_configured:
            return {
                "success": False,
                "text": "",
                "model_used": "none",
                "error": "GEMINI_API_KEY is not configured in .env"
            }

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Try designated model, followed by fallback cascade
        models_to_try = [self.model] + [m for m in self.DEFAULT_MODELS if m != self.model]

        last_error = ""
        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status == 200:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return {
                                    "success": True,
                                    "text": parts[0].get("text", "").strip(),
                                    "model_used": m,
                                    "usage": res_data.get("usageMetadata", {}),
                                    "error": None
                                }
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {e.code} ({m}): {err_body[:200]}"
                logger.debug(last_error)
            except Exception as e:
                last_error = f"Exception ({m}): {str(e)}"
                logger.debug(last_error)

        return {
            "success": False,
            "text": "",
            "model_used": "fallback",
            "error": last_error or "All candidate models failed"
        }

    def verify_connection(self) -> Dict[str, Any]:
        """
        Pings Google Gemini API to verify authentication and active quota.
        """
        if not self.is_configured:
            return {"connected": False, "message": "API Key not set in .env"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "connected": True,
                        "available_models_count": len(models),
                        "models": models[:5],
                        "message": f"Successfully authenticated with Google Gemini API ({len(models)} models accessible)"
                    }
        except urllib.error.HTTPError as e:
            return {"connected": False, "message": f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"}
        except Exception as e:
            return {"connected": False, "message": str(e)}

        return {"connected": False, "message": "Unknown error"}


# Global singleton instance
_gemini_singleton: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    global _gemini_singleton
    if _gemini_singleton is None:
        _gemini_singleton = GeminiClient()
    return _gemini_singleton

