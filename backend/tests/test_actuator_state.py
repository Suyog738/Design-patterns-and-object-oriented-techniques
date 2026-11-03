import pytest

from domain.actuators.context import ActuatorContext
from domain.actuators.state import ActuatorState, IllegalTransitionError


def test_idle_to_running_allowed():
    context = ActuatorContext(ActuatorState.IDLE)
    context.transition("running")
    assert context.state == ActuatorState.RUNNING
    assert context.allowed_commands() == ["stop_pump"]


def test_running_to_maintenance_rejected():
    context = ActuatorContext(ActuatorState.RUNNING)
    with pytest.raises(IllegalTransitionError):
        context.transition("maintenance")
    assert context.state == ActuatorState.RUNNING


def test_command_names_are_accepted():
    context = ActuatorContext(ActuatorState.IDLE)
    context.transition("start_pump")
    assert context.state == ActuatorState.RUNNING
