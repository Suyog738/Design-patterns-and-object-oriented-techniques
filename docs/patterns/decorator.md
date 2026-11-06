# Decorator Pattern 

## Purpose

Adds logging and a max-run-time safety check to actuator commands without changing
`SimulationActuatorAdapter` or putting policy `if`s in the router.

## Wrapping

All layers implement the same `ActuatorPort.apply(device_id, command, payload)`.
Each decorator holds an inner `ActuatorPort`, does its job, then calls it or refuses.

- **MaxRunTimeActuatorDecorator**: if the actuator is `running` and `updated_at` is
  ≥ 30 min old, it raises `ActuatorPolicyError` and does **not** call the inner port.
- **LoggingActuatorDecorator**: always writes a row to `actuator_execution_log`,
  on success or failure, then re-raises any error.

## Order

```text
LoggingActuatorDecorator → MaxRunTimeActuatorDecorator → SimulationActuatorAdapter
```

Built once in `build_actuator_port()` (`application/actuators/service.py`).

- Logging is outermost, so blocked attempts are logged too.
- Max run time comes before the adapter, so blocked commands never reach it.

| Case | success | policy_applied | message |
|---|---|---|---|
| Allowed | `true` | `["logging"]` | `null` |
| Blocked | `false` | `["maxRunTime", "logging"]` | `Max run time exceeded` |

## Decorator vs Inheritance

Inheritance needs a subclass per combination (`LoggingSimulationAdapter`,
`LoggingMaxRunTimeSimulationAdapter`, …), fixed at compile time.
Decorators are combined at runtime: adding, removing or reordering a policy only
changes `build_actuator_port()`, and each policy can be tested alone with a fake
inner port.