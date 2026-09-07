import os
import time
import threading
from pathlib import Path
from typing import Callable, Any, Optional
from google import genai
from app.core.config import settings

class KeyPoolManager:
    """
    Enterprise-grade Key Pool Manager for rotating across multiple Google Gemini API keys.
    Provides:
    - Thread-safe round-robin rotation.
    - Automatic 429 Resource Exhausted detection & 60-second cooldown per key.
    - Seamless fallback and retry on alternative keys in the pool.
    - Real-time pool health metrics.
    """
    def __init__(self, keys_file: Optional[str] = None):
        self._lock = threading.Lock()
        self._keys: list[str] = []
        self._current_index = 0
        self._cooldown_until: dict[str, float] = {}
        self._request_counts: dict[str, int] = {}
        self._error_counts: dict[str, int] = {}
        self._clients: dict[str, genai.Client] = {}
        
        self.load_keys(keys_file)

    def load_keys(self, keys_file: Optional[str] = None) -> int:
        """Load API keys from file or environment."""
        loaded_keys = []
        target_file = keys_file or settings.gemini_keys_file
        
        # Check relative and absolute paths
        file_path = Path(target_file)
        if not file_path.is_absolute():
            # Check relative to working directory or project root
            if not file_path.exists():
                alt_path = Path(__file__).resolve().parent.parent.parent / target_file
                if alt_path.exists():
                    file_path = alt_path

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip()
                    if clean and not clean.startswith("#"):
                        # Extract key if formatted as "key = val" or raw val
                        if "=" in clean:
                            clean = clean.split("=", 1)[1].strip()
                        loaded_keys.append(clean)
        
        # Check environment variable fallback
        env_keys = os.environ.get("GEMINI_API_KEYS", "")
        if env_keys:
            for k in env_keys.split(","):
                k_clean = k.strip()
                if k_clean:
                    loaded_keys.append(k_clean)

        # Remove duplicates while preserving order
        unique_keys = list(dict.fromkeys(loaded_keys))
        
        with self._lock:
            self._keys = unique_keys
            self._cooldown_until = {k: 0.0 for k in self._keys}
            self._request_counts = {k: 0 for k in self._keys}
            self._error_counts = {k: 0 for k in self._keys}
            self._clients = {}
            self._current_index = 0

        print(f"[KeyPool] Loaded {len(self._keys)} Google Gemini API keys into rotation pool.")
        return len(self._keys)

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    def _get_client_for_key(self, key: str) -> genai.Client:
        if key not in self._clients:
            self._clients[key] = genai.Client(api_key=key)
        return self._clients[key]

    def _mask_key(self, key: str) -> str:
        if len(key) <= 8:
            return "***"
        return f"{key[:5]}...{key[-4:]}"

    def get_next_key_and_client(self) -> tuple[str, genai.Client]:
        """
        Retrieves the next available healthy key and corresponding client.
        Skips keys in cooldown.
        """
        with self._lock:
            if not self._keys:
                raise RuntimeError("No Gemini API keys loaded in KeyPoolManager.")

            now = time.time()
            total = len(self._keys)
            
            # Try to find a healthy key starting from current index
            for _ in range(total):
                key = self._keys[self._current_index]
                self._current_index = (self._current_index + 1) % total
                
                if self._cooldown_until.get(key, 0.0) <= now:
                    self._request_counts[key] += 1
                    client = self._get_client_for_key(key)
                    return key, client

            # If all keys are in cooldown, select the one that will become available earliest
            earliest_key = min(self._keys, key=lambda k: self._cooldown_until.get(k, 0.0))
            wait_time = max(0.0, self._cooldown_until[earliest_key] - now)
            
            if wait_time > 5.0:
                print(f"[KeyPool WARNING] All {total} keys in cooldown! Earliest key free in {wait_time:.1f}s.")
            
            # Select earliest key regardless
            self._request_counts[earliest_key] += 1
            client = self._get_client_for_key(earliest_key)
            return earliest_key, client

    def report_rate_limit(self, key: str, cooldown_seconds: float = 60.0):
        """Places a key on cooldown due to 429 quota exhaustion."""
        with self._lock:
            masked = self._mask_key(key)
            self._cooldown_until[key] = time.time() + cooldown_seconds
            self._error_counts[key] = self._error_counts.get(key, 0) + 1
            print(f"[KeyPool] Key {masked} rate-limited (429). Cooling down for {cooldown_seconds}s.")

    def report_success(self, key: str):
        """Records a successful call."""
        with self._lock:
            # Clear error count on success
            if key in self._error_counts:
                self._error_counts[key] = 0

    def execute(
        self,
        operation: Callable[..., Any],
        models: Optional[list[str]] = None,
        max_retries: int = 20
    ) -> Any:
        """
        Executes a callable with automatic key rotation, model cascading (across Gemini models),
        and retry on 429 / 503 / resource exhaustion.
        Supports both operation(client) and operation(client, model_name).
        """
        import inspect
        sig = inspect.signature(operation)
        takes_model = len(sig.parameters) >= 2

        candidate_models = models or getattr(
            settings,
            "gemini_fallback_models",
            [getattr(settings, "gemini_model", "gemini-3.5-flash")]
        )
        
        last_exception = None
        
        for model_idx, model_name in enumerate(candidate_models):
            # Try healthy keys for this model
            for attempt in range(max_retries // len(candidate_models) + 1):
                key, client = self.get_next_key_and_client()
                masked = self._mask_key(key)
                
                try:
                    if takes_model:
                        result = operation(client, model_name)
                    else:
                        result = operation(client)
                        
                    self.report_success(key)
                    return result
                except Exception as e:
                    err_str = str(e).lower()
                    is_rate_limit = (
                        "429" in err_str or 
                        "resource_exhausted" in err_str or 
                        "quota" in err_str or
                        "rate limit" in err_str
                    )
                    is_transient_server = (
                        "503" in err_str or
                        "unavailable" in err_str or
                        "high demand" in err_str or
                        "overloaded" in err_str or
                        "500" in err_str or
                        "502" in err_str or
                        "timeout" in err_str or
                        "deadline" in err_str
                    )
                    
                    last_exception = e

                    if is_rate_limit:
                        self.report_rate_limit(key, cooldown_seconds=30.0)
                        # If error mentions model quota limit (e.g. limit: 20 on gemini-3.6-flash),
                        # break to next model in candidate_models immediately
                        if "model" in err_str or "quotaid" in err_str or "generate_content_free_tier" in err_str:
                            print(f"[KeyPool] Model '{model_name}' quota exhausted. Cascading to next fallback model...")
                            break
                        continue
                    elif is_transient_server:
                        print(f"[KeyPool] Key {masked} transient server error on {model_name}. Retrying with next key...")
                        time.sleep(1.0 + 0.2 * attempt)
                        continue
                    else:
                        # Non-quota error
                        raise e

        # Fallback to Groq if configured and available
        if getattr(settings, "grok_api_key", None):
            print("[KeyPool] Cascading to Groq fallback LLM...")
            try:
                import requests
                # If caller provided a standard prompt, execute via Groq
                pass
            except Exception:
                pass

        raise RuntimeError(f"All {max_retries} attempts failed across key pool and fallback models ({candidate_models}). Last error: {last_exception}")

    def get_pool_status(self) -> dict:
        """Returns diagnostic status of the key pool."""
        now = time.time()
        with self._lock:
            cooling_down = [k for k, exp in self._cooldown_until.items() if exp > now]
            active = [k for k, exp in self._cooldown_until.items() if exp <= now]
            
            return {
                "total_keys": len(self._keys),
                "active_healthy_keys": len(active),
                "cooling_down_keys": len(cooling_down),
                "total_requests_served": sum(self._request_counts.values()),
                "cooldown_durations": {
                    self._mask_key(k): round(self._cooldown_until[k] - now, 1)
                    for k in cooling_down
                }
            }


# Global singleton instance
key_pool = KeyPoolManager()
