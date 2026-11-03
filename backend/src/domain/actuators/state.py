from enum import Enum


class ActuatorState(str, Enum):
    OFF = "off"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class IllegalTransitionError(Exception):
    """Raised when an actuator transition is not allowed."""


ALLOWED_TRANSITIONS: dict[ActuatorState, set[ActuatorState]] = {
    ActuatorState.OFF: {
        ActuatorState.IDLE,
        ActuatorState.ERROR,
    },
    ActuatorState.IDLE: {
        ActuatorState.RUNNING,
        ActuatorState.MAINTENANCE,
        ActuatorState.ERROR,
        ActuatorState.OFF,
    },
    ActuatorState.RUNNING: {
        ActuatorState.IDLE,
        ActuatorState.ERROR,
    },
    ActuatorState.ERROR: {
        ActuatorState.IDLE,
        ActuatorState.MAINTENANCE,
        ActuatorState.OFF,
    },
    ActuatorState.MAINTENANCE: {
        ActuatorState.IDLE,
        ActuatorState.OFF,
        ActuatorState.ERROR,
    },
}


ALLOWED_COMMANDS: dict[ActuatorState, list[str]] = {
    ActuatorState.OFF: ["turn_on"],
    ActuatorState.IDLE: ["start_pump", "turn_off", "enter_maintenance"],
    ActuatorState.RUNNING: ["stop_pump"],
    ActuatorState.ERROR: ["reset", "enter_maintenance"],
    ActuatorState.MAINTENANCE: ["exit_maintenance"],
}


COMMAND_TARGETS: dict[str, ActuatorState] = {
    "turn_on": ActuatorState.IDLE,
    "turn_off": ActuatorState.OFF,
    "start_pump": ActuatorState.RUNNING,
    "stop_pump": ActuatorState.IDLE,
    "enter_maintenance": ActuatorState.MAINTENANCE,
    "exit_maintenance": ActuatorState.IDLE,
    "reset": ActuatorState.IDLE,
}


def get_allowed_commands(state: ActuatorState) -> list[str]:
    return ALLOWED_COMMANDS[state].copy()
