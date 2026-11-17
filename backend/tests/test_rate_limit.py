from app.rate_limit import FailureWindow, LoginThrottle


class FakeClock:
    def __init__(self) -> None:
        self.now = 1_000.0

    def __call__(self) -> float:
        return self.now


def test_blocks_after_max_failures_and_reports_the_wait() -> None:
    clock = FakeClock()
    window = FailureWindow(max_failures=3, window_seconds=60, clock=clock)

    for _ in range(2):
        window.add_failure("k")
    assert window.retry_after("k") == 0

    window.add_failure("k")
    assert window.retry_after("k") == 60

    clock.now += 20
    assert window.retry_after("k") == 40


def test_window_slides_one_attempt_at_a_time() -> None:
    clock = FakeClock()
    window = FailureWindow(max_failures=2, window_seconds=60, clock=clock)

    window.add_failure("k")
    clock.now += 30
    window.add_failure("k")
    assert window.retry_after("k") == 30

    # Sale de la ventana el primer fallo: se admite un intento, pero el segundo sigue contando.
    clock.now += 30
    assert window.retry_after("k") == 0
    window.add_failure("k")
    assert window.retry_after("k") == 30


def test_keys_are_independent_and_reset_forgets_one() -> None:
    window = FailureWindow(max_failures=1, window_seconds=60, clock=FakeClock())

    window.add_failure("a")
    assert window.retry_after("a") > 0
    assert window.retry_after("b") == 0

    window.reset("a")
    assert window.retry_after("a") == 0


def test_memory_stays_bounded_when_keys_keep_coming() -> None:
    clock = FakeClock()
    window = FailureWindow(max_failures=1, window_seconds=60, max_keys=3, clock=clock)

    for key in ("a", "b", "c"):
        window.add_failure(key)
    clock.now += 61
    window.add_failure("d")  # las tres primeras ya caducaron: se liberan
    assert len(window._failures) == 1

    for key in ("e", "f", "g"):
        window.add_failure(key)  # todas vivas y sin sitio: se olvidan los contadores
    assert len(window._failures) <= 3


def test_login_throttle_separates_addresses_but_caps_the_account() -> None:
    clock = FakeClock()
    throttle = LoginThrottle(
        per_client=FailureWindow(max_failures=2, window_seconds=60, clock=clock),
        per_account=FailureWindow(max_failures=3, window_seconds=60, clock=clock),
    )

    throttle.register_failure("ana@example.com", "10.0.0.1")
    throttle.register_failure("ana@example.com", "10.0.0.1")
    assert throttle.retry_after("ana@example.com", "10.0.0.1") > 0
    # Otra dirección no queda bloqueada por los fallos de la primera…
    assert throttle.retry_after("ana@example.com", "10.0.0.2") == 0
    # …ni otra cuenta desde la misma dirección.
    assert throttle.retry_after("luis@example.com", "10.0.0.1") == 0

    # Pero la cuenta tiene un tope global, venga de donde venga el intento.
    throttle.register_failure("ana@example.com", "10.0.0.2")
    assert throttle.retry_after("ana@example.com", "10.0.0.3") > 0


def test_login_throttle_success_clears_the_address_counter() -> None:
    throttle = LoginThrottle(
        per_client=FailureWindow(max_failures=2, window_seconds=60, clock=FakeClock()),
    )

    throttle.register_failure("ana@example.com", "10.0.0.1")
    throttle.register_success("ana@example.com", "10.0.0.1")
    throttle.register_failure("ana@example.com", "10.0.0.1")

    assert throttle.retry_after("ana@example.com", "10.0.0.1") == 0
