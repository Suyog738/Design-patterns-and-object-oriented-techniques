from uuid import uuid4

from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import (
    AggressiveMoistureStrategy,
    ConservativeMoistureStrategy,
    get_strategy,
)


def make_context() -> LocationAutomationContext:
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=0.40,
        light=500,
        moisture_low=0.25,
        moisture_high=0.45,
    )


def test_conservative_waits_when_within_band():
    context = make_context()

    recommendation = ConservativeMoistureStrategy().decide(context)

    assert recommendation.action == "wait"


def test_aggressive_differs_on_same_context():
    context = make_context()

    conservative = ConservativeMoistureStrategy().decide(context)
    aggressive = AggressiveMoistureStrategy().decide(context)

    assert conservative.action != aggressive.action
    assert conservative.action == "wait"
    assert aggressive.action == "irrigate"


def test_get_strategy_returns_correct_strategy():
    assert get_strategy("conservative").key == "conservative"
    assert get_strategy("aggressive").key == "aggressive"


def test_get_strategy_rejects_unknown_key():
    try:
        get_strategy("unknown")
        assert False
    except ValueError:
        assert True