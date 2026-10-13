from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.automation.context import LocationAutomationContext


@dataclass(frozen=True)
class Recommendation:
    action: str
    reason: str
    score: float | None = None


class AutomationStrategy(ABC):
    key: str

    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        ...


class ConservativeMoistureStrategy(AutomationStrategy):
    key = "conservative"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture reading is available",
            )

        if context.moisture < context.moisture_low:
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.2f} is below "
                    f"{context.moisture_low:.2f}"
                ),
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.2f} is within "
                f"{context.moisture_low:.2f}–{context.moisture_high:.2f}"
            ),
        )


class AggressiveMoistureStrategy(AutomationStrategy):
    key = "aggressive"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture reading is available",
            )

        if context.moisture < context.moisture_high:
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.2f} is below "
                    f"{context.moisture_high:.2f}"
                ),
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.2f} is at or above "
                f"{context.moisture_high:.2f}"
            ),
        )


def get_strategy(key: str) -> AutomationStrategy:
    if key == "conservative":
        return ConservativeMoistureStrategy()

    if key == "aggressive":
        return AggressiveMoistureStrategy()

    raise ValueError(f"Unknown strategy: {key}")