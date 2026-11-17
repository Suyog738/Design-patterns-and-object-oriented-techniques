# Command Pattern

## Purpose

Each actuator action ("start pump", "set light level") is wrapped in an object.
The object can be checked, run, and saved to `command_log`, so every request has
a record, even when it is refused.

## Classes

| Class | Role |
|---|---|
| `StartPumpCommand` | `start_pump` → state becomes `running` |
| `StopPumpCommand` | `stop_pump` → state becomes `idle` |
| `SetLightLevelCommand` | `set_light_level` with `{ "level": 0–1 }` → `running` |
| `CommandInvoker` | Calls `command.execute(port)` |
| `CommandService` | Checks state, runs the command, updates state, writes the log |

`command_for()` finds the class in `COMMAND_REGISTRY` by name, with no `if`
chain. To add a new command, write one class and add it to the registry.

## Flow

```text
POST /api/commands
  → command_for()            unknown type → 400, no log row
  → check allowed_commands   not allowed  → "rejected", 409
  → CommandInvoker.run()     → Logging → MaxRunTime → Simulation adapter
  → update actuator_states   only if the state changes
  → save "success" or "failed"
```

## Object vs function

A function like `start_pump()` just runs. A command object also carries its
name, device, payload and target state, so we can check it before running it
and save it afterwards.

## Audit

| Status | Meaning | Example |
|---|---|---|
| `success` | Allowed and ran | `start_pump` on an idle pump |
| `rejected` | Not allowed in this state, never ran | `start_pump` on a running pump |
| `failed` | Allowed, but blocked while running | `stop_pump` → "Max run time exceeded" |

- `command_log` stores what the user asked for.
- `actuator_execution_log` (Phase 9) stores what reached the actuator.
- A rejected command only appears in `command_log`.

`GET /api/commands?limit=50` shows the history, newest first.