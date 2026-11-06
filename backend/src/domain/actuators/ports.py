from abc import ABC, abstractmethod
from uuid import UUID


class ActuatorPort(ABC):
    @abstractmethod
    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        ...

class ActuatorPolicyError(Exception):
    """Raised by a policy decorator that refuses to call its inner port."""

    def __init__(self, policy: str, message: str):
        super().__init__(message)
        self.policy = policy