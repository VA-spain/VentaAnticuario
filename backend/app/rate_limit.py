"""Freno de intentos de inicio de sesión, en la memoria del proceso.

Vale mientras el backend corra en un solo proceso: los contadores no se comparten entre
procesos y se pierden al reiniciar.
"""

import math
import threading
import time
from collections import deque
from collections.abc import Callable


class FailureWindow:
    """Cuenta fallos por clave en una ventana deslizante."""

    def __init__(
        self,
        *,
        max_failures: int,
        window_seconds: float,
        max_keys: int = 50_000,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_failures = max_failures
        self._window = window_seconds
        self._max_keys = max_keys
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def retry_after(self, key: str) -> int:
        """Segundos que faltan para admitir otro intento; 0 si se admite ya."""
        with self._lock:
            recent = self._recent(key)
            if recent is None or len(recent) < self._max_failures:
                return 0
            # Se admite otro intento cuando el fallo más antiguo sale de la ventana.
            return max(1, math.ceil(recent[0] + self._window - self._clock()))

    def add_failure(self, key: str) -> None:
        with self._lock:
            recent = self._recent(key)
            if recent is None:
                if len(self._failures) >= self._max_keys:
                    self._evict()
                recent = self._failures[key] = deque(maxlen=self._max_failures)
            recent.append(self._clock())

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def _recent(self, key: str) -> deque[float] | None:
        """Fallos de la clave que siguen dentro de la ventana, o None si no queda ninguno."""
        recent = self._failures.get(key)
        if recent is None:
            return None
        limit = self._clock() - self._window
        while recent and recent[0] <= limit:
            recent.popleft()
        if not recent:
            del self._failures[key]
            return None
        return recent

    def _evict(self) -> None:
        """Libera memoria cuando hay demasiadas claves (las claves las elige quien ataca)."""
        limit = self._clock() - self._window
        for key in [k for k, hits in self._failures.items() if hits[-1] <= limit]:
            del self._failures[key]
        if len(self._failures) >= self._max_keys:
            # Todas siguen vivas: se prefiere olvidar los contadores a crecer sin límite.
            self._failures.clear()


class LoginThrottle:
    """Dos frenos a la vez sobre los intentos fallidos de inicio de sesión.

    - Por cuenta y dirección IP: pocos fallos seguidos. Frena a quien prueba contraseñas sin
      dejar fuera al dueño de la cuenta, que entra desde otra dirección.
    - Por cuenta, desde cualquier dirección: un tope más alto, por si quien ataca va cambiando
      de dirección.
    """

    def __init__(
        self,
        *,
        per_client: FailureWindow | None = None,
        per_account: FailureWindow | None = None,
    ) -> None:
        self._per_client = per_client or FailureWindow(max_failures=5, window_seconds=15 * 60)
        self._per_account = per_account or FailureWindow(max_failures=20, window_seconds=15 * 60)

    def retry_after(self, username: str, client_ip: str) -> int:
        return max(
            self._per_client.retry_after(self._client_key(username, client_ip)),
            self._per_account.retry_after(username),
        )

    def register_failure(self, username: str, client_ip: str) -> None:
        self._per_client.add_failure(self._client_key(username, client_ip))
        self._per_account.add_failure(username)

    def register_success(self, username: str, client_ip: str) -> None:
        self._per_client.reset(self._client_key(username, client_ip))

    @staticmethod
    def _client_key(username: str, client_ip: str) -> str:
        return f"{client_ip}|{username}"


_login_throttle = LoginThrottle()


def get_login_throttle() -> LoginThrottle:
    return _login_throttle
