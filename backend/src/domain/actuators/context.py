from domain.actuators.state import (
    ActuatorState,
    ALLOWED_TRANSITIONS,
    COMMAND_TARGETS,
    IllegalTransitionError,
    get_allowed_commands,
)


class ActuatorContext:
    def __init__(self, state: ActuatorState):
        self._state = ActuatorState(state)

    @property
    def state(self) -> ActuatorState:
        return self._state

    def transition(self, target: str) -> None:
        if target in COMMAND_TARGETS:
            if target not in get_allowed_commands(self._state):
                raise IllegalTransitionError(
                    f"Command {target} is not allowed "
                    f"in state {self._state.value}."
                )
            target_state = COMMAND_TARGETS[target]
        else:
            try:
                target_state = ActuatorState(target)
            except ValueError as error:
                raise IllegalTransitionError(
                    f"Unknown actuator state or command: {target}"
                ) from error

        allowed = ALLOWED_TRANSITIONS[self._state]

        if target_state not in allowed:
            raise IllegalTransitionError(
                f"Cannot transition from "
                f"{self._state.value} to {target_state.value}."
            )

        self._state = target_state

    def allowed_commands(self) -> list[str]:
        return get_allowed_commands(self._state)
