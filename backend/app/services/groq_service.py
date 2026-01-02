"""
Groq API Service
Handles proxying requests to Groq API
"""
import httpx
import logging
import time
from typing import Dict, Any, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Service for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = settings.GROQ_API_URL
        self.timeout = httpx.Timeout(30.0, connect=10.0)
    
    async def proxy_to_groq(self, request_body: dict) -> Tuple[dict, int, int]:
        """
        Proxy request to Groq API
        
        Args:
            request_body: Request body in Groq-compatible format
            
        Returns:
            tuple: (response_data, status_code, latency_ms)
            
        Raises:
            Exception: If Groq API request fails
        """
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=request_body,
                    headers=headers
                )
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Handle different status codes
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✓ Groq API success - {latency_ms}ms")
                    return data, 200, latency_ms
                
                elif response.status_code == 401:
                    logger.error("Groq API authentication failed")
                    raise GroqAPIError(
                        "Groq API authentication failed",
                        status_code=502,
                        groq_status=401
                    )
                
                elif response.status_code == 429:
                    logger.warning("Groq API rate limit exceeded")
                    raise GroqAPIError(
                        "Groq API rate limit exceeded",
                        status_code=429,
                        groq_status=429
                    )
                
                elif response.status_code >= 500:
                    logger.error(f"Groq API server error: {response.status_code}")
                    raise GroqAPIError(
                        "Groq API server error",
                        status_code=502,
                        groq_status=response.status_code
                    )
                
                else:
                    error_detail = response.text
                    logger.error(f"Groq API error {response.status_code}: {error_detail}")
                    raise GroqAPIError(
                        f"Groq API error: {error_detail}",
                        status_code=502,
                        groq_status=response.status_code
                    )
        
        except httpx.TimeoutException:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Groq API timeout after {latency_ms}ms")
            raise GroqAPIError(
                "Groq API request timeout",
                status_code=504,
                groq_status=None
            )
        
        except httpx.ConnectError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("Failed to connect to Groq API")
            raise GroqAPIError(
                "Failed to connect to Groq API",
                status_code=502,
                groq_status=None
            )
        
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Unexpected error calling Groq API: {str(e)}")
            raise GroqAPIError(
                f"Groq API request failed: {str(e)}",
                status_code=502,
                groq_status=None
            )
    
    async def check_health(self) -> bool:
        """
        Check if Groq API is reachable
        
        Returns:
            bool: True if Groq API is healthy
        """
        try:
            # Simple health check - try to make a minimal request
            test_request = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            _, status_code, _ = await self.proxy_to_groq(test_request)
            return status_code == 200
        
        except Exception as e:
            logger.warning(f"Groq API health check failed: {str(e)}")
            return False


class GroqAPIError(Exception):
    """Custom exception for Groq API errors"""
    
    def __init__(self, message: str, status_code: int, groq_status: int = None):
        self.message = message
        self.status_code = status_code
        self.groq_status = groq_status
        super().__init__(self.message)


# Global instance
groq_service = GroqService()
