
# State Pattern — Actuators

## Purpose

The State pattern manages the current operating state of each actuator. It controls which state transitions are allowed and prevents invalid changes.

## Actuator states

The system supports five states:

- **off** — The actuator is switched off.
- **idle** — The actuator is available but not running.
- **running** — The actuator is operating.
- **error** — The actuator has encountered an error.
- **maintenance** — The actuator is under maintenance.

## State transitions

Each state has a defined set of allowed next states. For example:

- An idle actuator can start running, turn off, enter maintenance, or enter an error state.
- A running actuator can return to idle or enter an error state.
- A running actuator cannot move directly to maintenance.

The ActuatorContext checks every requested transition. If a transition is not allowed, it raises IllegalTransitionError and keeps the current state unchanged.

## Allowed commands

The system also provides commands based on the current state.

| State | Allowed commands |
|---|---|
| off | turn_on |
| idle | start_pump, turn_off, enter_maintenance |
| running | stop_pump |
| error | reset, enter_maintenance |
| maintenance | exit_maintenance |

The overview API returns the actuator state and its allowed commands. The frontend displays the state using a colored badge, with the available commands shown in the badge tooltip.

## Persistence

Actuator states are stored in the actuator_states database table. Each actuator has one state record, identified by its device ID. Existing actuators are initialized with the idle state.

## Benefits

- Prevents invalid actuator state changes.
- Keeps transition rules in one place.
- Makes the available commands clear for each state.
- Separates state-related behavior from the API and frontend.
