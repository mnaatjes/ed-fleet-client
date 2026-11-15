"""Type-safe observer and event dispatch engine for hydrated telemetry domain events."""

from __future__ import annotations

import asyncio
import inspect
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

from .models import (
    DispatchResult,
    EventHandler,
    HandlerFailure,
    Subscription,
    TelemetryEvent,
)

E = TypeVar("E", bound=TelemetryEvent)


class TelemetryEventDispatcher:
    """Type-safe observer and dispatch registry for hydrated Elite Dangerous events.

    Provides decorator and programmatic subscription mechanisms supporting:
    - Exact class and polymorphic subclass matching
    - Synchronous and asynchronous handler execution
    - Complete error isolation preventing user handler crashes from affecting dispatch
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # Mapping: Event Type -> List of (Subscription, EventHandler)
        self._registry: dict[type[Any], list[tuple[Subscription, EventHandler]]] = defaultdict(list)
        # Quick lookup: Subscription ID -> (Event Type, Subscription, EventHandler)
        self._subscriptions: dict[str, tuple[type[Any], Subscription, EventHandler]] = {}

    @property
    def subscription_count(self) -> int:
        """Total number of active subscriptions across all event types."""
        with self._lock:
            return len(self._subscriptions)

    def on(self, event_type: type[E]) -> Callable[[EventHandler], EventHandler]:
        """Decorator registering a handler callback for the specified domain event type."""

        def decorator(handler: EventHandler) -> EventHandler:
            self.subscribe(event_type, handler)
            return handler

        return decorator

    def subscribe(self, event_type: type[E], handler: EventHandler) -> Subscription:
        """Programmatically registers an event handler for a specific event type."""
        is_async = inspect.iscoroutinefunction(handler)
        sub = Subscription(event_type=event_type, is_async=is_async)

        with self._lock:
            self._registry[event_type].append((sub, handler))
            self._subscriptions[sub.subscription_id] = (event_type, sub, handler)

        return sub

    def unsubscribe(self, subscription: Subscription | str) -> bool:
        """Detaches a subscription by its token or ID. Returns True if removed."""
        sub_id = (
            subscription.subscription_id if isinstance(subscription, Subscription) else subscription
        )

        with self._lock:
            if sub_id not in self._subscriptions:
                return False

            ev_type, sub_token, handler = self._subscriptions.pop(sub_id)
            if ev_type in self._registry:
                self._registry[ev_type] = [
                    (s, h) for (s, h) in self._registry[ev_type] if s.subscription_id != sub_id
                ]
                if not self._registry[ev_type]:
                    del self._registry[ev_type]

            return True

    def clear(self) -> None:
        """Removes all active subscriptions."""
        with self._lock:
            self._registry.clear()
            self._subscriptions.clear()

    def _find_matching_handlers(
        self, event: TelemetryEvent
    ) -> list[tuple[Subscription, EventHandler]]:
        """Finds all registered handlers matching the event type or its superclasses."""
        matched: list[tuple[Subscription, EventHandler]] = []
        with self._lock:
            for sub_type, handlers in self._registry.items():
                if isinstance(event, sub_type):
                    matched.extend(handlers)
        return matched

    def dispatch(self, event: TelemetryEvent) -> DispatchResult:
        """Synchronously dispatches an event to all matching handlers.

        Async coroutine handlers are executed in an event loop if available or via asyncio.run.
        All exceptions are caught and recorded in DispatchResult.failures.
        """
        event_name = (
            getattr(event, "event", event.__class__.__name__)
            if hasattr(event, "event")
            else event.__class__.__name__
        )

        matched = self._find_matching_handlers(event)
        executed = 0
        failures: list[HandlerFailure] = []

        for sub, handler in matched:
            handler_name = getattr(handler, "__name__", str(handler))
            try:
                if sub.is_async:
                    # Async handler execution: schedule on active running loop
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(event))  # type: ignore[arg-type]
                    except RuntimeError as err:
                        raise RuntimeError(
                            f"Cannot execute async handler {handler_name} via dispatch() "
                            "without a running event loop. Use dispatch_async() instead."
                        ) from err
                else:
                    # Sync handler execution
                    handler(event)
                executed += 1
            except Exception as err:
                failures.append(
                    HandlerFailure(
                        subscription_id=sub.subscription_id,
                        event_type=event_name,
                        handler_name=handler_name,
                        error_type=type(err).__name__,
                        error_message=str(err),
                    )
                )

        return DispatchResult(
            event_name=event_name,
            total_matched=len(matched),
            executed_count=executed,
            failures=failures,
        )

    async def dispatch_async(self, event: TelemetryEvent) -> DispatchResult:
        """Asynchronously dispatches an event to all matching handlers concurrently."""
        event_name = (
            getattr(event, "event", event.__class__.__name__)
            if hasattr(event, "event")
            else event.__class__.__name__
        )

        matched = self._find_matching_handlers(event)
        executed = 0
        failures: list[HandlerFailure] = []

        for sub, handler in matched:
            handler_name = getattr(handler, "__name__", str(handler))
            try:
                if sub.is_async:
                    await handler(event)  # type: ignore[misc]
                else:
                    handler(event)
                executed += 1
            except Exception as err:
                failures.append(
                    HandlerFailure(
                        subscription_id=sub.subscription_id,
                        event_type=event_name,
                        handler_name=handler_name,
                        error_type=type(err).__name__,
                        error_message=str(err),
                    )
                )

        return DispatchResult(
            event_name=event_name,
            total_matched=len(matched),
            executed_count=executed,
            failures=failures,
        )
