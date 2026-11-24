import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any


logger = logging.getLogger(__name__)

Handler = Callable[[Any], None]


class EventBus:
    """In-process subject: publishers call publish(), subscribers get called."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            try:
                handler(event)
            except Exception:
                # A broken subscriber must not break the publisher's request.
                logger.exception(
                    "Subscriber %r failed for %s",
                    handler,
                    type(event).__name__,
                )
